import argparse
import json
from utils.eval.eval import Eval
import random

CONTAINER_ASSETS = ['plate', 'cabinet', 'drawer', 'bowl', 'sink', 'toaster', 'tray']
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', type=str, default='script_general/gt_test.json', help='data for eval')
    return parser.parse_args()


def format_answer(answer):
    commands = []
    for inst in answer:
        formatted_inst = {}
        for robob_name, robot_inst in inst.items():
            formatted_inst[robob_name] = f'<{",".join(robot_inst)}>'
        commands.append(formatted_inst)
    return commands


def eval(data: list):
    judger = Eval()
    success_count = 0
    for idx, d in enumerate(data):
        # d = {'task_id': '2-1_993', 'task_name': 'parallel_human_dual_asset_to_plate_or_bowl', 'layout_id': 8, 'description': 'Carry the pear along with the tomato and place them into the bowl.', 'robots': {'R1': 'fetch', 'R2': 'unitree_h1'}, 'ground_truth': [{'R2': ['Move', 'pear'], 'R1': ['Move', 'tomato']}, {'R2': ['Reach', 'pear'], 'R1': ['Reach', 'tomato']}, {'R2': ['Grasp', 'pear'], 'R1': ['Grasp', 'tomato']}, {'R2': ['Move', 'bowl'], 'R1': ['Move', 'bowl']}, {'R2': ['Place', 'bowl'], 'R1': ['Place', 'bowl']}], 'init_pos': {'pear_0': ['kitchen work area', 'kitchen island area'], 'tomato_1': ['kitchen work area', 'kitchen island area'], 'bowl_2': ['kitchen work area', 'kitchen island area']}, 'idle_robots': [], 'constraints': [[[{'type': 'asset', 'name': 'pear', 'is_satisfied': True, 'status': {'pos.name': 'bowl'}}]], [[{'type': 'asset', 'name': 'tomato', 'is_satisfied': True, 'status': {'pos.name': 'bowl'}}]]]}
        robots = d["robots"]
        gt = d["ground_truth"]
        init_pos = d['init_pos']
        constraints = d['constraints']
        
        default_metadata = {
            "agents": {

            },
            "assets": {

            }
        }
        for robot_id, robot_type in robots.items():
            default_metadata["agents"][robot_id] = {
                "type": robot_type,
                "pos": {
                    "name": robot_id,
                }
            }
        for asset_name, asset_pos in init_pos.items():
            asset_type = asset_name.rsplit('_', maxsplit=1)[0]
            default_metadata["assets"][asset_type] = {
                "pos": {
                    "name": random.choice(asset_pos)
                },
            }
            if asset_type in CONTAINER_ASSETS:
                default_metadata["assets"][asset_type]['params'] = {
                    "is_container": True,
                    "position_kwargs": {
                        "name": asset_type,
                        "isolated": True if asset_type in ['cabinet'] else False
                    }
                }

        default_metadata['constraints'] = constraints
        judger.set_env(default_metadata)
        answers = format_answer(gt)
        # print(answers)
        success = judger.eval(answers)
        # success = judger.eval([{
        #     'R1': '<move, bread>'
        # }])
        if not success:
            print(f'{idx}: {judger.get_error_desc()}')
        else:
            success_count += 1
        # break
    print(f'Success Count: {success_count}')


if __name__ == '__main__':
    args = parse_args()
    data = json.load(open(args.data, 'r'))
    print(f'Eval {len(data)} data.')
    eval(data)
    