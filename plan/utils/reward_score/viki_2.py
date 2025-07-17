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
# from mathruler.grader import extract_boxed_content, grade_answer  # Removed unused import
from typing import List, Dict
from utils.reward_score.utils.eval.eval_viki_2 import eval_single

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

def map_robot_keys(data, ground_truth=None):
    """
    Part 1: Replace robot names with IDs
    Map robot names to robot IDs (based on mapping relationship in ground_truth)
    
    Args:
        data: Original data containing robot names as keys
        ground_truth: Dictionary containing robot mapping information
    
    Returns:
        Processed data with robot names replaced by IDs
    """
    # Handle single step input
    if isinstance(data, list) and 'step' in data and 'actions' in data:
        data = [data]  # Convert single step to list format
    
    if not isinstance(data, list):
        return []
    
    # Create robot name mapping from ground_truth (case-insensitive)
    robot_mapping = {}
    if ground_truth and 'robots' in ground_truth:
        for robot_id, robot_type in ground_truth['robots'].items():
            if robot_type is not None:  # Skip None values
                robot_mapping[robot_type.lower()] = robot_id
        
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
                # Map robot name to robot ID if mapping exists (case-insensitive)
                mapped_robot = robot_mapping.get(robot.lower(), robot)
                step_actions[mapped_robot] = action_list  # Keep original action_list format
                
            if step_actions:  # Only append if we have actions for this step
                result.append({'step': step_info.get('step'), 'actions': step_actions})
                
    except Exception as e:
        return []
        
    return result

def format_actions(data):
    """
    Part 2: Format actions
    Convert action lists to <action1,action2> format and filter out None values
    
    Args:
        data: Data containing actions in list format
    
    Returns:
        Formatted data with actions converted to string format and None values filtered
    """
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
                # Skip None values
                if action_list is None:
                    continue
                    
                if isinstance(action_list, list):
                    step_actions[robot] = f'<{",".join(action_list)}>'
                else:
                    step_actions[robot] = action_list  # Keep as is if not a list
                
            if step_actions:  # Only append if we have actions for this step
                result.append(step_actions)
                
    except Exception as e:
        return []
        
    return result

def transform_actions(data, ground_truth=None):
    """
    Main function: Combine robot name mapping and action formatting
    
    Args:
        data: Original data
        ground_truth: Dictionary containing robot mapping information
    
    Returns:
        Fully processed data
    """
    # Step 1: Replace robot names with IDs
    mapped_data = map_robot_keys(data, ground_truth)
    
    # Step 2: Format actions
    formatted_data = format_actions(mapped_data)
    
    return formatted_data

def calculate_partial_score(pred_sequence, gt_sequence):
    """
    Calculate partial matching score with multiple evaluation dimensions
    
    Args:
        pred_sequence: Predicted sequence, e.g., [{'R1': '<Move,wine>'}, {'R1': '<Reach,wine>'}, ...]
        gt_sequence: Ground truth sequence, same format as above
    
    Returns:
        dict: Dictionary containing various scores
    """
    if not pred_sequence or not gt_sequence:
        return {
            'exact_match': 0.0,
            'step_match': 0.0, 
            'prefix_match': 0.0,
            'length_ratio': 0.0,
            'action_type_match': 0.0,
            'overall_partial': 0.0
        }
    
    # 1. Exact match score
    exact_match = 1.0 if pred_sequence == gt_sequence else 0.0
    
    # 2. Step match score - step by step comparison
    min_len = min(len(pred_sequence), len(gt_sequence))
    step_matches = 0
    for i in range(min_len):
        if pred_sequence[i] == gt_sequence[i]:
            step_matches += 1
    step_match_score = step_matches / max(len(pred_sequence), len(gt_sequence))
    
    # 3. Prefix match score - consecutive matches from the beginning
    prefix_matches = 0
    for i in range(min_len):
        if pred_sequence[i] == gt_sequence[i]:
            prefix_matches += 1
        else:
            break
    prefix_match_score = prefix_matches / len(gt_sequence)
    
    # 4. Length match score
    length_ratio = min(len(pred_sequence), len(gt_sequence)) / max(len(pred_sequence), len(gt_sequence))
    
    # 5. Action type match score - only consider action type, ignore target objects
    action_type_matches = 0
    for i in range(min_len):
        pred_actions = pred_sequence[i]
        gt_actions = gt_sequence[i]
        
        # 比较每个机器人的动作类型
        for robot in pred_actions:
            if robot in gt_actions:
                pred_action = pred_actions[robot]
                gt_action = gt_actions[robot]
                
                # 提取动作类型 (< 和第一个逗号之间的内容)
                pred_type = pred_action.split(',')[0].replace('<', '') if ',' in pred_action else pred_action.replace('<', '').replace('>', '')
                gt_type = gt_action.split(',')[0].replace('<', '') if ',' in gt_action else gt_action.replace('<', '').replace('>', '')
                
                if pred_type == gt_type:
                    action_type_matches += 1
                    break
    
    action_type_score = action_type_matches / len(gt_sequence)
    
    # 6. 综合部分分数 (加权平均)
    overall_partial = (
        0.4 * step_match_score +      # 40% 步骤匹配
        0.3 * prefix_match_score +    # 30% 前缀匹配  
        0.2 * action_type_score +     # 20% 动作类型匹配
        0.1 * length_ratio            # 10% 长度匹配
    )
    
    return {
        'exact_match': exact_match,
        'step_match': step_match_score,
        'prefix_match': prefix_match_score, 
        'length_ratio': length_ratio,
        'action_type_match': action_type_score,
        'overall_partial': overall_partial
    }

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
            pred_obj = ast.literal_eval(answer)
            # print(f"Parsed pred_obj type: {type(pred_obj)}")
            # print(f"Parsed pred_obj: {pred_obj}")
        except Exception as e:
            # print(f"Error parsing answer: {e}")
            return 0.0
            
        pred_obj_transform = transform_actions(pred_obj['action_plan'], ground_truth)
        #ground_truth['robots']
        if not pred_obj_transform:
            # print("transform_actions returned empty result")
            return 0.0
        # print(f"pred_obj_transform: {pred_obj_transform}")
        result = eval_single(pred_obj_transform, ground_truth)
        #print(f"eval_single result: {result}")
        if result:
            ratio =  len(ground_truth['time_steps']) / len(pred_obj_transform)
            if ratio >= 0.99:
            #return ratio
                return 1.0
            else:
                return 0.0
        else:
            return 0.0
        
    except Exception as e:
        # print(f"Error in acc_reward: {e}")
        return 0.0

