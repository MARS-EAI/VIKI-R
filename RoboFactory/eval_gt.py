import argparse
import json
from utils.eval.eval import Eval


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', type=str, default='script_general/output.json', help='data for eval')
    return parser.parse_args()


def eval(data: list):
    for d in data:
        robots = d["robots"]
        gt = d["ground_truth"]
        prediction = gt    # currently use the same gt


if __name__ == '__main__':
    args = parse_args()
    data = json.load(open(args.data, 'r'))
    print(f'Eval {len(data)} data.')
    eval(data)
    