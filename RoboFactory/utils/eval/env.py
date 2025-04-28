from copy import deepcopy
from .entities import Action, Agent, Asset, Position, ALL_ACTIONS, AGENT_AVAIL_ACTIONS, AGENT_END_EFFECTOR_NUM


class SimEnv:
    def __init__(self, metadata: dict):
        """
            metadata: {
                "agents": {
                    "R1": {
                        type: [robot_type],
                        pos: {
                            **kwargs
                        }
                        params: **
                    }
                },
                "assets": {
                    "A1": {
                        pos: {
                            **kwargs
                        }
                        params: **
                        [
                            is_container: True,
                            container_params: **params for pos
                        ]
                    }
                }
            }
        """
        self.metadata = metadata
        self.initialize_scene()
    
    def initialize_scene(self):
        self.agents = {}
        self.assets = {}
        self.container_assets = {}
        for agent_name, agent_cfg in self.metadata["agents"].items():
            agent_type = agent_cfg['type']
            pos_params = agent_cfg['pos'] if 'pos' in agent_cfg else {"name": agent_name}
            agent_pos = Position(**pos_params)    # default as self
            avail_actions = AGENT_AVAIL_ACTIONS[agent_type]
            end_effector_num = AGENT_END_EFFECTOR_NUM[agent_type]
            agent_params = agent_cfg['params'] if 'params' in agent_cfg else {}
            self.agents[agent_name] = Agent(
                name=agent_name,
                type=agent_type,
                pos=agent_pos,
                avail_actions=avail_actions,
                end_effector_num=end_effector_num,
                **agent_params
            )
        for asset_name, asset_cfg in self.metadata["assets"].items():
            pos_params = asset_cfg['pos'] if 'pos' in asset_cfg else {"name": asset_name}
            asset_pos = Position(**pos_params)
            asset_params = asset_cfg['params'] if 'params' in asset_cfg else {}
            asset = Asset(
                name=asset_name,
                pos=asset_pos,
                **asset_params
            )
            self.assets[asset_name] = asset
            if asset.is_container:
                self.container_assets[asset_name] = asset

        # link container positions
        for asset_name, asset in self.assets.items():
            asset_pos_name = asset.pos.name
            if asset_pos_name in self.container_assets:
                self.assets[asset_name].pos = self.container_assets[asset_pos_name].container_position

    def nested_set_attr(self, obj, attr_path: str, value):
        attrs = attr_path.split('.')
        current = obj
        for attr in attrs[:-1]:
            current = getattr(current, attr)
        setattr(current, attrs[-1], value)

    def step(self, command: list):
        # assume feasible command
        operation = command[0]    # str
        params = command[1:]    # entities
        agent = params[0]
        if operation == 'move':
            agent.pos = Position(name=params[1].name)
            agent.get_reached_objects().clear()
        elif operation == 'reach':
            if len(agent.get_reached_objects()) >= agent.end_effector_num:
                agent.get_reached_objects().pop(0)    # release the earliest
            agent.get_reached_objects().append(params[1])
        elif operation == 'grasp':
            agent.get_carried_objects().extend(agent.reached_objects)
            agent.get_reached_objects().clear()
            for carried_object in agent.get_carried_objects():
                carried_object.is_grasped_by.append(agent)
                carried_object.pos = Position(name=agent.name)
        elif operation == 'place':
            for carried_object in agent.get_carried_objects():
                if isinstance(params[1], Position):
                    carried_object.pos = params[1]
                elif isinstance(params[1], Asset):    # asset as position
                    carried_object.pos = params[1].container_position
                carried_object.is_grasped_by.remove(agent)
            agent.get_carried_objects().clear()
        elif operation == 'open':
            params[1].container_position.isolated = False
        elif operation == 'close':
            params[1].container_position.isolated = True
        elif operation == 'handover':
            new_agent = params[1]
            asset = params[2]
            agent.get_carried_objects().remove(asset)
            asset.is_grasped_by.remove(agent)
            asset.pos.name = new_agent.name
            new_agent.get_carried_objects().append(asset)
            asset.is_grasped_by.append(new_agent)
        elif operation == 'interact':
            params[1].is_activated = True
        elif operation == 'push':
            params[0].pos.name = params[1].name
            params[1].pos.name = params[2].name
        else:    # should never reach
            raise ValueError(f'Unsupported operation: {operation}')
        
    def sim_step(self, commands: list):
        new_env_status = {
            "agents": {},
            "assets": {}
        }
        for command in commands:
            operation = command[0]    # str
            params = command[1:]    # entities
            agent = params[0]
            if operation == 'move':
                new_env_status["agents"][agent.name] = {
                    "pos": Position(name=params[1].name),
                    "reached_objects": []
                }
            elif operation == 'reach':
                new_reached_objects = agent.get_reached_objects().copy()
                if len(agent.get_reached_objects()) >= agent.end_effector_num:
                    new_reached_objects.pop(0)
                new_reached_objects.append(params[1])
                new_env_status["agents"][agent.name] = {
                    "reached_objects": new_reached_objects
                }
            elif operation == 'grasp':
                new_carried_objects = agent.get_carried_objects().copy()
                new_carried_objects.extend(agent.get_reached_objects())
                new_env_status["agents"][agent.name] = {
                    "reached_objects": [],
                    "carried_objects": new_carried_objects
                }
                for carried_object in new_carried_objects:
                    is_grasped_by = carried_object.is_grasped_by.copy()
                    is_grasped_by.append(agent)
                    new_env_status["assets"][carried_object.name] = {
                    "is_grasped_by": is_grasped_by,
                    "pos": Position(name=agent.name)
                }
            elif operation == 'place':
                for carried_object in agent.get_carried_objects():
                    if carried_object.name not in new_env_status["assets"]:
                        new_env_status["assets"][carried_object.name] = {}
                    if isinstance(params[1], Position):
                        new_env_status["assets"][carried_object.name]["pos"] = params[1]
                    elif isinstance(params[1], Asset) and hasattr(params[1], 'container_position'):    # asset as container
                        new_env_status["assets"][carried_object.name]["pos"] = params[1].container_position
                    elif isinstance(params[1], Asset):    # asset as position
                        new_env_status["assets"][carried_object.name]["pos"] = params[1]
                    new_env_status["assets"][carried_object.name]["is_grasped_by"] = []
                new_env_status['agents'][agent.name] = {
                    "carried_objects": []
                }
            elif operation == 'open':
                new_env_status["assets"][params[1].name] = {
                    "container_position.isolated": False
                }
            elif operation == 'close':
                new_env_status["assets"][params[1].name] = {
                    "container_position.isolated": True
                }
            elif operation == 'handover':
                new_agent = params[1]
                asset = params[2]
                agent_new_carried_objects = agent.get_carried_objects().copy()
                agent_new_carried_objects.remove(asset)
                new_agent_new_carried_objects = new_agent.get_carried_objects().copy()
                new_agent_new_carried_objects.append(asset)
                is_grasped_by = asset.is_grasped_by.copy()
                is_grasped_by.remove(agent)
                is_grasped_by.append(new_agent)
                new_env_status["agents"][agent.name] = {
                    "carried_objects": agent_new_carried_objects,
                }
                new_env_status["agents"][new_agent.name] = {
                    "carried_objects": new_agent_new_carried_objects,
                }
                new_env_status["assets"][asset.name] = {
                    "pos.name": new_agent.name,
                    "is_grasped_by": is_grasped_by
                }
            elif operation =='interact':
                new_env_status["assets"][params[1].name] = {
                    "is_activated": True
                }
            elif operation == 'push':
                new_env_status["agents"][params[0].name] = {
                    "pos.name": params[1].name
                }
                new_env_status["assets"][params[1].name] = {
                    "pos.name": params[2].name
                }
            else:    # should never reach
                raise ValueError(f'Unsupported operation: {operation}')
        # update env
        for agent_name, agent_status in new_env_status["agents"].items():
            for agent_attr, value in agent_status.items():
                self.nested_set_attr(self.agents[agent_name], agent_attr, value)
        for asset_name, asset_status in new_env_status["assets"].items():
            for asset_attr, value in asset_status.items():
                self.nested_set_attr(self.assets[asset_name], asset_attr, value)