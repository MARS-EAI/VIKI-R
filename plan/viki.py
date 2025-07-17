import json
import os
import base64
from openai import OpenAI
import time
from tqdm import tqdm
import concurrent.futures
import threading
import hashlib
from functools import lru_cache
import backoff
import argparse
from utils.reward_score import viki_2
import re
import pandas as pd
import ast
import tempfile
import numpy as np
from dotenv import load_dotenv
from prompt import ROBOT_DESCRIPTION, AGENT_AVAIL_ACTIONS, AGENT_END_EFFECTOR_NUM, SYSTEM_INSTRUCTION, get_user_message_template

# Load environment variables from .env file
load_dotenv()

# Image cache lock to prevent multi-thread write conflicts
cache_lock = threading.Lock()
# Image cache dictionary
image_cache = {}

client = OpenAI()

def load_data(file_path):
    if file_path.endswith('.parquet'):
        df = pd.read_parquet(file_path)
        return df.to_dict('records')
    else:
        with open(file_path, 'r') as f:
            return json.load(f)

@lru_cache(maxsize=100)
def encode_image(image_path):
    """Encode image to base64 string with caching"""
    if image_path in image_cache:
        return image_cache[image_path]
    
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            with cache_lock:
                image_cache[image_path] = encoded
            return encoded
    except Exception as e:
        return None

def sanitize_filename(name):
    """Remove or replace characters that are unsafe for filenames"""
    return re.sub(r'[\\/*?:"<>|]', '_', name)

@backoff.on_exception(backoff.expo, 
                      Exception, 
                      max_tries=5,
                      max_time=60)
def api_call_with_retry(messages, model):
    """API call with retry using backoff"""
    try:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=4000
        )
    except Exception as e:
        raise

def convert_arrays_to_native(obj):
    """Convert numpy arrays and other non-native types back to Python native types"""
    if isinstance(obj, np.ndarray):
        return [convert_arrays_to_native(item) for item in obj.tolist()]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_arrays_to_native(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_arrays_to_native(item) for item in obj]
    elif hasattr(obj, 'tolist'):
        return convert_arrays_to_native(obj.tolist())
    else:
        return obj

def generate_combined_response(task_description, image_path, model):
    """Generate combined response for robot selection and action planning"""
    
    # Use system instruction imported from prompt.py
    instruction = SYSTEM_INSTRUCTION

    # Prepare the base64 encoded image
    if not os.path.exists(image_path):
        return None
    
    base64_image = encode_image(image_path)
    if not base64_image:
        return None

    # Build message sequence with image and task
    user_message_template = get_user_message_template()
    user_text = user_message_template.format(task_description=task_description)
    
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            {"type": "text", "text": user_text}
        ]}
    ]

    response = api_call_with_retry(messages, model)
    return response.choices[0].message.content

def process_sample(idx, sample, output_dir, model):
    """Process a single sample with combined robot selection and action planning"""
    
    # Extract data from parquet structure
    user_content = sample['prompt'][1]['content']
    task_description = user_content.replace('<image>', '').strip()
    
    # Get ground truth
    ground_truth = sample['reward_model']['ground_truth']
    ground_truth = convert_arrays_to_native(ground_truth)
    
    # Extract robots_set from ground_truth for compatibility
    robots_set = ground_truth.get('robots', {})
    
    # Generate task_id
    task_id = ground_truth.get('task_id', f"task_{idx}")
    
    # Save binary image to temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_file.write(sample['images'][0]['bytes'])
        image_path = tmp_file.name
    
    try:
        # Generate combined response - no robots provided, model must infer
        combined_response = generate_combined_response(task_description, image_path, model)
        
        # Compute score using viki_2
        res = viki_2.compute_score(combined_response, ground_truth)
        answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
        match = re.search(answer_pattern, combined_response)
        if not match:
            # print("No <answer> tags found")
            return 0.0
            
        answer = match.group(1).strip()
        pred_obj = ast.literal_eval(answer)
        pred_obj_transform = viki_2.transform_actions(pred_obj['action_plan'], ground_truth)

        print(f"res:{res}")
        plan_data = ground_truth.get('time_steps', [])
        if isinstance(plan_data, (dict, list)):
            plan_answer = plan_data
        else:
            plan_answer = str(plan_data)
        
        if not plan_answer or plan_answer == '':
            print(f"Warning: No existing plan found for sample {idx}")
            # Clean up temporary file
            os.unlink(image_path)
            return None
        return idx, {
            "task_id": task_id,
            "task_description": task_description,
            "ground_truth": ground_truth['time_steps'],
            # "pred_obj_transform": pred_obj_transform,
            # "combined_response": combined_response,
            #"plan_answer": plan_answer,
            "ground_truth_robots":ground_truth['robots'],
            "answer":pred_obj,
            "correct": res
        }
    
    finally:
        # Clean up temporary file
        os.unlink(image_path)

def calculate_percentage(count, total):
    """Helper function to calculate percentage safely"""
    return count / total * 100 if total > 0 else 0.0

