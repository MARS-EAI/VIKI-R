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
        self.assets = {}
        self.container_assets = {}
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
                self.container_assets[asset_pos_name].add_container_position(asset.pos)
        for container_asset_name, container_asset in self.container_assets.items():   
            if 'container_params' in self.metadata['assets'][container_asset_name]:
                container_asset.set_all_container_positions(self.metadata['assets'][container_asset_name]['container_params'])

    def step(self, command: list):
        # assume feasible command
        operation = command[0]    # str
        params = command[1:]    # entities
        agent = params[0]
        if operation == 'move':
            agent.pos.name = params[1].name    # known bug: move to agent may cause the wrong position.
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
                carried_object.pos.name = agent.name
        elif operation == 'place':
            for carried_object in agent.get_carried_objects():
                carried_object.pos = params[1]
                carried_object.is_grasped_by.remove(agent)
            agent.get_carried_objects().clear()
        elif operation == 'open':
            for position in params[1].container_positions:
                position.isolated = False
        elif operation == 'close':
            for position in params[1].container_positions:
                position.isolated = True
        elif operation == 'handover':
            new_agent = params[1]
            asset = params[2]
            agent.get_carried_objects().remove(asset)
            asset.is_grasped_by.remove(agent)
            asset.pos.name = new_agent.name
            new_agent.get_carried_objects().append(asset)
            asset.is_grasped_by.append(new_agent)
        elif operation =='interact':
            params[1].is_activated = True
        else:    # should never reach
            raise ValueError(f'Unsupported operation: {operation}')