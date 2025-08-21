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
    """Process a single sample with inference only"""
    
    # Extract data from parquet structure
    user_content = sample['prompt'][1]['content']
    task_description = user_content.replace('<image>', '').strip()
    
    # Generate task_id
    task_id = f"task_{idx}"
    
    # Save binary image to temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_file.write(sample['images'][0]['bytes'])
        image_path = tmp_file.name
    
    try:
        # Generate combined response - no robots provided, model must infer
        combined_response = generate_combined_response(task_description, image_path, model)
        
        # Extract answer from response
        answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
        match = re.search(answer_pattern, combined_response)
        if not match:
            print(f"No <answer> tags found for sample {idx}")
            return None
            
        answer = match.group(1).strip()
        try:
            pred_obj = ast.literal_eval(answer)
        except:
            print(f"Failed to parse answer for sample {idx}")
            return None

        return idx, {
            "task_id": task_id,
            "task_description": task_description,
            "answer": pred_obj,
            "combined_response": combined_response
        }
    
    finally:
        # Clean up temporary file
        os.unlink(image_path)


def main():
    parser = argparse.ArgumentParser(description='robot selection and action planning inference for VIKI')
    parser.add_argument('--model', type=str, required=False, default="gpt-4o", help='Model name to use for inference')
    parser.add_argument('--split', type=str, required=False, default="test", help='Dataset split to use')
    args = parser.parse_args()
    
    # Define data paths
    data_path = f"data/{args.split}.parquet"
    output_dir = f"result"
    
    # Load data
    data = load_data(data_path)
    data = data[:10]  # Limit for testing
    
    os.makedirs(output_dir, exist_ok=True)
    model = args.model
    max_workers = 10
    
    cot_data = []
    processed_count = 0
    save_interval = 50
    
    print(f"Processing {len(data)} samples with {max_workers} workers for VIKI dataset")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(process_sample, idx, sample, output_dir, model): idx 
            for idx, sample in enumerate(data)
        }
        
        for future in tqdm(concurrent.futures.as_completed(future_to_idx), total=len(data)):
            result = future.result()
            if result:
                _, data_item = result
                cot_data.append(data_item)
            
            processed_count += 1
            if processed_count % save_interval == 0:
                sorted_data = sorted(cot_data, key=lambda x: x["task_id"])
                safe_model_name = sanitize_filename(model)
                with open(os.path.join(output_dir, f"inference_data_partial_{processed_count}_{safe_model_name}.json"), 'w') as f:
                    json.dump(sorted_data, f, indent=2)
                print(f"Saved {processed_count} samples")
    
    # Final save
    sorted_final_data = sorted(cot_data, key=lambda x: x["task_id"])
    safe_model_name = sanitize_filename(model)
    with open(os.path.join(output_dir, f"inference_data_final_{safe_model_name}.json"), 'w') as f:
        json.dump(sorted_final_data, f, indent=2)
    
    print(f"\nInference completed. Total samples: {len(sorted_final_data)}")

if __name__ == "__main__":
    main()
