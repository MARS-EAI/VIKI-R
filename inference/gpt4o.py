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
from verl.utils.reward_score import viki_2
# Image cache lock to prevent multi-thread write conflicts
cache_lock = threading.Lock()
# Image cache dictionary
image_cache = {}
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
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
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
            max_tokens=2000
        )
    except Exception as e:
        # print(f"API error: {str(e)}")
        raise

def generate_cot(task_description, robots, image_path, plan_answer):
    instruction_following = """You are a plan creator. I will provide you with an image of robots in a scene, available robots and their action primitives, and a task description. You need to create a plan to complete the task.
1. Create a plan to complete the task, noting:
   - Each robot can only perform ONE action per time step.
   - Multiple robots can work in parallel, but each robot is limited to one action at a time.
2. You need to first provide your reasoning process within <think> and </think> tags.
3. Your final answer must be within <answer> and </answer> tags, and **strictly follow the JSON format specified below**.

Output Format Requirements(please comply strictly, do not output any additional content):
<answer>
  [
    {{
      "step": 1,
      "actions": {{'R1': ['Move', 'pumpkin'], 'R2': ['Move', 'apple']}}
    }},
    {{
      "step": 2,
      "actions": {{'R1': ['Reach', 'pumpkin'], 'R2': ['Reach', 'apple']}}
    }}
    # ... subsequent steps ...
  ]
</answer>
Where:
- step is the time step number (starting from 1, incrementing sequentially).
- Each robot can only have ONE action per time step.
- "actions" is a dictionary that specifies the action for each robot during a single time step. Each key (e.g., "R1", "R2") represents a robot. Each value is a list describing the single action that robot will perform in this step, with the following format: action_type, target_object_or_location, (optional: extra_argument)
Action primitives and descriptions: {ACTION_DESCRIPTION}
Available robot set: {robots}
Robot characteristics: {available_robots}
Their available operation APIs: {available_actions}
"""
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
    available_actions = {r: AGENT_AVAIL_ACTIONS.get(r, []) for r in robots_list}
    available_robots = {r: ROBOT_DESCRIPTION.get(r, '') for r in robots_list}

    # print(f"Processing task: {task_description[:50]}...")
    
    # Build message sequence with image and plan
    messages = [
        {"role": "system", "content": instruction_following.format(ACTION_DESCRIPTION=ACTION_DESCRIPTION,robots=robots,available_actions=available_actions,available_robots=available_robots)},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            {"type": "text", "text": f"""{task_description}"""}
        ]}
    ]
    

    response = api_call_with_retry(messages)
    return response.choices[0].message.content
# Modified process_sample call to accept plan_answer field (time_steps)
def process_sample(idx, sample, output_dir):
    task_id=sample['gt']['task_id']
    ground_truth=sample['gt']
    task_description = sample['gt']['description'].strip()
    robots_set = sample['gt']['robots']
    image_path = f"/fs-computility/mabasic/zhouheng/work/embodied/verl/data/merged_images/{sample['image']}"
    
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
    res = viki_2.compute_score(cot_response, ground_truth)
    print(f"res:{res}")
    return idx, {
        "task_id":task_id,
        "task_description": task_description,
        "robots_set": robots_set,
        "plan_answer": plan_answer,
        "cot": cot_response,
        "image_path": image_path,
        "correct": res
    }

def main():
    data = load_data("/fs-computility/mabasic/zhouheng/work/embodied/verl/data/viki/viki_plan_final/split/test.json")
    data=data[:500]
    output_dir = "/fs-computility/mabasic/zhouheng/RoboViki-R/eval"
    os.makedirs(output_dir, exist_ok=True)
    model="gpt-4o"
    # Use thread pool for parallel processing
    max_workers = 10  # Adjust parallel count based on API limits
    cot_data = []
    processed_count = 0
    save_interval = 300
    total_correct = 0
    total_samples = 0
    
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
                if data_item["correct"]==1:
                    total_correct += 1
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
    
    # Print final statistics
    print("\nFinal Evaluation Results:")
    print(f"Total samples processed: {total_samples}")
    print(f"Total correct predictions: {total_correct}")
    print(f"Final accuracy: {total_correct/total_samples:.4f}")
    print(f"Processing completed. Total samples: {len(sorted_final_data)}")

if __name__ == "__main__":
    main() 