def main():
    parser = argparse.ArgumentParser(description='robot selection and action planning evaluation for VIKI')
    parser.add_argument('--model', type=str, required=False, default="gpt-4o", help='Model name to use for inference')
    parser.add_argument('--split', type=str, required=False, default="test", help='Dataset split to use')
    args = parser.parse_args()
    
    # Define data paths
    data_path = f"data/{args.split}.parquet"
    output_dir = f"result"
    
    # Load data
    data = load_data(data_path)
    data = data[:]  # Limit for testing
    
    os.makedirs(output_dir, exist_ok=True)
    model = args.model
    max_workers = 10
    
    cot_data = []
    processed_count = 0
    save_interval = 50
    total_samples = 0
    total_scores = 0.0
    score_ranges = {
        "0.0": 0,           # Zero score
        "0.0-0.3": 0,       # Low score
        "0.3-0.6": 0,       # Medium-low score
        "0.6-0.9": 0,       # Medium-high score
        "0.9-1.0": 0,       # High score
        "1.0": 0,           # Perfect score
        ">1.0": 0           # Above perfect score
    }
    
    print(f"Processing {len(data)} samples with {max_workers} workers for VIKI dataset")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(process_sample, idx, sample, output_dir, model): idx 
            for idx, sample in enumerate(data)
        }
        
        for future in tqdm(concurrent.futures.as_completed(future_to_idx), total=len(data)):
            result = future.result()
            if result:
                idx, data_item = result
                cot_data.append(data_item)
                score = data_item["correct"]
                total_scores += score
                total_samples += 1
                
                # Statistics by score range
                if score == 0.0:
                    score_ranges["0.0"] += 1
                elif score == 1.0:
                    score_ranges["1.0"] += 1
                elif score > 1.0:
                    score_ranges[">1.0"] += 1
                elif 0.0 < score < 0.3:
                    score_ranges["0.0-0.3"] += 1
                elif 0.3 <= score < 0.6:
                    score_ranges["0.3-0.6"] += 1
                elif 0.6 <= score < 0.9:
                    score_ranges["0.6-0.9"] += 1
                elif 0.9 <= score < 1.0:
                    score_ranges["0.9-1.0"] += 1
            
            processed_count += 1
            if processed_count % save_interval == 0:
                sorted_data = sorted(cot_data, key=lambda x: x["task_id"])
                safe_model_name = sanitize_filename(model)
                with open(os.path.join(output_dir, f"combined_data_partial_{processed_count}_{safe_model_name}.json"), 'w') as f:
                    json.dump(sorted_data, f, indent=2)
                print(f"Saved {processed_count} samples")
                avg_score = total_scores / total_samples if total_samples > 0 else 0.0
                print(f"Current average score: {avg_score:.4f} ({total_scores:.2f}/{total_samples})")
    
    # Final save
    sorted_final_data = sorted(cot_data, key=lambda x: x["task_id"])
    safe_model_name = sanitize_filename(model)
    with open(os.path.join(output_dir, f"combined_data_final_{safe_model_name}.json"), 'w') as f:
        json.dump(sorted_final_data, f, indent=2)
    
    # Save statistics
    avg_score = total_scores / total_samples if total_samples > 0 else 0.0
    stats_content = f"""Combined Evaluation Results for {model} on VIKI-L2 {args.split} dataset:
Total samples processed: {total_samples}
Total scores: {total_scores:.2f}
Average score: {avg_score:.4f}

Score Distribution:
- Zero (0.0): {score_ranges["0.0"]} samples ({calculate_percentage(score_ranges["0.0"], total_samples):.1f}%)
- Low (0.0-0.3): {score_ranges["0.0-0.3"]} samples ({calculate_percentage(score_ranges["0.0-0.3"], total_samples):.1f}%)
- Medium-Low (0.3-0.6): {score_ranges["0.3-0.6"]} samples ({calculate_percentage(score_ranges["0.3-0.6"], total_samples):.1f}%)
- Medium-High (0.6-0.9): {score_ranges["0.6-0.9"]} samples ({calculate_percentage(score_ranges["0.6-0.9"], total_samples):.1f}%)
- High (0.9-1.0): {score_ranges["0.9-1.0"]} samples ({calculate_percentage(score_ranges["0.9-1.0"], total_samples):.1f}%)
- Perfect (1.0): {score_ranges["1.0"]} samples ({calculate_percentage(score_ranges["1.0"], total_samples):.1f}%)
- Above Perfect (>1.0): {score_ranges[">1.0"]} samples ({calculate_percentage(score_ranges[">1.0"], total_samples):.1f}%)
"""
    with open(os.path.join(output_dir, f"stats_{safe_model_name}_{args.split}.txt"), 'w') as f:
        f.write(stats_content)
    
    # Print final statistics
    print(f"\nCombined Evaluation Results for VIKI-L2 {args.split} dataset:")
    print(f"Total samples processed: {total_samples}")
    print(f"Total scores: {total_scores:.2f}")
    print(f"Average score: {avg_score:.4f}")
    print(f"\nScore Distribution:")
    print(f"- Zero (0.0): {score_ranges['0.0']} samples ({calculate_percentage(score_ranges['0.0'], total_samples):.1f}%)")
    print(f"- Low (0.0-0.3): {score_ranges['0.0-0.3']} samples ({calculate_percentage(score_ranges['0.0-0.3'], total_samples):.1f}%)")
    print(f"- Medium-Low (0.3-0.6): {score_ranges['0.3-0.6']} samples ({calculate_percentage(score_ranges['0.3-0.6'], total_samples):.1f}%)")
    print(f"- Medium-High (0.6-0.9): {score_ranges['0.6-0.9']} samples ({calculate_percentage(score_ranges['0.6-0.9'], total_samples):.1f}%)")
    print(f"- High (0.9-1.0): {score_ranges['0.9-1.0']} samples ({calculate_percentage(score_ranges['0.9-1.0'], total_samples):.1f}%)")
    print(f"- Perfect (1.0): {score_ranges['1.0']} samples ({calculate_percentage(score_ranges['1.0'], total_samples):.1f}%)")
    print(f"- Above Perfect (>1.0): {score_ranges['>1.0']} samples ({calculate_percentage(score_ranges['>1.0'], total_samples):.1f}%)")
    print(f"Processing completed. Total samples: {len(sorted_final_data)}")

if __name__ == "__main__":
    main()
