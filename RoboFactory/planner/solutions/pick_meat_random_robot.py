import numpy as np
import sapien
import os
from tasks import PickMeatRandomRobotEnv
from planner.motionplanner import PandaArmMotionPlanningSolver
from PIL import Image
import json

def solve(env: PickMeatRandomRobotEnv, seed=None, debug=False, vis=False):
    env.reset(seed=seed)
    env = env.unwrapped
    while 1:
        env.render_human()
    res_video = env.render()
    out_dir = 'demos/PickMeatRandomRobotRenders'
    meta_file = 'meta_data.json'
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, 'images'), exist_ok=True)
    fns = os.listdir(os.path.join(out_dir, 'images'))
    robot_num = len(env.scene_builder.articulations)
    fn_idx = 0
    while f'{fn_idx}.png' in fns:
        fn_idx += 1
    if os.path.exists(os.path.join(out_dir, meta_file)):
        with open(os.path.join(out_dir, meta_file), 'r') as f:
            meta_data = json.load(f)
    else:
        meta_data = []
    Image.fromarray(res_video[0, :, :, :].numpy()).save(os.path.join(out_dir, 'images', f'{fn_idx}.png'))
    meta_data.append({
        'image': f'{fn_idx}.png',
        'gt': env.cfg['gt']
    })
    json.dump(meta_data, open(os.path.join(out_dir, meta_file), 'w'), indent=4)
    exit(0)
    planner = PandaArmMotionPlanningSolver(
        env,
        debug=False,
        vis=vis,
        base_pose=[agent.robot.pose for agent in env.agent.agents],
        visualize_target_grasp_pose=vis,
        print_env_info=False,
        is_multi_agent=True,
    )
    pose1 = env.scene_builder.articulations['panda-0'].robot.pose
    pose1[2] += 0.1
    # pose1 = planner.get_grasp_pose_w_labeled_direction(actor=env.meat, actor_data=env.annotation_data['meat'], pre_dis=0)
    # planner.move_to_pose_with_screw(pose1)
    # planner.close_gripper()
    # pose1[2] += 0.2
    res = planner.move_to_pose_with_screw([pose1], move_id=[0])
    res = planner.close_gripper()
    # while 1:
    #     planner.open_gripper()
    return res
