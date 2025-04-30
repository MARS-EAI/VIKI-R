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

# Image cache lock to prevent multi-thread write conflicts
cache_lock = threading.Lock()
# Image cache dictionary
image_cache = {}

client = OpenAI()

ROBOT_DESCRIPTION = {
    'stompy': 'A bipedal robot designed for dynamic walking and stomping tasks, featuring articulated arms. Color: Light blue body with yellow and orange accents.',
    'fetch': 'A wheeled robot with a flexible arm for object manipulation, designed for mobility and dexterity. Color: White with blue and black accents.',
    'unitree_h1': 'A humanoid robot with arms and legs designed for human-like movements and tasks. Color: Black.',
    'panda': 'A fixed robotic arm designed for precise and delicate manipulation tasks. Color: White with black accents.',
    'anymal_c': 'A quadrupedal robot built for navigating rough terrains and performing complex tasks with four articulated legs. Color: Red and black with some accents.',
    'unitree_go2': 'A compact quadrupedal robot optimized for agile movement and stability with four legs for efficient locomotion. Color: White.'
}
ACTION_DESCRIPTION = {
    'move': 'Move the robot to a specific location.',
    'reach': 'Move the robot\'s end effector near a specific object.',
    'grasp': 'The robot\'s end effector performs a grasping operation on a specific object.',
    'place': 'Place the object held by the robot\'s end effector at a specific location (note: this refers to the location where the object is to be released, not the object itself).',
    'pull': 'The robot\'s end effector performs an outward pulling operation on a specific object.',
    'push': 'The robot\'s end effector performs an inward pushing operation on a specific object.',
    'handover': 'Handover operation, where an object held by one robot is given to another robot (or received).',
    'interact': 'Interaction operation, flexible and used to represent interactions with each asset.',
}
AGENT_AVAIL_ACTIONS = {
    'panda': ['reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'fetch': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'unitree_go2': ['move', 'reach', 'grasp', 'place', 'handover', 'interact'],
    'unitree_h1': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'stompy': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'anymal_c': ['move', 'reach', 'grasp', 'place', 'handover', 'interact'],
}

AGENT_END_EFFECTOR_NUM = {
    'panda': 1,
    'fetch': 1,
    'unitree_go2': 1,
    'unitree_h1': 2,
    'stompy': 2,
    'anymal_c': 1,
}
def load_data(file_path):
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
        print(f"Error encoding image {image_path}: {e}")
        return None

@backoff.on_exception(backoff.expo, 
                      Exception, 
                      max_tries=5,
                      max_time=60)
def api_call_with_retry(messages):
    """API call with retry using backoff"""
    try:
        return client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
            max_tokens=2000
        )
    except Exception as e:
        print(f"API error: {str(e)}")
        raise

def generate_cot(task_description, robots_set, image_path, plan_answer):
    """Generate Chain of Thought by injecting existing answer and requesting CoT"""
    system_prompt = (
        "You are a plan creator. I will provide you with an image of robots in a scene, "
        "available robots and their action primitives, and a task description. "
        "You need to create a plan to complete the task, but we already have a final plan. "
        "Your job is to generate the intermediate Chain-of-Thought reasoning." 
    )
    # Prepare the base64 encoded image
    if not os.path.exists(image_path):
        print(f"Warning: Image not found at {image_path}")
        return None
    base64_image = encode_image(image_path)
    if not base64_image:
        return None

    # Get available actions and descriptions
    available_actions = {r: AGENT_AVAIL_ACTIONS.get(r, []) for r in robots_set}
    available_robots = {r: ROBOT_DESCRIPTION.get(r, '') for r in robots_set}

    print(f"Processing task: {task_description[:50]}...")
    
    # Build message sequence with image and plan
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            {"type": "text", "text": f"""
Here is a task description and a final plan that accomplishes this task.
Your job is to generate a detailed chain-of-thought reasoning process that explains how one would arrive at this plan.

Task Description: {task_description}
Available robot set: {robots_set}
Robot characteristics: {available_robots}
Their available operation APIs: {available_actions}
Action primitives and descriptions: {ACTION_DESCRIPTION}

Final Plan: {plan_answer}

Provide your step-by-step reasoning within <think>...</think> tags, analyzing:
1. Analyze the image and task
2. What sequence of actions is necessary
3. How to optimize for parallel execution
4. Any constraints or considerations

Then include the final plan exactly as provided within <answer>...</answer> tags.
"""}
        ]}
    ]
    

    response = api_call_with_retry(messages)
    return response.choices[0].message.content
            

# Modified process_sample call to accept plan_answer field (time_steps)
def process_sample(idx, sample, output_dir):
    task_description = sample['gt']['description'].strip()
    robots_set = list(sample['gt']['robots'].values())
    image_path = f"/fs-computility/mabasic/zhouheng/work/embodied/verl/data/viki_1/images/{sample['image']}"
    
    # Get plan answer and convert to string if it's a dictionary/list
    plan_data = sample.get('gt', {}).get('time_steps', '')
    if isinstance(plan_data, (dict, list)):
        plan_answer = json.dumps(plan_data, ensure_ascii=False)
    else:
        plan_answer = str(plan_data)

    if not plan_answer or plan_answer == '':
        print(f"Warning: No existing plan found for sample {idx}")
        return None

    # Check if image exists before processing
    if not os.path.exists(image_path):
        print(f"Warning: Image not found at {image_path}")
        return None

    cot_response = generate_cot(task_description, robots_set, image_path, plan_answer)
    if cot_response:
        return idx, {
            "task_description": task_description,
            "robots_set": robots_set,
            "plan_answer": plan_answer,
            "cot": cot_response,
            "image_path": image_path
        }
    return None

def main():
    data = load_data("/fs-computility/mabasic/zhouheng/work/embodied/verl/data/viki_2/metadata_trans.json")
    
    output_dir = "data/viki_2/cot_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all possible robot set
    robot_set = list(ROBOT_DESCRIPTION.keys())
    
    # Use thread pool for parallel processing
    max_workers = 10  # Adjust parallel count based on API limits
    cot_data = []
    processed_count = 0
    save_interval = 10
    
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
            
            processed_count += 1
            if processed_count % save_interval == 0:
                # Sort results by index
                sorted_data = sorted(cot_data, key=lambda x: next((i for i, s in enumerate(data) if s.get('image', '').split('/')[-1] == x.get('image_path', '').split('/')[-1]), 0))
                with open(os.path.join(output_dir, f"cot_data_partial_{processed_count}.json"), 'w') as f:
                    json.dump(sorted_data, f, indent=2)
                print(f"Saved {processed_count} samples")
    
    # Final save of all data
    # Sort results by original data index
    sorted_final_data = sorted(cot_data, key=lambda x: next((i for i, s in enumerate(data) if s.get('image', '').split('/')[-1] == x.get('image_path', '').split('/')[-1]), 0))
    with open(os.path.join(output_dir, "cot_data_final.json"), 'w') as f:
        json.dump(sorted_final_data, f, indent=2)
    print(f"Processing completed. Total samples: {len(sorted_final_data)}")

if __name__ == "__main__":
    main() 