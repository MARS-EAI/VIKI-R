import argparse
import os
import json
import yaml
from datetime import datetime
import random

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='script_general/output.json', help="the json file for data")
    parser.add_argument('--temp_config_path', type=str, default='data_gen', help="the save path for temp configs")
    parser.add_argument('--save_temp_config', action='store_true', help="whether to save temp configs")
    args = parser.parse_args()

    data = json.load(open(args.data, 'r'))
    print(f'Get {len(data)} data.')

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"data_{current_time}"
    os.makedirs(os.path.join(args.temp_config_path, folder_name), exist_ok=True)

    for gt in data:
        
        general_config_file = 'configs/robocasa_random_task/layout_8_pick_meat_multiple_assets.yaml'    # the config that consists all possible assets & agents in a layout
        with open(general_config_file, 'r', encoding='utf-8') as f:
            general_config = yaml.load(f.read(), Loader=yaml.FullLoader)
        # generate a subset config that fits the gt as temp_config
        temp_config_name = f'task_{gt["task_id"]}.yaml'
        temp_config = general_config

        object_cfgs = general_config['objects']
        agent_cfgs = general_config['agents']

        objects_dict = {}    # all available assets
        agents_dict = {}    # all available agents
        pos_dict = {}
        for agent_cfg in agent_cfgs:
            agent_name = agent_cfg['robot_uid'].rsplit('-', maxsplit=1)[0]
            agents_dict[agent_name] = agent_cfg
        for object_cfg in object_cfgs:
            object_name = object_cfg['name'].rsplit('_', maxsplit=1)[0].replace(' ', '_').replace('-', '_')
            objects_dict[object_name] = object_cfg
        for pos_area in general_config['position_areas']:
            pos_args = pos_area['pos']
            pos_names = pos_area['names']
            for pos_name in pos_names:
                pos_dict[pos_name] = pos_args
        # print(agents_dict)
        # print(objects_dict)
        # print(pos_dict)
        # select needed objects and agents
        new_object_cfgs = []
        new_agent_cfgs = []
        transparent_style = False

        for c, robot_type in enumerate(gt['robots'].values()):
            base_agent_cfg = agents_dict[robot_type].copy()
            base_agent_cfg['robot_uid'] = f'{robot_type}-{c}'
            new_agent_cfgs.append(base_agent_cfg)

        for item_name, item_pos in gt['init_pos'].items():
            item_type = item_name.rsplit('_', maxsplit=1)[0].replace(' ', '_').replace('-', '_')
            item_cfg = objects_dict[item_type]
            item_cfg['name'] = item_name
            
            # set random positions
            position_area = random.choice(item_pos)
            if position_area in ['cabinet', 'rack', 'kitchen cabinet', 'kitchen rack']:
                transparent_style = True
            new_pos_cfg = pos_dict[position_area]
            for axis in range(len(item_cfg['pos']['ppos']['p'])):
                item_cfg['pos']['ppos']['p'][axis] = new_pos_cfg['ppos']['p'][axis] + item_cfg['pos']['ppos']['p'][axis]
            item_cfg['pos']['randp_scale'] = new_pos_cfg['randp_scale']
            new_object_cfgs.append(item_cfg)
        
        if transparent_style:
            style_idx = random.choice([4, 11])
        else:
            style_idx = random.randint(0, 11)
        temp_config['scene']['env']['style_idx'] = style_idx
        
        temp_config['agents'] = new_agent_cfgs
        temp_config['objects'] = new_object_cfgs


        

        # print(general_config)

        yaml.dump(temp_config, open(os.path.join(args.temp_config_path, folder_name, temp_config_name), 'w'))
        command = (
            f"python script/generate_data.py \\"
            f"{os.path.join(args.temp_config_path, folder_name, temp_config_name)} \ " 
            f"100 "
        )

        os.system(command)
        # os.system('')    # generate
        if not args.save_temp_config:
            os.remove(os.path.join(args.temp_config_path, folder_name, temp_config_name))

if __name__ == "__main__":
    main()
