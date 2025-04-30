"""
Preprocess the Viki-Count dataset to parquet format
"""

import os
import json
import datasets
from datasets import Dataset
from verl.utils.hdfs_io import copy, makedirs
import argparse
from PIL import Image
import io
import logging
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ROBOT_DESCRIPTION = {
    'stompy': 'A bipedal robot designed for dynamic walking and stomping tasks, featuring articulated arms. Color: Light blue body with yellow and orange accents.',
    'fetch': 'A wheeled robot with a flexible arm for object manipulation, designed for mobility and dexterity. Color: White with blue and black accents.',
    'unitree_h1': 'A humanoid robot with arms and legs designed for human-like movements and tasks. Color: Black.',
    'panda': 'A fixed robotic arm designed for precise and delicate manipulation tasks. Color: White with black accents.',
    'anymal_c': 'A quadrupedal robot built for navigating rough terrains and performing complex tasks with four articulated legs. Color: Red and black with some accents.',
    'unitree_go2': 'A compact quadrupedal robot optimized for agile movement and stability with four legs for efficient locomotion. Color: White.'
}
ACTION_DESCRIPTION = {
    'move': "Command ['move', 'object']: Robot R moves to the specified object.",
    'open': "Command ['open', 'object']: Open the object held by the Robot R's end effector.",
    'close': "Command ['close', 'object']: Close the object held by the Robot R's end effector.",
    'reach': "Command ['reach', 'object']: Robot R reaches the specified object.",
    'grasp': "Command ['grasp', 'object']: Robot R's end effector performs a grasping operation on a specified object.",
    'place': "Command ['place', 'object']: Place the object held by the Robot R's end effector at a specified location (the release point, not the object itself).",
    'push': "Command ['push', 'object', 'R1']: Robot R pushes the object to robot R1.",
    'interact': "Command ['interact', 'object']: A general interaction operation, flexible for representing interactions with any asset."

}