def enhanced_acc_reward(predict_str: str, ground_truth: List[Dict], use_partial_score=True) -> float:
    """
    增强版准确度评分，支持部分匹配分数
    
    Args:
        predict_str: 预测字符串
        ground_truth: 真实标准答案
        use_partial_score: 是否使用部分匹配分数，False则使用原有的二元评分
    
    Returns:
        float: 评分结果
    """
    try:
        # 提取答案
        answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
        match = re.search(answer_pattern, predict_str)
        if not match:
            return 0.0
            
        answer = match.group(1).strip()
        
        # 解析答案
        try:
            pred_obj = ast.literal_eval(answer)
        except Exception as e:
            return 0.0
            
        # 转换预测序列
        pred_obj_transform = transform_actions(pred_obj['action_plan'], ground_truth)
        if not pred_obj_transform:
            return 0.0
        
        # 转换真实序列
        gt_sequence = format_actions(ground_truth['time_steps'])
        if not gt_sequence:
            return 0.0
        
        if use_partial_score:
            # 使用部分匹配评分
            scores = calculate_partial_score(pred_obj_transform, gt_sequence)
            
            # 如果完全匹配，返回1.0
            if scores['exact_match'] == 1.0:
                return 1.0
            
            # 否则返回部分分数
            return scores['overall_partial']
        else:
            # 使用原有的二元评分
            result = eval_single(pred_obj_transform, ground_truth)
            if result:
                ratio = len(ground_truth['time_steps']) / len(pred_obj_transform)
                return 1.0 if ratio >= 0.99 else 0.0
            else:
                return 0.0
        
    except Exception as e:
        return 0.0

def compute_score(predict_str: str, ground_truth: List[Dict], use_partial_score=True) -> float:
    """
    计算综合评分
    
    Args:
        predict_str: 预测字符串
        ground_truth: 真实标准答案
        use_partial_score: 是否使用部分匹配评分，默认False保持向后兼容
    
    Returns:
        float: 综合评分
    """
    robot_score = compare_robot_lists(predict_str, ground_truth)
    
    if use_partial_score:
        acc_score = enhanced_acc_reward(predict_str, ground_truth, use_partial_score=True)
    else:
        acc_score = acc_reward(predict_str, ground_truth)
    
    return 0.1 * robot_score + 0.9 * acc_score

 

