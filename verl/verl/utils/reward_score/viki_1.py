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
from mathruler.grader import extract_boxed_content, grade_answer


def format_reward(predict_str: str) -> float:
    # Check overall structure with <think> and <answer> tags
    structure_pattern = re.compile(r'<think>.*</think>.*<answer>.*</answer>.*', re.DOTALL)
    structure_match = re.fullmatch(structure_pattern, predict_str)
    
    if not structure_match:
        return 0.0
    
    # Check if answer is in Python list format
    answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
    answer_match = re.search(answer_pattern, predict_str)
    
    if not answer_match:
        return 0.0
    
    answer_content = answer_match.group(1).strip()
    list_pattern = re.compile(r'\[.*\]', re.DOTALL)
    list_match = re.fullmatch(list_pattern, answer_content)
    
    return 1.0 if list_match else 0.0


def acc_reward(predict_str: str, ground_truth: str) -> float:
    # Extract answer from <answer> tags
    answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
    match = re.search(answer_pattern, predict_str)
    answer = match.group(1).strip() if match else ""
    
    try:
        # Parse both strings as Python lists
        pred_list = ast.literal_eval(answer)
        gt_list = ast.literal_eval(ground_truth)

        if isinstance(pred_list, list) and isinstance(gt_list, list):
            # Try hashing via tuple conversion (handle list of lists)
            pred_set = set(tuple(x) if isinstance(x, list) else x for x in pred_list)
            gt_set = set(tuple(x) if isinstance(x, list) else x for x in gt_list)
            return 1.0 if pred_set == gt_set else 0.0
    except (ValueError, SyntaxError, TypeError):
        pass
    
    # Fall back to original comparison if paarsing fails
    return 1.0 if grade_answer(answer, str(ground_truth)) else 0.0



def compute_score(predict_str: str, ground_truth: str) -> float:
    return 0.9 * acc_reward(predict_str, ground_truth) + 0.1 * format_reward(predict_str)
