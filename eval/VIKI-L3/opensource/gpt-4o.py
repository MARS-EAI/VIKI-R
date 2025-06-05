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
import re
from verl.utils.reward_score import viki_2, viki_3, viki_3_re
import pandas as pd
import ast
import tempfile
import numpy as np

def convert_arrays_to_native(obj):
    """Convert numpy arrays and other non-native types back to Python native types"""
    if isinstance(obj, np.ndarray):
        # Convert numpy array to list and recursively process each element
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
    elif hasattr(obj, 'tolist'):  # Handle other numpy types
        return convert_arrays_to_native(obj.tolist())
    else:
        return obj

# Image cache lock to prevent multi-thread write conflicts
cache_lock = threading.Lock()
# Image cache dictionary
image_cache = {}
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
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
        # print(f"Error encoding image {image_path}: {e}")
        return None

@backoff.on_exception(backoff.expo, 
                      Exception, 
                      max_tries=5,
                      max_time=60)
def api_call_with_retry(messages, model_name):
    """API call with retry using backoff"""
    try:
        return client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.0,
            max_tokens=2000
        )
    except Exception as e:
        # print(f"API error: {str(e)}")
        raise
def sanitize_filename(name):
    """Remove or replace characters that are unsafe for filenames"""
    # Replace slashes, backslashes, and other filesystem-unsafe characters
    return re.sub(r'[\\/*?:"<>|]', '_', name)
def generate_cot(task_description, image_path, model_name):
    instruction_following = """
You are an expert in visual understanding and trajectory planning.
**INPUT:**
* An ego-view image showing two robotic arms working together; the arm closest to the camera represents **you**.
* A string describing the overall task.
* Two strings specifying your subtask ("you") and your partner's subtask.
**YOUR JOB:**
1. Enclose your scene analysis and task division within `<think>…</think>` tags.
2. Enclose your final output within `<answer>…</answer>` tags as a nested list of **ten 2D pixel coordinates**:
   * Two groups of five points each:
     * **First group:** your trajectory
     * **Second group:** your partner's trajectory
3. Follow this format **exactly** (no additional text):
   [[ [x1, y1], [x2, y2], [x3, y3], [x4, y4], [x5, y5] ],
    [ [x1', y1'], [x2', y2'], [x3', y3'], [x4', y4'], [x5', y5'] ]]
"""
    # Prepare the base64 encoded image
    if not os.path.exists(image_path):
        # print(f"Warning: Image not found at {image_path}")
        return None
    base64_image = encode_image(image_path)
    if not base64_image:
        return None

    messages = [
        {"role": "system", "content": instruction_following},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            {"type": "text", "text": f"""{task_description}"""}
        ]}
    ]
    

    response = api_call_with_retry(messages, model_name)
    return response.choices[0].message.content
