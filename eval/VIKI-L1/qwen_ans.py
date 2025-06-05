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
from verl.utils.reward_score import viki_1, viki_2
import pandas as pd
import ast
import tempfile
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key="EMPTY",base_url="http://0.0.0.0:8000/v1")

# Image cache lock to prevent multi-thread write conflicts
cache_lock = threading.Lock()
# Image cache dictionary
image_cache = {}

ROBOT_DESCRIPTION = {
    'stompy': 'A bipedal robot designed for dynamic walking and stomping tasks, featuring articulated arms. Color: Light blue body with yellow and orange accents.',
    'fetch': 'A wheeled robot with a flexible arm for object manipulation, designed for mobility and dexterity. Color: White with blue and black accents.',
    'unitree_h1': 'A humanoid robot with arms and legs designed for human-like movements and tasks. Color: Black.',
    'panda': 'A fixed robotic arm designed for precise and delicate manipulation tasks. Color: White with black accents.',
    'anymal_c': 'A quadrupedal robot built for navigating rough terrains and performing complex tasks with four articulated legs. Color: Red and black with some accents.',
    'unitree_go2': 'A compact quadrupedal robot optimized for agile movement and stability with four legs for efficient locomotion. Color: White.'
}
ACTION_DESCRIPTION = {
    'Move': "Command ['Move', 'object']: Robot R moves to the specified object.",
    'Open': "Command ['Open', 'object']: Open the object held by the Robot R's end effector.",
    'Close': "Command ['Close', 'object']: Close the object held by the Robot R's end effector.",
    'Reach': "Command ['Reach', 'object']: Robot R reaches the specified object.",
    'Grasp': "Command ['Grasp', 'object']: Robot R's end effector performs a grasping operation on a specified object.",
    'Place': "Command ['Place', 'object']: Place the object held by the Robot R's end effector at a specified location (the release point, not the object itself).",
    'Push': "Command ['Push', 'object', 'R1']: Robot R pushes the object to robot R1.",
    'Interact': "Command ['Interact', 'object']: A general interaction operation, flexible for representing interactions with any asset."

}
AGENT_AVAIL_ACTIONS = {
    'panda':      ['Reach', 'Grasp', 'Place', 'Open', 'Close', 'Interact'],
    'fetch':      ['Move', 'Reach', 'Grasp', 'Place', 'Open', 'Close', 'Interact'],
    'unitree_go2':['Move', 'Push', 'Interact'],
    'unitree_h1': ['Move', 'Reach', 'Grasp', 'Place', 'Open', 'Close', 'Interact'],
    'stompy':     ['Move', 'Reach', 'Grasp', 'Place', 'Open', 'Close', 'Interact'],
    'anymal_c':   ['Move', 'Push', 'Interact'],
}

AGENT_END_EFFECTOR_NUM = {
    'panda': 1,
    'fetch': 1,
    'unitree_go2': 0,
    'unitree_h1': 2,
    'stompy': 2,
    'anymal_c': 0,
}
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
def api_call_with_retry(messages):
    """API call with retry using backoff"""
    try:
        return client.chat.completions.create(
            model="Qwen2.5-VL-7B-Instruct",
            messages=messages,
            temperature=0,
            max_tokens=2000
        )
    except Exception as e:
        # print(f"API error: {str(e)}")
        raise

def generate_cot(task_description, robots, image_path, plan_answer):
    robot_set = """
Stompy: A bipedal robot designed for dynamic walking and stomping tasks, featuring articulated arms. Color: Light blue body with yellow and orange accents.
Fetch: A wheeled robot with a flexible arm for object manipulation, designed for mobility and dexterity. Color: White with blue and black accents.
Unitree_H1: A humanoid robot with arms and legs designed for human-like movements and tasks. Color: Black.
Panda: A fixed robotic arm designed for precise and delicate manipulation tasks. Color: White with black accents.
Anymal_C: A quadrupedal robot built for navigating rough terrains and performing complex tasks with four articulated legs. Color: Red and black with some accents.
Unitree_Go2: A compact quadrupedal robot optimized for agile movement and stability with four legs for efficient locomotion. Color: White."""
    instruction_following = (
        r'Possible robots: {robot_set} '
        r'First, identify the robots visible in the image from a list of "possible robots". Among the visible robots, select the most suitable one or more to collaborate on the task.'
        r'You FIRST think about the reasoning process as an internal monologue and then provide the final answer. '
        r'The reasoning process MUST BE enclosed within <think> </think> tags. The final answer MUST BE enclosed within <answer>Your final answer must be provided as a Python list format, for example: [\'fetch\', \'unitree_h1\']. Include only the robot names that are suitable for the task.</answer> tags.'
    )
    """Generate Chain of Thought by injecting existing answer and requesting CoT"""
    # Prepare the base64 encoded image
    if not os.path.exists(image_path):
        # print(f"Warning: Image not found at {image_path}")
        return None
    base64_image = encode_image(image_path)
    if not base64_image:
        return None
    robots_list = list(robots.values())
    # Get available actions and descriptions

    # print(f"Processing task: {task_description[:50]}...")
    
    # Build message sequence with image and plan
    messages = [
        {"role": "system", "content": instruction_following.format(robot_set=robot_set)},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            {"type": "text", "text": f"""Task Description: {task_description}
"""}
        ]}
    ]
    

    response = api_call_with_retry(messages)
    return response.choices[0].message.content

