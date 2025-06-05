# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import ast
import json
from mathruler.grader import extract_boxed_content, grade_answer
from typing import List, Dict
from verl.utils.reward_score.utils.eval_re.eval_viki_2 import eval_single

def format_reward(predict_str: str) -> float:
    # Check overall structure with <think> and <answer> tags
    structure_pattern = re.compile(r'<think>.*</think>.*<answer>.*</answer>.*', re.DOTALL)
    structure_match = re.fullmatch(structure_pattern, predict_str)
    
    if not structure_match:
        return 0.0
    
    # Extract answer content
    answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
    answer_match = re.search(answer_pattern, predict_str)
    
    if not answer_match:
        return 0.0
    
    answer_content = answer_match.group(1).strip()
    
    # Check for double braces format
    double_braces_pattern = re.compile(r'\{\{.*\}\}', re.DOTALL)
    if re.search(double_braces_pattern, answer_content):
        answer_content = answer_content.replace('{{', '{').replace('}}', '}')

    try:
        # First try to parse as a list or dict directly
        parsed = ast.literal_eval(answer_content)
        return 1.0 if isinstance(parsed, (list, dict)) else 0.0
    except (ValueError, SyntaxError, TypeError):
        try:
            # If direct parsing fails, try to evaluate as a string representation
            # This avoids issues with sets containing unhashable types
            parsed = eval(answer_content, {'__builtins__': {}}, {})
            return 1.0 if isinstance(parsed, (list, dict)) else 0.0
        except Exception:
            return 0.0

def transform_actions(data):
    # Handle single step input
    if isinstance(data, list) and 'step' in data and 'actions' in data:
        data = [data]  # Convert single step to list format
    
    if not isinstance(data, list):
        return []
        
    result = []
    try:
        for step_info in data:
            if not isinstance(step_info, dict):
                continue
                
            actions = step_info.get('actions', {})
            if not isinstance(actions, dict):
                continue
                
            step_actions = {}
            for robot, action_list in actions.items():
                step_actions[robot] = f'<{",".join(action_list)}>'
                
            if step_actions:  # Only append if we have actions for this step
                result.append(step_actions)
                
    except Exception as e:
        return []
        
    return result

def acc_reward(predict_str: str, ground_truth: List[Dict]) -> float:
    try:
        # print(f"\nInput predict_str: {predict_str}")
        # print(f"Input ground_truth: {ground_truth}")
        
        # Extract answer from <answer> tags
        answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
        match = re.search(answer_pattern, predict_str)
        if not match:
            # print("No <answer> tags found")
            return 0.0,None
            
        answer = match.group(1).strip()
        # print(f"Extracted answer: {answer}")
        
        # Parse answer string
        try:
            pred_obj = ast.literal_eval(answer)
            # print(f"Parsed pred_obj type: {type(pred_obj)}")
            # print(f"Parsed pred_obj: {pred_obj}")
        except Exception as e:
            # print(f"Error parsing answer: {e}")
            return 0.0,None
            
        pred_obj_transform = transform_actions(pred_obj)
        if not pred_obj_transform:
            # print("transform_actions returned empty result")
            return 0.0,None
        # print(f"pred_obj_transform: {pred_obj_transform}")
        result,error_desc = eval_single(pred_obj_transform, ground_truth)
        #print(f"eval_single result: {result}")
        if result:
            return 1.0,None
        #     ratio =  len(ground_truth['time_steps']) / len(pred_obj_transform)
        #     if ratio > 1.0:
                
        #         print(f"ratio: {ratio}  {ground_truth['task_id']}")
        #         # return ratio
        #         return 1.0
        #     return ratio
        else:
            return 0.0,error_desc
        
    except Exception as e:
        # print(f"Error in acc_reward: {e}")
        return 0.0,None

def compute_score(predict_str: str, ground_truth: List[Dict]):
    acc,error_desc=acc_reward(predict_str, ground_truth)
    return 0.1 * format_reward(predict_str) + 0.9 * acc , error_desc


