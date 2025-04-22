

class Position:
    def __init__(
        self,
        name: str, 
        isolated: bool = False
    ):
        self.name = name
        self.isolated = isolated


class Asset:
    def __init__(
        self, 
        name: str,
        pos: Position,
        is_grasped_by: list[str] = [],
        is_activated: bool = False,    # whether the asset is interacted
        is_container: bool = False    # whether the asset can serve as a container (holding other assets)
    ):
        self.name = name
        self.pos = pos
        self.is_grasped_by = is_grasped_by
        self.is_activated = is_activated
        self.is_container = is_container


class Agent:
    def __init__(
        self,
        name: str,
        pos: Position,
        avail_actions: list[str],    # available action list
        end_effector_num: int = 0,
        reached_objects: list[str] = [],
        carried_objects: list[str] = []
    ):
        self.name = name
        self.pos = pos
        self.avail_actions = avail_actions
        self.end_effector_num = end_effector_num
        self.reached_objects = reached_objects
        self.carried_objects = carried_objects
    

def check_agent_has_free_end_effector(agent: Agent):
    return agent.end_effector_num - len(agent.carried_objects) > 0

def check_asset_is_activated(asset: Asset):
    return asset.is_activated

def check_asset_pos(asset: Asset, pos: Position):
    return asset.pos.name == pos.name

def check_pos_is_isolated(pos: Position):
    return pos.isolated

def check_asset_is_grasped(asset: Asset):
    return len(asset.is_grasped_by) > 0

def check_asset_is_reached(asset: Asset, agent: Agent):
    return asset.name in agent.reached_objects

def check_agent_pos(agent: Agent, pos: Position):
    return agent.pos.name == pos.name

def check_agent_action(agent: Agent, action: str):
    return action in agent.avail_actions

