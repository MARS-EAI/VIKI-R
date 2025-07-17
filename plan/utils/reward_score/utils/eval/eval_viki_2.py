import random
import argparse
import json
from utils.reward_score.utils.eval.eval import Eval
import random
CONTAINER_ASSETS = ['plate', 'cabinet', 'drawer', 'bowl', 'sink', 'toaster', 'tray', 'cardboardbox']

def eval_single(pred_obj: dict,ground_truth) -> bool:
    """
    Evaluate a single data dict and return True if successful, False otherwise.
    """
    judger = Eval()
    ground_truth = filter_none_values(ground_truth)
    # Unpack fields
    robots = ground_truth["robots"]
    #gt = ground_truth["ground_truth"]
    init_pos = ground_truth['init_pos']
    goal_constraints = ground_truth['goal_constraints']
    temporal_constraints = ground_truth['temporal_constraints']

    # Build metadata
    metadata = {"agents": {}, "assets": {}}
    for robot_id, robot_type in robots.items():
        metadata["agents"][robot_id] = {
            "type": robot_type,
            "pos": {"name": robot_id}
        }
    for asset_name, positions in init_pos.items():
        if asset_name.startswith('R') and asset_name[1:].isdigit():    # skip agent
            continue
        asset_type = asset_name.rsplit('_', 1)[0]
        chosen_pos = random.choice(positions)
        metadata["assets"][asset_type] = {"pos": {"name": chosen_pos}}
        if asset_type in CONTAINER_ASSETS:
            metadata["assets"][asset_type]["params"] = {
                "is_container": True,
                "position_kwargs": {
                    "name": asset_type,
                    "isolated": True if asset_type in ['cabinet'] else False
                }
            }

    # Attach constraints
    metadata['goal_constraints'] = goal_constraints
    metadata['temporal_constraints'] = temporal_constraints

    # Evaluate
    judger.set_env(metadata)
    answers = pred_obj
    success = judger.eval(answers)
    # if not success:
    #     print(judger.get_error_desc())
    return success

def filter_none_values(ground_truth):
    """
    Filter out None values from ground_truth dictionary and its nested structures.
    Keep all empty lists and empty dictionaries.
    
    Args:
        ground_truth: The input dictionary to process
        
    Returns:
        A new dictionary with all None values removed
    """
    if ground_truth is None:
        return None
        
    if isinstance(ground_truth, dict):
        filtered_ground_truth = {}
        for key, value in ground_truth.items():
            if value is None:
                continue
            if isinstance(value, (dict, list)):
                filtered_value = filter_none_values(value)
                if filtered_value is not None:  # Only add if the filtered value is not None
                    filtered_ground_truth[key] = filtered_value
            else:
                filtered_ground_truth[key] = value
        return filtered_ground_truth if filtered_ground_truth else {}
        
    elif isinstance(ground_truth, list):
        filtered_list = []
        for item in ground_truth:
            if item is None:
                continue
            if isinstance(item, (dict, list)):
                filtered_item = filter_none_values(item)
                if filtered_item is not None:  # Only add if the filtered item is not None
                    filtered_list.append(filtered_item)
            else:
                filtered_list.append(item)
        return filtered_list if filtered_list else []
        
    return ground_truth

def main():
    # Example prediction object
    pred_obj = [
        {'R1': '<Move,apple>'},
        {'R1': '<Reach,apple>'},
        {'R1': '<Grasp,apple>'},
        {'R1': '<Move,bowl>'},
        {'R1': '<Place,bowl>'}
    ]

    # Example ground truth
    ground_truth = {
        'description': 'Place the apple onto the bowl. Should it be missing, have a quick look inside the cabinet.',
        'goal_constraints': [[{
            'is_satisfied': True,
            'name': 'apple',
            'status': {'is_activated': None, 'pos.name': 'bowl'},
            'type': 'asset'
        }]],
        'idle_robots': ['anymal_c'],
        'init_pos': {
            'R1': None,
            'R2': None,
            'R3': None,
            'apple_0': ['kitchen work area', 'kitchen island area'],
            'apple_1': None,
            'bowl_2': ['kitchen island area', 'kitchen work area'],
            'cabinet_1': ['room_cabinet']
        },
        'layout_id': 4,
        'robots': {'R1': 'stompy', 'R2': None, 'R3': None},
        'task_id': '1367_10-2',
        'task_name': 'serve_bread_from_counter',
        'temporal_constraints': [],
        'time_steps': [
            {'actions': {'R1': ['Move', 'apple'], 'R2': None, 'R3': None}, 'step': 1},
            {'actions': {'R1': ['Reach', 'apple'], 'R2': None, 'R3': None}, 'step': 2},
            {'actions': {'R1': ['Grasp', 'apple'], 'R2': None, 'R3': None}, 'step': 3},
            {'actions': {'R1': ['Move', 'bowl'], 'R2': None, 'R3': None}, 'step': 4},
            {'actions': {'R1': ['Place', 'bowl'], 'R2': None, 'R3': None}, 'step': 5}
        ]
    }

    # Evaluate the prediction
    success = eval_single(pred_obj, ground_truth)
    print(f"Evaluation result: {'Success' if success else 'Failure'}")

if __name__ == "__main__":
    main()