# Modified process_sample call to accept plan_answer field (time_steps)
def process_sample(idx, sample, output_dir, model_name):
    # Extract data from new parquet structure
    # Get task description from user prompt (remove '<image>' prefix)
    user_content = sample['prompt'][1]['content']  # user message
    task_description = user_content.replace('<image>', '').strip()
    
    # For VIKI-L3, ground_truth contains the trajectory data as string
    ground_truth = sample['reward_model']['ground_truth']
    # Convert numpy arrays back to native Python types if needed
    ground_truth = convert_arrays_to_native(ground_truth)
    
    # Generate a task_id based on index since it might not be in the new structure
    task_id = f"task_{idx}"
    
    # Save the binary image to a temporary file for processing
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_file.write(sample['images'][0]['bytes'])
        image_path = tmp_file.name

    ans_response = generate_cot(task_description, image_path, model_name)
    
    # Clean up temporary file
    os.unlink(image_path)
    
    res, rmse_score, hd_score, dtw_score = viki_3_re.compute_score(ans_response, ground_truth)
    print(f"res:{res}")
    return idx, {
        "task_id": task_id,
        "task_description": task_description,
        "answer": ground_truth,
        "ans": ans_response,
        "image_path": f"binary_image_{idx}",  # placeholder since we used temp file
        "overall_score": res,
        "rmse_score": rmse_score,
        "hd_score": hd_score,
        "dtw_score": dtw_score
    }

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run evaluation with specified model')
    parser.add_argument('--model', type=str, default="gpt-4o", 
                        help='Model name to use for API calls')
    args = parser.parse_args()
    model_name = args.model
    
    # Define data paths and output directories
    datasets = {
        'test': {
            'data_path': "RoboFactory-VIKI/data/viki/VIKI-L3/test.parquet",
            'output_dir': "eval/VIKI-L3/opensource/results/test"
        }
    }
    
    max_workers = 10  # Adjust parallel count based on API limits
    
    for dataset_name, dataset_info in datasets.items():
        print(f"\nProcessing {dataset_name} dataset...")
        
        data = load_data(dataset_info['data_path'])
        data = data[:100]
        output_dir = dataset_info['output_dir']
        
        os.makedirs(output_dir, exist_ok=True)
        
        cot_data = []
        processed_count = 0
        save_interval = 2000
        
        # Score tracking variables
        total_samples = 0
        sum_overall_score = 0
        sum_rmse_score = 0
        sum_hd_score = 0
        sum_dtw_score = 0
        
        print(f"Processing {len(data)} samples with {max_workers} workers using model: {model_name}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_idx = {
                executor.submit(process_sample, idx, sample, output_dir, model_name): idx 
                for idx, sample in enumerate(data)
            }
            
            # Use tqdm to create progress bar
            for future in tqdm(concurrent.futures.as_completed(future_to_idx), total=len(data)):
                result = future.result()
                if result:
                    idx, data_item = result
                    cot_data.append(data_item)
                    
                    # Track scores
                    sum_overall_score += data_item["overall_score"]
                    sum_rmse_score += data_item["rmse_score"]
                    sum_hd_score += data_item["hd_score"]
                    sum_dtw_score += data_item["dtw_score"]
                    total_samples += 1
                
                processed_count += 1
                if processed_count % save_interval == 0:
                    # Sort results by index
                    sorted_data = sorted(cot_data, key=lambda x: next((i for i, s in enumerate(data) if s.get('image', '').split('/')[-1] == x.get('image_path', '').split('/')[-1]), 0))
                    safe_model_name = sanitize_filename(model_name)
                    with open(os.path.join(output_dir, f"cot_data_partial_{processed_count}_{safe_model_name}.json"), 'w') as f:
                        json.dump(sorted_data, f, indent=2)
                    print(f"Saved {processed_count} samples")
                    if total_samples > 0:
                        print(f"Current mean scores: overall={sum_overall_score/total_samples:.4f}, rmse={sum_rmse_score/total_samples:.4f}, hd={sum_hd_score/total_samples:.4f}, dtw={sum_dtw_score/total_samples:.4f}")
        
        # Final save of all data
        # Sort results by original data index
        sorted_final_data = sorted(cot_data, key=lambda x: next((i for i, s in enumerate(data) if s.get('image', '').split('/')[-1] == x.get('image_path', '').split('/')[-1]), 0))
        safe_model_name = sanitize_filename(model_name)
        with open(os.path.join(output_dir, f"cot_data_final_{safe_model_name}_{dataset_name}.json"), 'w') as f:
            json.dump(sorted_final_data, f, indent=2)
        
        # Calculate final mean scores
        mean_overall_score = sum_overall_score / total_samples if total_samples > 0 else 0
        mean_rmse_score = sum_rmse_score / total_samples if total_samples > 0 else 0
        mean_hd_score = sum_hd_score / total_samples if total_samples > 0 else 0
        mean_dtw_score = sum_dtw_score / total_samples if total_samples > 0 else 0
        
        # Save summary results to a txt file
        with open(os.path.join(output_dir, f"results_summary_{safe_model_name}_{dataset_name}.txt"), 'w') as f:
            f.write(f"Final Evaluation Results for {dataset_name} dataset:\n")
            f.write(f"Model: {model_name}\n")
            f.write(f"Total samples processed: {total_samples}\n")
            f.write(f"Mean overall score: {mean_overall_score:.4f}\n")
            f.write(f"Mean RMSE score: {mean_rmse_score:.4f}\n")
            f.write(f"Mean HD score: {mean_hd_score:.4f}\n")
            f.write(f"Mean DTW score: {mean_dtw_score:.4f}\n")
        
        # Print final statistics
        print(f"\nFinal Evaluation Results for {dataset_name} dataset:")
        print(f"Model: {model_name}")
        print(f"Total samples processed: {total_samples}")
        print(f"Mean overall score: {mean_overall_score:.4f}")
        print(f"Mean RMSE score: {mean_rmse_score:.4f}")
        print(f"Mean HD score: {mean_hd_score:.4f}")
        print(f"Mean DTW score: {mean_dtw_score:.4f}")
        print(f"Processing completed. Total samples: {len(sorted_final_data)}")

if __name__ == "__main__":
    main() 