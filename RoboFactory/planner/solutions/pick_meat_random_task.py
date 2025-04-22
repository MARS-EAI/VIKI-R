import numpy as np
import sapien
import os
from tasks import PickMeatRandomTaskEnv
from planner.motionplanner import PandaArmMotionPlanningSolver
from PIL import Image
import json

def solve(env: PickMeatRandomTaskEnv, seed=None, debug=False, vis=False):
    env.reset(seed=seed)
    env = env.unwrapped
    # while 1:
    #     env.render_human()
    res_video = env.render()
    for _ in range(10):
        res_video = env.render()
    out_dir = 'demos/PickMeatRandomTaskRenders'
    # meta_file = 'meta_data.json'
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'images'), exist_ok=True)
    fns = os.listdir(os.path.join(out_dir, 'images'))
    # robot_num = len(env.scene_builder.articulations)
    fn_idx = 0
    while f'{fn_idx}.png' in fns:
        fn_idx += 1
    # if os.path.exists(os.path.join(out_dir, meta_file)):
    #     with open(os.path.join(out_dir, meta_file), 'r') as f:
    #         meta_data = json.load(f)
    # else:
    #     meta_data = []
    Image.fromarray(res_video[0, :, :, :].cpu().numpy()).save(os.path.join(out_dir, 'images', f'{fn_idx}.png'))
    # meta_data.append({
    #     'image': f'{fn_idx}.png',
    #     'robot_num': robot_num,
    #     'robot_uids': env.robot_uids,
    # })
    # json.dump(meta_data, open(os.path.join(out_dir, meta_file), 'w'), indent=4)
    exit(0)
    res = {}
    return res