def process_sample(idx, sample, output_dir):
    # Extract data from new parquet structure
    # Get task description from user prompt (remove '<image>' prefix)
    user_content = sample['prompt'][1]['content']  # user message
    task_description = user_content.replace('<image>', '').strip()
    
    # Get ground truth from reward_model
    ground_truth_str = sample['reward_model']['ground_truth']
    # Parse the string representation of list back to actual list
    ground_truth = ast.literal_eval(ground_truth_str)
    
    # Create a dummy robots_set for compatibility (since we don't have the original structure)
    # We'll extract robot names from ground_truth
    robots_set = {f"robot_{i}": robot for i, robot in enumerate(ground_truth)}
    
    # Generate a task_id based on index since it's not in the new structure
    task_id = f"task_{idx}"
    
    # Save the binary image to a temporary file for processing
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_file.write(sample['images'][0]['bytes'])
        image_path = tmp_file.name
    
    answer = ground_truth
    robots_idle = []  # Not available in new structure
    
    cot_response = generate_cot(task_description, robots_set, image_path, answer)
    
    # Clean up temporary file
    os.unlink(image_path)
    
    # Keep the special ans_response logic from the original qwen_ans.py
    ans_response = "<think> 123 </think>"+"<answer>"+cot_response+"</answer>"
    res = viki_1.compute_score(ans_response, ground_truth)
    print(f"res:{res}")
    return idx, {
        "task_id": task_id,
        "task_description": task_description,
        "robots_set": robots_set,
        "plan_answer": answer,
        "cot": cot_response,
        "image_path": f"binary_image_{idx}",  # placeholder since we used temp file
        "correct": res
    }

#vllm serve models/qwen2.5_vl-7b/merged_model/rft_495_112 --served-model-name Qwen2.5-VL-7B-Instruct
#vllm serve models/qwen2.5_vl-7b/full/viki_plan_cot_488/checkpoint-30 --served-model-name Qwen2.5-VL-7B-Instruct
def main():
    
    # data=load_data("data/viki/viki_plan_final/split_6/id/val.json")
    # output_dir = "eval/56new/ood"
    
    data=load_data("RoboFactory-VIKI/data/viki/VIKI-L1/test.parquet")
    output_dir = "eval/VIKI-L1/qwen_ans/result"

    os.makedirs(output_dir, exist_ok=True)
    model="Qwen2.5-VL-3B-Instruct_sft_all_ans"
    # Use thread pool for parallel processing
    max_workers = 1  # Adjust parallel count based on API limits
    cot_data = []
    processed_count = 0
    save_interval = 2000
    total_correct = 0
    total_samples = 0
    total_zero = 0
    total_one = 0
    total_gt_one = 0
    
    print(f"Processing {len(data)} samples with {max_workers} workers")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_idx = {
            executor.submit(process_sample, idx, sample, output_dir): idx 
            for idx, sample in enumerate(data)
        }
        
        # Use tqdm to create progress bar
        for future in tqdm(concurrent.futures.as_completed(future_to_idx), total=len(data)):
            result = future.result()
            if result:
                idx, data_item = result
                cot_data.append(data_item)
                if data_item["correct"]>0.1:
                    total_correct += 1
                if data_item["correct"] == 0:
                    total_zero += 1
                if data_item["correct"] == 1:
                    total_one += 1
                if data_item["correct"] > 1:
                    total_gt_one += 1
                total_samples += 1
            
            processed_count += 1
            if processed_count % save_interval == 0:
                # Sort results by index
                sorted_data = sorted(cot_data, key=lambda x: next((i for i, s in enumerate(data) if s.get('image', '').split('/')[-1] == x.get('image_path', '').split('/')[-1]), 0))
                with open(os.path.join(output_dir, f"cot_data_partial_{processed_count}.json"), 'w') as f:
                    json.dump(sorted_data, f, indent=2)
                print(f"Saved {processed_count} samples")
                print(f"Current accuracy: {total_correct/total_samples:.4f} ({total_correct}/{total_samples})")
    
    # Final save of all data
    # Sort results by original data index
    sorted_final_data = sorted(cot_data, key=lambda x: next((i for i, s in enumerate(data) if s.get('image', '').split('/')[-1] == x.get('image_path', '').split('/')[-1]), 0))
    with open(os.path.join(output_dir, f"cot_data_final_{model}.json"), 'w') as f:
        json.dump(sorted_final_data, f, indent=2)
    
    # Save statistics to a txt file
    stats_content = f"""Final Evaluation Results for {model}:
Total samples processed: {total_samples}
Total correct predictions (res > 0.1): {total_correct}
Total predictions equal to 0: {total_zero}
Total predictions equal to 1: {total_one}
Total predictions greater than 1: {total_gt_one}
Final accuracy: {total_correct/total_samples:.4f}
"""
    with open(os.path.join(output_dir, f"stats_{model}.txt"), 'w') as f:
        f.write(stats_content)
    
    # Print final statistics
    print("\nFinal Evaluation Results:")
    print(f"Total samples processed: {total_samples}")
    print(f"Total correct predictions (res > 0.1): {total_correct}")
    print(f"Total predictions equal to 0: {total_zero}")
    print(f"Total predictions greater than 1: {total_gt_one}")
    print(f"Final accuracy: {total_correct/total_samples:.4f}")
    print(f"Processing completed. Total samples: {len(sorted_final_data)}")

if __name__ == "__main__":
    main() 