AGENT_AVAIL_ACTIONS = {
    'panda': ['reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'fetch': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'unitree_go2': ['move', 'push', 'interact'],
    'unitree_h1': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'stompy': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'anymal_c': ['move', 'push', 'interact'],
}

AGENT_END_EFFECTOR_NUM = {
    'panda': 1,
    'fetch': 1,
    'unitree_go2': 0,
    'unitree_h1': 2,
    'stompy': 2,
    'anymal_c': 0,
}
def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def image_to_bytes(image_path):
    """Convert image to bytes"""
    try:
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None
            
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            return buffered.getvalue()
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {str(e)}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local_dir', default='/fs-computility/mabasic/zhouheng/work/embodied/verl/data/viki/viki_plan')
    parser.add_argument('--hdfs_dir', default=None)
    parser.add_argument('--data_dir', default='/fs-computility/mabasic/zhouheng/work/embodied/verl/data/viki/viki_plan')
    args = parser.parse_args()

    # Load train and test data
    train_data = load_json_data(os.path.join(args.data_dir, 'meta_data_4500_trans_train.json'))
    test_data = load_json_data(os.path.join(args.data_dir, 'meta_data_4500_trans_test.json'))

    logger.info(f"Loaded {len(train_data)} training samples and {len(test_data)} test samples")

    instruction_following = """You are a plan creator. I will provide you with an image of robots in a scene, available robots and their action primitives, and a task description. You need to create a plan to complete the task.
You FIRST think about the reasoning process as an internal monologue and then provide the final answer. 
The reasoning process MUST BE enclosed within <think> </think> tags. The final answer MUST BE enclosed within <answer></answer> tags.

1. Analyze the image, understand the robots and their available actions, and comprehend the task description.
2. Create a plan to complete the task, noting:
   - Each robot can only perform ONE action per time step.
   - Multiple robots can work in parallel, but each robot is limited to one action at a time.
3. You need to first provide your reasoning process within <think> and </think> tags.
4. Your final answer must be within <answer> and </answer> tags, and **strictly follow the JSON format specified below**.

Output Format Requirements(please comply strictly, do not output any additional content):
<answer>
  [
    {{
      "step": 1,
      "plan": {{'R1': ['Grasp', 'apple'], 'R2': ['Push', 'cardboardbox', 'R1']}}
      
    }},
    {{
      "step": 2,
      "plan": {{'R1': ['Reach', 'pumpkin'], 'R2': ['Reach', 'apple']}}
    }}
    # ... subsequent steps ...
  ]
</answer>

Where:
- step is the time step number (starting from 1, incrementing sequentially).
- Each actions list contains the actions of various robots in that time step.
- Each robot can only have ONE action per time step.
- "plan" is a dictionary that specifies the action for each robot during a single time step. Each key (e.g., "R1", "R2") represents a robot. Each value is a list describing the single action that robot will perform in this step, with the following format: [action_type, target_object_or_location, (optional: extra_argument)]
Action primitives and descriptions: {ACTION_DESCRIPTION}
Available robot set: {robots_set}
Robot characteristics: {available_robots}
Their available operation APIs: {available_actions}
"""

    def process_data(data, split):
        processed_data = []
        skipped_count = 0

        for idx, item in enumerate(data):
            try:
                # Extract user and assistant messages
                user_message = '<image>'+item['gt']['description']
                answer=item['gt']
                robot=item['gt']['robots']
                robots_set=list(item['gt']['robots'].values())
                available_actions = {r: AGENT_AVAIL_ACTIONS.get(r, []) for r in robots_set}
                available_robots = {r: ROBOT_DESCRIPTION.get(r, '') for r in robots_set}
                # Convert images to bytes
                image_binaries = []
                image_path=f"/fs-computility/mabasic/zhouheng/work/embodied/verl/data/compress/images_4500/{item['image']}"
                try:
                    with open(image_path, 'rb') as f:
                        image_binaries.append(f.read())
                except Exception as e:
                    logger.warning(f"Failed to read image {image_path}: {str(e)}")
                    skipped_count += 1
                    continue
                if not image_binaries:
                    logger.warning(f"No valid images found for sample {idx}")
                    skipped_count += 1
                    continue

                # Structure the data
                processed_item = {
                    "images": [
                        {
                            "bytes": image_binaries[0],
                            "path":None
                        }
                    ],
                    "data_source": "viki_2",
                    "prompt": [
                        {
                            "role": "system",
                            "content": instruction_following.format(ACTION_DESCRIPTION=ACTION_DESCRIPTION,robots_set=robot,available_actions=available_actions,available_robots=available_robots)
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    "ability": "plan",
                    "reward_model": {
                        "style": "rule",
                        "ground_truth": answer
                    }
                }
                processed_data.append(processed_item)
            except Exception as e:
                logger.warning(f"Failed to process sample {idx}: {str(e)}")
                skipped_count += 1
                continue

        logger.info(f"Processed {len(processed_data)} samples for {split} split, skipped {skipped_count} samples")
        return processed_data

    # Process train and test data
    train_processed = process_data(train_data, 'train')
    test_processed = process_data(test_data, 'test')

    if not train_processed:
        raise ValueError("No training samples were successfully processed!")
    if not test_processed:
        raise ValueError("No test samples were successfully processed!")

    # Convert to HuggingFace datasets
    train_dataset = Dataset.from_list(train_processed)
    test_dataset = Dataset.from_list(test_processed)

    logger.info(f"Created datasets with {len(train_dataset)} training samples and {len(test_dataset)} test samples")

    local_dir = args.local_dir
    hdfs_dir = args.hdfs_dir

    # Save to parquet
    train_dataset.to_parquet(os.path.join(local_dir, 'train_50k.parquet'))
    test_dataset.to_parquet(os.path.join(local_dir, 'test_50k.parquet'))

    if hdfs_dir is not None:
        makedirs(hdfs_dir)
        copy(src=local_dir, dst=hdfs_dir) 
