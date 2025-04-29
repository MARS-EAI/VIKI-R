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
from utils.eval.eval_viki_2 import eval_single

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
    # print(f"transform_actions input type: {type(data)}")
    # print(f"transform_actions input data: {data}")
    
    if isinstance(data, str):
        try:
            data = ast.literal_eval(data.replace('{{', '{').replace('}}', '}'))
            # print(f"After parsing string: {type(data)} - {data}")
        except Exception as e:
            # print(f"Error parsing string in transform_actions: {e}")
            return []
    
    # Handle single step input
    if isinstance(data, dict) and 'step' in data and 'actions' in data:
        data = [data]  # Convert single step to list format
    
    if not isinstance(data, list):
        # print(f"Data is not a list after parsing: {type(data)}")
        return []
        
    result = []
    try:
        for step_info in data:
            if not isinstance(step_info, dict):
                # print(f"Step info is not a dict: {type(step_info)} - {step_info}")
                continue
                
            step_actions = {}
            actions = step_info.get('actions', [])
            if isinstance(actions, list):
                for action in actions:
                    if not isinstance(action, dict):
                        # print(f"Action is not a dict: {type(action)} - {action}")
                        continue
                        
                    robot = action.get('robot')
                    action_type = action.get('action')
                    obj = action.get('object')
                    
                    if all([robot, action_type, obj]):
                        step_actions[robot] = f"<{action_type},{obj}>"
                    else:
                        # print(f"Missing required fields in action: {action}")
                        pass
                        
            if step_actions:
                result.append(step_actions)
    except Exception as e:
        # print(f"Error in transform_actions loop: {e}")
        return []
        
    # print(f"transform_actions result: {result}")
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
            return 0.0
            
        answer = match.group(1).strip()
        # print(f"Extracted answer: {answer}")
        
        # Parse answer string
        try:
            pred_obj = ast.literal_eval(answer.replace('{{', '{').replace('}}', '}'))
            # print(f"Parsed pred_obj type: {type(pred_obj)}")
            # print(f"Parsed pred_obj: {pred_obj}")
        except Exception as e:
            # print(f"Error parsing answer: {e}")
            return 0.0
            
        pred_obj_transform = transform_actions(pred_obj)
        if not pred_obj_transform:
            # print("transform_actions returned empty result")
            return 0.0
        # print(f"pred_obj_transform: {pred_obj_transform}")
        result = eval_single(pred_obj_transform, ground_truth)
        #print(f"eval_single result: {result}")
        return 1.0 if result else 0.0
        
    except Exception as e:
        # print(f"Error in acc_reward: {e}")
        return 0.0

def compute_score(predict_str: str, ground_truth: List[Dict]) -> float:
    return 0.9 * acc_reward(predict_str, ground_truth) + 0.1 * format_reward(predict_str)
