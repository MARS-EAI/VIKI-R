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
                    }
                }
            }
        """
        self.metadata = metadata
        self.agents = {}
        for agent_name, agent_cfg in metadata["agents"]:
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
        for asset_name, asset_cfg in metadata["assets"]:
            pos_params = asset_cfg['pos'] if 'pos' in asset_cfg else {"name": asset_name}
            asset_pos = Position(**pos_params)
            asset_params = asset_cfg['params'] if 'params' in asset_cfg else {}
            self.assets[asset_name] = Asset(
                name=asset_name,
                pos=asset_pos,
                **asset_params
            )
    
    def step(self, command: list):
        # assume feasible command
        operation = command[0]
        params = command[1:]
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
        else:
            raise ValueError('Unsupported operation')