import random
import argparse
import json
from verl.utils.reward_score.utils.eval.eval import Eval
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
        asset_type = asset_name.rsplit('_', 1)[0]
        chosen_pos = random.choice(positions)
        metadata["assets"][asset_type] = {"pos": {"name": chosen_pos}}
        if asset_type in CONTAINER_ASSETS:
            metadata["assets"][asset_type]["params"] = {
                "is_container": True,
                "position_kwargs": {
                    "name": asset_type,
                    "isolated": asset_type == 'cabinet'
                }
            }

    # Attach constraints
    metadata['goal_constraints'] = goal_constraints
    metadata['temporal_constraints'] = temporal_constraints

    # Evaluate
    judger.set_env(metadata)
    answers = pred_obj
    success = judger.eval(answers)
    if not success:
        print(judger.get_error_desc())
    return success

def filter_none_values(ground_truth):
    """
    Filter out None values from ground_truth dictionary and its nested structures.
    Keep all empty lists.
    """
    filtered_ground_truth = {}
    for key, value in ground_truth.items():
        if value is None:
            continue
        if isinstance(value, dict):
            filtered_value = filter_none_values(value)
            filtered_ground_truth[key] = filtered_value
        elif isinstance(value, list):
            filtered_list = []
            for item in value:
                if item is None:
                    continue
                if isinstance(item, dict):
                    filtered_item = filter_none_values(item)
                    filtered_list.append(filtered_item)
                else:
                    filtered_list.append(item)
            filtered_ground_truth[key] = filtered_list
        else:
            filtered_ground_truth[key] = value
    return filtered_ground_truth

def main():
    # Example prediction object
    pred_obj = [
        {'R1': '<Move,spoon>', 'R2': '<Move,tomato>'},
        {'R1': '<Reach,spoon>', 'R2': '<Reach,tomato>'},
        {'R1': '<Grasp,spoon>', 'R2': '<Grasp,tomato>'},
        {'R1': '<Move,cabinet>', 'R2': '<Move,cabinet>'},
        {'R1': '<Open,cabinet>'},
        {'R1': '<Place,cabinet>', 'R2': '<Place,cabinet>'}
    ]

    # Example ground truth
    ground_truth = {
        'description': 'Put the tomato and the spoon into the cabinet to clean up the workspace.',
        'goal_constraints': [
            [{'is_satisfied': True, 'name': 'tomato', 'status': {'pos.name': 'cabinet'}, 'type': 'asset'}],
            [{'is_satisfied': True, 'name': 'spoon', 'status': {'pos.name': 'cabinet'}, 'type': 'asset'}]
        ],
        'ground_truth': [
            {'R1': ['Move', 'tomato'], 'R2': ['Move', 'spoon']},
            {'R1': ['Reach', 'tomato'], 'R2': ['Reach', 'spoon']},
            {'R1': ['Grasp', 'tomato'], 'R2': ['Grasp', 'spoon']},
            {'R1': ['Move', 'cabinet'], 'R2': ['Move', 'cabinet']},
            {'R1': ['Open', 'cabinet'], 'R2': None},
            {'R1': ['Place', 'cabinet'], 'R2': ['Place', 'cabinet']}
        ],
        'idle_robots': ['anymal_c', 'panda'],
        'init_pos': {
            'apple_0': None,
            'apple_1': None,
            'banana_0': None,
            'bowl_0': None,
            'bowl_1': None,
            'bowl_2': None,
            'bread_0': None,
            'cabinet_1': None,
            'cabinet_2': ['room_cabinet'],
            'fork_1': None,
            'plate_0': None,
            'plate_1': None,
            'pumpkin_1': None,
            'sink_1': None,
            'spoon_1': ['kitchen work area', 'kitchen island area'],
            'tomato_0': ['kitchen work area', 'kitchen island area']
        },
        'layout_id': 4,
        'robots': {'R1': 'unitree_h1', 'R2': 'fetch'},
        'task_id': '67_5-1',
        'task_name': 'clear_table_with_two_robots_and_put_in_cabinet',
        'temporal_constraints': []
    }

    # Evaluate the prediction
    success = eval_single(pred_obj, ground_truth)
    print(f"Evaluation result: {'Success' if success else 'Failure'}")

if __name__ == "__main__":
    main()