if __name__ == "__main__":
    test=      {
    "task_id": "756_11-1",
    "task_description": "Look over the table; whichever of the bowl or plate is not already resting there, go get it and set it down.",
    "robots_set": {
      "R1": "unitree_h1"
    },
    "plan_answer": "[{\"step\": 1, \"actions\": {\"R1\": [\"Move\", \"plate\"]}}, {\"step\": 2, \"actions\": {\"R1\": [\"Reach\", \"plate\"]}}, {\"step\": 3, \"actions\": {\"R1\": [\"Grasp\", \"plate\"]}}, {\"step\": 4, \"actions\": {\"R1\": [\"Move\", \"table\"]}}, {\"step\": 5, \"actions\": {\"R1\": [\"Place\", \"table\"]}}]",
    "system_prompt": "You are a plan creator. I will provide you with an image of robots in a scene, available robots and their action primitives, and a task description. You need to create a plan to complete the task.\n1. Create a plan to complete the task, noting:\n   - Each robot can only perform ONE action per time step.\n   - Multiple robots can work in parallel, but each robot is limited to one action at a time.\n2. You need to first provide your reasoning process within <think> and </think> tags.\n3. Your final answer must be within <answer> and </answer> tags, and **strictly follow the JSON format specified below**.\n\nOutput Format Requirements(please comply strictly, do not output any additional content):\n<answer>\n  [\n    {\n      \"step\": 1,\n      \"actions\": {'R1': ['Move', 'pumpkin'], 'R2': ['Move', 'apple']}\n    },\n    {\n      \"step\": 2,\n      \"actions\": {'R1': ['Reach', 'pumpkin'], 'R2': ['Reach', 'apple']}\n    }\n    # ... subsequent steps ...\n  ]\n</answer>\nWhere:\n- step is the time step number (starting from 1, incrementing sequentially).\n- Each robot can only have ONE action per time step.\n- \"actions\" is a dictionary that specifies the action for each robot during a single time step. Each key (e.g., \"R1\", \"R2\") represents a robot. Each value is a list describing the single action that robot will perform in this step, with the following format: action_type, target_object_or_location, (optional: extra_argument)\nAction primitives and descriptions: {'Move': \"Command ['Move', 'object']: Robot R moves to the specified object.\", 'Open': \"Command ['Open', 'object']: Open the object held by the Robot R's end effector.\", 'Close': \"Command ['Close', 'object']: Close the object held by the Robot R's end effector.\", 'Reach': \"Command ['Reach', 'object']: Robot R reaches the specified object.\", 'Grasp': \"Command ['Grasp', 'object']: Robot R's end effector performs a grasping operation on a specified object.\", 'Place': \"Command ['Place', 'object']: Place the object held by the Robot R's end effector at a specified location (the release point, not the object itself).\", 'Push': \"Command ['Push', 'object', 'R1']: Robot R pushes the object to robot R1.\", 'Interact': \"Command ['Interact', 'object']: A general interaction operation, flexible for representing interactions with any asset.\"}\nAvailable robot set: {'R1': 'unitree_h1'}\nRobot characteristics: {'unitree_h1': 'A humanoid robot with arms and legs designed for human-like movements and tasks. Color: Black.'}\nTheir available operation APIs: {'unitree_h1': ['Move', 'Reach', 'Grasp', 'Place', 'Open', 'Close', 'Interact']}\n",
    "cot": "<think>\n1. **Analyze the Image**: The image shows a kitchen with a countertop and a table. On the countertop, there is a plate and a bowl. On the table, there is only a single object, which appears to be a cup or a small bowl.\n\n2. **Task Understanding**: The task is to identify which of the bowl or plate is not on the table and then place it there. From the image, the bowl is not on the table, as the object on the table is not a bowl.\n\n3. **Robot Capabilities**: The robot available is 'unitree_h1', which can perform actions like Move, Reach, Grasp, Place, etc. It is capable of human-like movements, which is suitable for this task.\n\n4. **Plan Development**:\n   - **Step 1**: Move the robot to the bowl on the countertop.\n   - **Step 2**: Reach for the bowl.\n   - **Step 3**: Grasp the bowl.\n   - **Step 4**: Move to the table.\n   - **Step 5**: Place the bowl on the table.\n\n5. **Final Plan**: The plan involves moving to the bowl, grasping it, and placing it on the table.\n</think>\n\n<answer>[{\"step\": 1, \"actions\": {\"R1\": [\"Move\", \"bowl\"]}}, {\"step\": 2, \"actions\": {\"R1\": [\"Reach\", \"bowl\"]}}, {\"step\": 3, \"actions\": {\"R1\": [\"Grasp\", \"bowl\"]}}, {\"step\": 4, \"actions\": {\"R1\": [\"Move\", \"table\"]}}, {\"step\": 5, \"actions\": {\"R1\": [\"Place\", \"table\"]}}]</answer>",
    "image_path": "merged_images/12384.png",
    "res": 0.1
  }
    predict_str = test['cot']
    ground_truth = {
            "description": "Observe the table for both the bowl and plate. Bring along whichever plate or bowl you don't detect.",
            "goal_constraints": [
                [
                    {
                        "is_satisfied": True,
                        "name": "bowl",
                        "status": {
                            "pos.name": "table"
                        },
                        "type": "asset"
                    }
                ],
                [
                    {
                        "is_satisfied": True,
                        "name": "plate",
                        "status": {
                            "pos.name": "table"
                        },
                        "type": "asset"
                    }
                ]
            ],
            "idle_robots": [],
            "init_pos": {
                "bowl_0": [
                    "table"
                ],
                "plate_1": [
                    "kitchen work area"
                ]
            },
            "layout_id": 6,
            "robots": {
                "R1": "unitree_h1"
            },
            "task_id": "1756_11-1",
            "task_name": "bring_plate_to_table_bowl_already_there",
            "temporal_constraints": [],
            "time_steps": [
                {
                    "step": 1,
                    "actions": {
                        "R1": [
                            "Move",
                            "plate"
                        ]
                    }
                },
                {
                    "step": 2,
                    "actions": {
                        "R1": [
                            "Reach",
                            "plate"
                        ]
                    }
                },
                {
                    "step": 3,
                    "actions": {
                        "R1": [
                            "Grasp",
                            "plate"
                        ]
                    }
                },
                {
                    "step": 4,
                    "actions": {
                        "R1": [
                            "Move",
                            "table"
                        ]
                    }
                },
                {
                    "step": 5,
                    "actions": {
                        "R1": [
                            "Place",
                            "table"
                        ]
                    }
                }
            ]
        }
    print(compute_score(predict_str, ground_truth))
    
    
   