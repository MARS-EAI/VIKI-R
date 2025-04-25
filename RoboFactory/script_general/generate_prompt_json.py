import argparse
import random
from copy import deepcopy
from collections import Counter
from task_pool import TASK_POOL
import json, pprint
import re
from generate_prompt import instantiate_task

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', type=int, default=1000, help='the number of generated data')
    parser.add_argument('-o', '--output', type=str, default='script_general/output.json', help='the output file')
    args = parser.parse_args()

    count = 0
    data = []
    while count < args.number:
        try:
            sample = instantiate_task(random.choice(TASK_POOL))
        except Exception as e:
            print(e)
            continue
        sample['task_id'] = f'{count}_{sample["task_id"]}'
        data.append(sample)
        count += 1
    json.dump(data, open(args.output, 'w'), indent=4)
    print("Successfully generated %d data." % len(data))