def compare_robot_lists(predict_str,ground_truth):
    """
    简单比较机器人列表
    Args:
        ground_truth_robots: ground_truth['robots'] 字典，如 {'R1': 'fetch', 'R2': None, 'R3': None}
        predicted_robots: pred_obj['selected_robots'] 列表，如 ['Fetch']
    Returns:
        int: 一样返回1，不一样返回0
    """
    answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
    match = re.search(answer_pattern, predict_str)
    if not match:
        # print("No <answer> tags found")
        return 0.0
        
    answer = match.group(1).strip()
    # print(f"Extracted answer: {answer}")
    
    # Parse answer string
    try:
        pred_obj = ast.literal_eval(answer)
        # print(f"Parsed pred_obj type: {type(pred_obj)}")
        # print(f"Parsed pred_obj: {pred_obj}")
    except Exception as e:
        # print(f"Error parsing answer: {e}")
        return 0.0

    ground_truth_robots=ground_truth['robots']
    predicted_robots=pred_obj['selected_robots']
    print(f"Ground truth robots dict: {ground_truth_robots}")
    print(f"Predicted robots list: {predicted_robots}")
    
    # 1. 将 ground_truth['robots'] 转化为列表，去除 None
    gt_robot_list = []
    for robot_id, robot_type in ground_truth_robots.items():
        if robot_type is not None:
            gt_robot_list.append(robot_type)
    
    print(f"Ground truth robot types (non-None): {gt_robot_list}")
    
    # 2. 转换为小写进行比较（大小写不敏感）
    gt_robot_set = set(robot.lower() for robot in gt_robot_list)
    pred_robot_set = set(robot.lower() for robot in predicted_robots)
    
    print(f"Ground truth set (lowercase): {gt_robot_set}")
    print(f"Predicted set (lowercase): {pred_robot_set}")
    
    # 3. 比较两个集合是否相同
    is_same = gt_robot_set == pred_robot_set
    result = 1 if is_same else 0
    
    print(f"Sets are equal: {is_same}")
    print(f"Result: {result}")
    
    return result









def test_your_case():
    """测试您的具体案例"""
    print("=== 测试您的案例 ===")
    
    ground_truth_robots = {'R1': 'fetch', 'R2': None, 'R3': None}
    predicted_robots = ['Fetch']
    
    result = compare_robot_lists(ground_truth_robots, predicted_robots)
    
    print(f"\n总结:")
    if result == 1:
        print("🎉 机器人预测正确！")
    else:
        print("❌ 机器人预测错误")
    
    return result

