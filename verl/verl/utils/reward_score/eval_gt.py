import argparse
import json
from verl.utils.reward_score.utils.eval.eval import Eval
import random

CONTAINER_ASSETS = ['plate', 'cabinet', 'drawer', 'bowl', 'sink', 'toaster', 'tray']
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', type=str, default='RoboViki-R/RoboFactory/script_general/output.json', help='data for eval')
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
        # d = data[954]
        robots = d["robots"]
        gt = d["ground_truth"]
        init_pos = d['init_pos']
        goal_constraints = d['goal_constraints']
        temporal_constraints = d['temporal_constraints']

        # skip test data

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

        default_metadata['goal_constraints'] = goal_constraints
        default_metadata['temporal_constraints'] = temporal_constraints
        judger.set_env(default_metadata)
        answers = format_answer(gt)
        # print(answers)
        success = judger.eval(answers)
        if not success:
            print(f'{idx}: {judger.get_error_desc()}')
        else:
            success_count += 1

        # break
    print(f'Success Count: {success_count}. Failed Count: {len(data) - success_count}.')


if __name__ == '__main__':
    args = parse_args()
    data = json.load(open(args.data, 'r'))
    print(f'Eval {len(data)} data.')
    eval(data)
    