def test_additional_cases():
    """测试更多案例"""
    print("\n=== 测试更多案例 ===")
    
    test_cases = [
        {
            'name': '多个机器人 - 正确',
            'ground_truth': {'R1': 'fetch', 'R2': 'mobile', 'R3': None},
            'predicted': ['Fetch', 'Mobile'],
            'expected': 1
        },
        {
            'name': '多个机器人 - 错误（缺少一个）',
            'ground_truth': {'R1': 'fetch', 'R2': 'mobile', 'R3': None},
            'predicted': ['Fetch'],
            'expected': 0
        },
        {
            'name': '多个机器人 - 错误（多了一个）',
            'ground_truth': {'R1': 'fetch', 'R2': None, 'R3': None},
            'predicted': ['Fetch', 'Mobile'],
            'expected': 0
        },
        {
            'name': '全部为None',
            'ground_truth': {'R1': None, 'R2': None, 'R3': None},
            'predicted': [],
            'expected': 1
        },
        {
            'name': '不同大小写组合',
            'ground_truth': {'R1': 'FETCH', 'R2': 'mobile', 'R3': None},
            'predicted': ['fetch', 'MOBILE'],
            'expected': 1
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- 测试案例 {i}: {case['name']} ---")
        result = compare_robot_lists(case['ground_truth'], case['predicted'])
        expected = case['expected']
        status = "✅ 通过" if result == expected else "❌ 失败"
        print(f"期望: {expected}, 实际: {result} - {status}")
    
    return True

def test_order_independence():
    """测试列表顺序是否影响结果"""
    print("\n=== 测试列表顺序是否影响结果 ===")
    
    # 基准数据
    base_ground_truth = {'R1': 'fetch', 'R2': 'mobile', 'R3': 'arm', 'R4': None}
    
    order_test_cases = [
        {
            'name': '顺序1：fetch, mobile, arm',
            'predicted': ['fetch', 'mobile', 'arm']
        },
        {
            'name': '顺序2：arm, fetch, mobile',
            'predicted': ['arm', 'fetch', 'mobile']
        },
        {
            'name': '顺序3：mobile, arm, fetch',
            'predicted': ['mobile', 'arm', 'fetch']
        },
        {
            'name': '顺序4：arm, mobile, fetch（大小写混合）',
            'predicted': ['ARM', 'Mobile', 'FETCH']
        }
    ]
    
    print(f"基准 ground_truth: {base_ground_truth}")
    print(f"从 ground_truth 提取的机器人类型: {[v for v in base_ground_truth.values() if v is not None]}")
    
    for i, case in enumerate(order_test_cases, 1):
        print(f"\n--- 顺序测试 {i}: {case['name']} ---")
        result = compare_robot_lists(base_ground_truth, case['predicted'])
        status = "✅ 正确" if result == 1 else "❌ 错误"
        print(f"预测列表: {case['predicted']}")
        print(f"结果: {result} - {status}")
    
    print(f"\n🔍 结论: 所有不同顺序的结果都应该是 1，因为使用了 set() 比较")
    return True

def test_partial_scoring():
    """
    测试部分评分系统
    """
    print("\n=== 测试部分评分系统 ===")
    
    # 示例真实序列
    gt_sequence = [
        {'R1': '<Move,wine>'}, 
        {'R1': '<Reach,wine>'}, 
        {'R1': '<Grasp,wine>'}, 
        {'R1': '<Move,kitchen work area>'}, 
        {'R1': '<Place,kitchen work area>'}
    ]
    
    # 测试案例
    test_cases = [
        {
            'name': '完全匹配',
            'pred_sequence': [
                {'R1': '<Move,wine>'}, 
                {'R1': '<Reach,wine>'}, 
                {'R1': '<Grasp,wine>'}, 
                {'R1': '<Move,kitchen work area>'}, 
                {'R1': '<Place,kitchen work area>'}
            ]
        },
        {
            'name': '前3步正确',
            'pred_sequence': [
                {'R1': '<Move,wine>'}, 
                {'R1': '<Reach,wine>'}, 
                {'R1': '<Grasp,wine>'}, 
                {'R1': '<Move,table>'}, 
                {'R1': '<Place,table>'}
            ]
        },
        {
            'name': '动作类型正确，目标物体错误',
            'pred_sequence': [
                {'R1': '<Move,apple>'}, 
                {'R1': '<Reach,apple>'}, 
                {'R1': '<Grasp,apple>'}, 
                {'R1': '<Move,table>'}, 
                {'R1': '<Place,table>'}
            ]
        },
        {
            'name': '序列过短',
            'pred_sequence': [
                {'R1': '<Move,wine>'}, 
                {'R1': '<Reach,wine>'}, 
                {'R1': '<Grasp,wine>'}
            ]
        },
        {
            'name': '序列过长',
            'pred_sequence': [
                {'R1': '<Move,wine>'}, 
                {'R1': '<Reach,wine>'}, 
                {'R1': '<Grasp,wine>'}, 
                {'R1': '<Move,kitchen work area>'}, 
                {'R1': '<Place,kitchen work area>'},
                {'R1': '<Move,table>'}, 
                {'R1': '<Place,table>'}
            ]
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- 测试案例 {i}: {case['name']} ---")
        scores = calculate_partial_score(case['pred_sequence'], gt_sequence)
        
        print(f"预测序列长度: {len(case['pred_sequence'])}")
        print(f"真实序列长度: {len(gt_sequence)}")
        print(f"完全匹配: {scores['exact_match']:.3f}")
        print(f"步骤匹配: {scores['step_match']:.3f}")
        print(f"前缀匹配: {scores['prefix_match']:.3f}")
        print(f"长度匹配: {scores['length_ratio']:.3f}")
        print(f"动作类型匹配: {scores['action_type_match']:.3f}")
        print(f"🎯 综合部分分数: {scores['overall_partial']:.3f}")
    
    print(f"\n📊 评分权重配置:")
    print(f"- 步骤匹配: 40%")
    print(f"- 前缀匹配: 30%")
    print(f"- 动作类型匹配: 20%")
    print(f"- 长度匹配: 10%")
    
    return True

def demo_partial_scoring_usage():
    """
    演示如何使用新的部分评分系统
    """
    print("\n=== 部分评分系统使用示例 ===")
    
    # 模拟一个预测结果（答案不完全正确）
    predict_str = """
    <think>
    我需要把酒移动到厨房工作区域。
    </think>
    
    <answer>
    {
        "selected_robots": ["unitree_h1"],
        "action_plan": [
            {"step": 1, "actions": {"R1": ["Move", "wine"]}},
            {"step": 2, "actions": {"R1": ["Reach", "wine"]}},
            {"step": 3, "actions": {"R1": ["Grasp", "wine"]}},
            {"step": 4, "actions": {"R1": ["Move", "table"]}},
            {"step": 5, "actions": {"R1": ["Place", "table"]}}
        ]
    }
    </answer>
    """
    
    # 模拟真实答案
    ground_truth = {
        'robots': {'R1': 'unitree_h1'},
        'time_steps': [
            {'step': 1, 'actions': {'R1': ['Move', 'wine']}},
            {'step': 2, 'actions': {'R1': ['Reach', 'wine']}},
            {'step': 3, 'actions': {'R1': ['Grasp', 'wine']}},
            {'step': 4, 'actions': {'R1': ['Move', 'kitchen work area']}},
            {'step': 5, 'actions': {'R1': ['Place', 'kitchen work area']}}
        ]
    }
    
    print("预测序列（目标位置错误）:")
    print("- Step 4: Move to 'table' (应该是 'kitchen work area')")
    print("- Step 5: Place at 'table' (应该是 'kitchen work area')")
    
    # 比较两种评分系统
    original_score = compute_score(predict_str, ground_truth, use_partial_score=False)
    partial_score = compute_score(predict_str, ground_truth, use_partial_score=True)
    
    print(f"\n📊 评分对比:")
    print(f"原始评分系统 (二元评分): {original_score:.3f}")
    print(f"部分评分系统 (连续评分): {partial_score:.3f}")
    
    # 详细分析
    print(f"\n🔍 详细分析:")
    
    # 获取详细的部分评分信息
    pred_sequence = transform_actions([
        {"step": 1, "actions": {"R1": ["Move", "wine"]}},
        {"step": 2, "actions": {"R1": ["Reach", "wine"]}},
        {"step": 3, "actions": {"R1": ["Grasp", "wine"]}},
        {"step": 4, "actions": {"R1": ["Move", "table"]}},
        {"step": 5, "actions": {"R1": ["Place", "table"]}}
    ], ground_truth)
    
    gt_sequence = format_actions(ground_truth['time_steps'])
    
    scores = calculate_partial_score(pred_sequence, gt_sequence)
    
    print(f"- 完全匹配: {scores['exact_match']:.3f}")
    print(f"- 步骤匹配: {scores['step_match']:.3f} (前3步正确)")
    print(f"- 前缀匹配: {scores['prefix_match']:.3f} (连续3步正确)")
    print(f"- 动作类型匹配: {scores['action_type_match']:.3f} (动作类型都正确)")
    print(f"- 长度匹配: {scores['length_ratio']:.3f} (长度相同)")
    print(f"- 🎯 综合部分分数: {scores['overall_partial']:.3f}")
    
    print(f"\n💡 结论:")
    print(f"- 原始系统: 因为不完全匹配，得分为 {original_score:.3f}")
    print(f"- 部分评分系统: 考虑到前3步正确且动作类型都对，得分为 {partial_score:.3f}")
    print(f"- 部分评分系统能更好地反映答案的质量!")
    
    return True

def analyze_sequence_comparison():
    """
    分析用户提供的两个序列的判断流程
    """
    print("\n=== 序列比较分析 ===")
    
    # 用户提供的两个序列
    pred_sequence = [
        {'R1': '<Move,tomato>'}, 
        {'R1': '<Reach,tomato>'}, 
        {'R1': '<Grasp,tomato>'}, 
        {'R1': '<Move,sink>'}, 
        {'R1': '<Place,sink>'}, 
        {'R1': '<Interact,sink>'}, 
        {'R1': '<Move,tomato>'}, 
        {'R1': '<Reach,tomato>'}, 
        {'R1': '<Grasp,tomato>'}, 
        {'R1': '<Move,plate>'}, 
        {'R1': '<Place,plate>'}
    ]
    
    gt_sequence = [
        {'R1': '<Move,tomato>'}, 
        {'R1': '<Reach,tomato>'}, 
        {'R1': '<Grasp,tomato>'}, 
        {'R1': '<Move,sink>'}, 
        {'R1': '<Open,tap>'}, 
        {'R1': '<Interact,tomato>'}, 
        {'R1': '<Close,tap>'}, 
        {'R1': '<Move,plate>'}, 
        {'R1': '<Place,tomato>'}
    ]
    
    print("📋 序列信息:")
    print(f"预测序列长度: {len(pred_sequence)} 步")
    print(f"真实序列长度: {len(gt_sequence)} 步")
    
    # 显示两个序列的对比
    print("\n🔍 逐步对比:")
    max_len = max(len(pred_sequence), len(gt_sequence))
    
    for i in range(max_len):
        pred_step = pred_sequence[i] if i < len(pred_sequence) else "N/A"
        gt_step = gt_sequence[i] if i < len(gt_sequence) else "N/A"
        
        match_status = "✅" if pred_step == gt_step else "❌"
        
        print(f"步骤 {i+1:2d}: {match_status}")
        print(f"  预测: {pred_step}")
        print(f"  真实: {gt_step}")
        
        if pred_step != "N/A" and gt_step != "N/A" and pred_step != gt_step:
            # 分析动作类型是否匹配
            if isinstance(pred_step, dict) and isinstance(gt_step, dict):
                pred_action = list(pred_step.values())[0]
                gt_action = list(gt_step.values())[0]
                
                pred_type = pred_action.split(',')[0].replace('<', '') if ',' in pred_action else pred_action.replace('<', '').replace('>', '')
                gt_type = gt_action.split(',')[0].replace('<', '') if ',' in gt_action else gt_action.replace('<', '').replace('>', '')
                
                if pred_type == gt_type:
                    print(f"    💡 动作类型匹配: {pred_type}")
                else:
                    print(f"    🔄 动作类型不匹配: {pred_type} vs {gt_type}")
        print()
    
    # 计算详细的部分评分
    print("📊 详细评分分析:")
    scores = calculate_partial_score(pred_sequence, gt_sequence)
    
    print(f"1. 完全匹配: {scores['exact_match']:.3f}")
    print(f"   - 序列是否完全相同: {'是' if scores['exact_match'] == 1.0 else '否'}")
    
    print(f"\n2. 步骤匹配: {scores['step_match']:.3f}")
    step_matches = 0
    min_len = min(len(pred_sequence), len(gt_sequence))
    for i in range(min_len):
        if pred_sequence[i] == gt_sequence[i]:
            step_matches += 1
    print(f"   - 匹配步骤数: {step_matches}/{max(len(pred_sequence), len(gt_sequence))}")
    
    print(f"\n3. 前缀匹配: {scores['prefix_match']:.3f}")
    prefix_matches = 0
    for i in range(min_len):
        if pred_sequence[i] == gt_sequence[i]:
            prefix_matches += 1
        else:
            break
    print(f"   - 连续匹配步骤数: {prefix_matches}/{len(gt_sequence)}")
    
    print(f"\n4. 长度匹配: {scores['length_ratio']:.3f}")
    print(f"   - 长度比例: {min_len}/{max(len(pred_sequence), len(gt_sequence))}")
    
    print(f"\n5. 动作类型匹配: {scores['action_type_match']:.3f}")
    action_type_matches = 0
    for i in range(min_len):
        pred_actions = pred_sequence[i]
        gt_actions = gt_sequence[i]
        
        for robot in pred_actions:
            if robot in gt_actions:
                pred_action = pred_actions[robot]
                gt_action = gt_actions[robot]
                
                pred_type = pred_action.split(',')[0].replace('<', '') if ',' in pred_action else pred_action.replace('<', '').replace('>', '')
                gt_type = gt_action.split(',')[0].replace('<', '') if ',' in gt_action else gt_action.replace('<', '').replace('>', '')
                
                if pred_type == gt_type:
                    action_type_matches += 1
                    break
    
    print(f"   - 动作类型匹配步骤数: {action_type_matches}/{len(gt_sequence)}")
    
    print(f"\n🎯 综合部分分数: {scores['overall_partial']:.3f}")
    print(f"   - 权重配置:")
    print(f"     • 步骤匹配 (40%): {scores['step_match']:.3f} × 0.4 = {scores['step_match'] * 0.4:.3f}")
    print(f"     • 前缀匹配 (30%): {scores['prefix_match']:.3f} × 0.3 = {scores['prefix_match'] * 0.3:.3f}")
    print(f"     • 动作类型匹配 (20%): {scores['action_type_match']:.3f} × 0.2 = {scores['action_type_match'] * 0.2:.3f}")
    print(f"     • 长度匹配 (10%): {scores['length_ratio']:.3f} × 0.1 = {scores['length_ratio'] * 0.1:.3f}")
    print(f"     • 总分: {scores['overall_partial']:.3f}")
    
    # 分析主要差异
    print(f"\n📝 主要差异分析:")
    print(f"1. 前4步完全匹配 (Move,tomato → Reach,tomato → Grasp,tomato → Move,sink)")
    print(f"2. 从第5步开始出现分歧:")
    print(f"   - 预测: Place,sink → Interact,sink → Move,tomato → Reach,tomato → Grasp,tomato → Move,plate → Place,plate")
    print(f"   - 真实: Open,tap → Interact,tomato → Close,tap → Move,plate → Place,tomato")
    print(f"3. 长度差异: 预测11步 vs 真实9步")
    print(f"4. 任务理解差异:")
    print(f"   - 预测序列: 似乎是先洗番茄，再拿另一个番茄放到盘子上")
    print(f"   - 真实序列: 洗番茄后直接把洗好的番茄放到盘子上")
    
    return scores

def analyze_multi_robot_sequence():
    """
    分析多机器人协作序列的判断流程
    """
    print("\n=== 多机器人协作序列分析 ===")
    
    # 用户提供的两个多机器人序列
    pred_sequence = [
        {'R1': '<Reach,pear>', 'R2': '<Move,cardboardbox>'}, 
        {'R1': '<Grasp,pear>', 'R2': '<Push,cardboardbox,R1>'}, 
        {'R1': '<Place,cardboardbox>'}, 
        {'R2': '<Push,cardboardbox,R3>'}, 
        {'R3': '<Reach,pear>'}, 
        {'R3': '<Grasp,pear>'}, 
        {'R3': '<Place,sink>'}
    ]
    
    gt_sequence = [
        {'R3': '<Reach,pear>'}, 
        {'R3': '<Grasp,pear>'}, 
        {'R3': '<Place,cardboardbox>'}, 
        {'Fetch': '<Move,cardboardbox>'}, 
        {'Fetch': '<Place,sink>'}, 
        {'R3': '<Reach,pear>'}, 
        {'R3': '<Grasp,pear>'}, 
        {'R3': '<Place,sink>'}
    ]
    
    print("📋 序列信息:")
    print(f"预测序列长度: {len(pred_sequence)} 步")
    print(f"真实序列长度: {len(gt_sequence)} 步")
    
    # 分析机器人分布
    pred_robots = set()
    gt_robots = set()
    
    for step in pred_sequence:
        pred_robots.update(step.keys())
    for step in gt_sequence:
        gt_robots.update(step.keys())
    
    print(f"预测序列涉及机器人: {sorted(pred_robots)}")
    print(f"真实序列涉及机器人: {sorted(gt_robots)}")
    
    # 显示两个序列的对比
    print("\n🔍 逐步对比:")
    max_len = max(len(pred_sequence), len(gt_sequence))
    
    for i in range(max_len):
        pred_step = pred_sequence[i] if i < len(pred_sequence) else {}
        gt_step = gt_sequence[i] if i < len(gt_sequence) else {}
        
        match_status = "✅" if pred_step == gt_step else "❌"
        
        print(f"步骤 {i+1:2d}: {match_status}")
        print(f"  预测: {pred_step}")
        print(f"  真实: {gt_step}")
        
        if pred_step != gt_step and pred_step and gt_step:
            # 分析动作类型匹配和机器人匹配
            pred_actions = []
            gt_actions = []
            
            for robot, action in pred_step.items():
                action_type = action.split(',')[0].replace('<', '') if ',' in action else action.replace('<', '').replace('>', '')
                pred_actions.append(f"{robot}:{action_type}")
            
            for robot, action in gt_step.items():
                action_type = action.split(',')[0].replace('<', '') if ',' in action else action.replace('<', '').replace('>', '')
                gt_actions.append(f"{robot}:{action_type}")
            
            print(f"    预测动作类型: {pred_actions}")
            print(f"    真实动作类型: {gt_actions}")
            
            # 检查是否有相同的动作类型
            pred_types = [action.split(':')[1] for action in pred_actions]
            gt_types = [action.split(':')[1] for action in gt_actions]
            common_types = set(pred_types) & set(gt_types)
            
            if common_types:
                print(f"    💡 共同动作类型: {common_types}")
        print()
    
    # 计算详细的部分评分
    print("📊 详细评分分析:")
    scores = calculate_partial_score(pred_sequence, gt_sequence)
    
    print(f"1. 完全匹配: {scores['exact_match']:.3f}")
    print(f"   - 序列是否完全相同: {'是' if scores['exact_match'] == 1.0 else '否'}")
    
    print(f"\n2. 步骤匹配: {scores['step_match']:.3f}")
    step_matches = 0
    min_len = min(len(pred_sequence), len(gt_sequence))
    for i in range(min_len):
        if pred_sequence[i] == gt_sequence[i]:
            step_matches += 1
    print(f"   - 完全匹配步骤数: {step_matches}/{max(len(pred_sequence), len(gt_sequence))}")
    
    print(f"\n3. 前缀匹配: {scores['prefix_match']:.3f}")
    prefix_matches = 0
    for i in range(min_len):
        if pred_sequence[i] == gt_sequence[i]:
            prefix_matches += 1
        else:
            break
    print(f"   - 连续匹配步骤数: {prefix_matches}/{len(gt_sequence)}")
    
    print(f"\n4. 长度匹配: {scores['length_ratio']:.3f}")
    print(f"   - 长度比例: {min_len}/{max(len(pred_sequence), len(gt_sequence))}")
    
    print(f"\n5. 动作类型匹配: {scores['action_type_match']:.3f}")
    
    # 手动计算动作类型匹配，考虑多机器人情况
    action_type_matches = 0
    for i in range(min_len):
        pred_actions = pred_sequence[i]
        gt_actions = gt_sequence[i]
        
        # 提取所有动作类型
        pred_types = []
        gt_types = []
        
        for robot, action in pred_actions.items():
            action_type = action.split(',')[0].replace('<', '') if ',' in action else action.replace('<', '').replace('>', '')
            pred_types.append(action_type)
        
        for robot, action in gt_actions.items():
            action_type = action.split(',')[0].replace('<', '') if ',' in action else action.replace('<', '').replace('>', '')
            gt_types.append(action_type)
        
        # 检查是否有相同的动作类型
        if set(pred_types) & set(gt_types):
            action_type_matches += 1
    
    manual_action_type_score = action_type_matches / len(gt_sequence)
    print(f"   - 动作类型匹配步骤数: {action_type_matches}/{len(gt_sequence)}")
    print(f"   - 手动计算的动作类型匹配分数: {manual_action_type_score:.3f}")
    
    print(f"\n🎯 综合部分分数: {scores['overall_partial']:.3f}")
    print(f"   - 权重配置:")
    print(f"     • 步骤匹配 (40%): {scores['step_match']:.3f} × 0.4 = {scores['step_match'] * 0.4:.3f}")
    print(f"     • 前缀匹配 (30%): {scores['prefix_match']:.3f} × 0.3 = {scores['prefix_match'] * 0.3:.3f}")
    print(f"     • 动作类型匹配 (20%): {scores['action_type_match']:.3f} × 0.2 = {scores['action_type_match'] * 0.2:.3f}")
    print(f"     • 长度匹配 (10%): {scores['length_ratio']:.3f} × 0.1 = {scores['length_ratio'] * 0.1:.3f}")
    print(f"     • 总分: {scores['overall_partial']:.3f}")
    
    # 分析协作模式差异
    print(f"\n📝 协作模式差异分析:")
    
    print(f"预测序列的协作模式:")
    print(f"  1. R1和R2并行工作：R1抓梨，R2移动纸箱")
    print(f"  2. R1和R2协作：R1抓梨，R2推纸箱给R1")
    print(f"  3. R1独立工作：放梨到纸箱")
    print(f"  4. R2独立工作：推纸箱给R3")
    print(f"  5. R3独立工作：抓梨并放到水槽")
    
    print(f"\n真实序列的协作模式:")
    print(f"  1. R3独立工作：抓梨并放到纸箱")
    print(f"  2. Fetch独立工作：移动纸箱并放到水槽")
    print(f"  3. R3独立工作：再抓梨并放到水槽")
    
    print(f"\n🔍 关键差异:")
    print(f"  1. 机器人分工：预测用R1/R2/R3三个机器人，真实用R3/Fetch两个机器人")
    print(f"  2. 协作复杂度：预测有更多的机器人间传递，真实更简单直接")
    print(f"  3. 任务完成方式：预测是分步传递，真实是批量处理")
    print(f"  4. 效率：两个序列都是7步，长度相同")
    
    # 分析动作类型分布
    print(f"\n📈 动作类型分布:")
    
    pred_action_counts = {}
    gt_action_counts = {}
    
    for step in pred_sequence:
        for robot, action in step.items():
            action_type = action.split(',')[0].replace('<', '') if ',' in action else action.replace('<', '').replace('>', '')
            pred_action_counts[action_type] = pred_action_counts.get(action_type, 0) + 1
    
    for step in gt_sequence:
        for robot, action in step.items():
            action_type = action.split(',')[0].replace('<', '') if ',' in action else action.replace('<', '').replace('>', '')
            gt_action_counts[action_type] = gt_action_counts.get(action_type, 0) + 1
    
    print(f"预测动作类型统计: {pred_action_counts}")
    print(f"真实动作类型统计: {gt_action_counts}")
    
    return scores

if __name__ == "__main__":
    # 运行机器人映射测试
    print("=== 测试机器人名称映射功能 ===")
    test_robot_mapping()
    
    # 运行详细的大小写不敏感测试
    test_case_insensitive_mapping()
    
    # 测试您的具体案例
    test_your_case()
    
    # 测试更多案例
    test_additional_cases()
    
    # 测试列表顺序是否影响结果
    test_order_independence()
    
    # 测试部分评分系统
    test_partial_scoring()
    
    print("\n=== 运行原有测试 ===")
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
    print(f"原始评分系统: {compute_score(predict_str, ground_truth):.3f}")
    print(f"部分评分系统: {compute_score(predict_str, ground_truth, use_partial_score=True):.3f}")
    
    # 展示详细的部分评分信息
    print("\n=== 详细部分评分分析 ===")
    enhanced_score = enhanced_acc_reward(predict_str, ground_truth, use_partial_score=True)
    print(f"增强版准确度评分: {enhanced_score:.3f}")
    
    # 演示部分评分系统使用示例
    demo_partial_scoring_usage()
    
    # 分析用户提供的两个序列的判断流程
    analyze_sequence_comparison()
    
    # 分析多机器人协作序列
    analyze_multi_robot_sequence()
   