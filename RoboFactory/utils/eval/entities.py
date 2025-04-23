from typing import Union

class Action:
    def __init__(
        self, 
        name: str,
        param_types: list[set] = [],
        param_scopes: Union[list[dict], None] = None,
    ):
        self.name = name
        self.param_types = param_types
        self.param_scopes = param_scopes


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
        is_grasped_by: list = [],
        is_activated: bool = False,    # whether the asset is interacted
        # is_container: bool = False    # whether the asset can serve as a container (holding other assets)
    ):
        self.name = name
        self.pos = pos
        self.is_grasped_by = is_grasped_by
        self.is_activated = is_activated
        # self.is_container = is_container


class Agent:
    def __init__(
        self,
        name: str,
        type: str, 
        pos: Position,
        avail_actions: list[str],    # available action list
        end_effector_num: int = 0,
        reached_objects: list = [],
        carried_objects: list = []
    ):
        self.name = name    # R1
        self.type = type    # panda
        self.pos = pos
        self.avail_actions = avail_actions
        self.end_effector_num = end_effector_num
        self.reached_objects = reached_objects
        self.carried_objects = carried_objects
    
    def get_reached_objects(self):
        return self.reached_objects
    
    def get_carried_objects(self):
        return self.carried_objects
    
    def is_reached_objects(self, asset: Asset):
        return asset in self.reached_objects
    
    def is_carried_objects(self, asset: Asset)
        return asset in self.carried_objects
    

ALL_ACTIONS  = {
    'move': Action(name='move', param_types=[{Agent, Asset}]),
    'reach': Action(name='reach', param_types=[{Agent, Asset}]),
    'grasp': Action(name='grasp', param_types=[{Asset}]),
    'place': Action(name='place', param_types=[{Asset}]),
    'open': Action(name='open', param_types=[{Asset}], param_scopes=[{"name": {'cabinet', 'drawer', 'kitchen cabinet', 'kitchen drawer'}}]),
    'close': Action(name='close', param_types=[{Asset}], param_scopes=[{"name": {'cabinet', 'drawer', 'kitchen cabinet', 'kitchen drawer'}}]),
    'handover': Action(name='handover', param_types=[{Asset}, {Agent}]),
    'interact': Action(name='interact', param_types=[{Asset}]),
}

AGENT_AVAIL_ACTIONS = {
    'panda': ['reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'fetch': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'unitree_go2': ['move', 'reach', 'grasp', 'place', 'handover', 'interact'],
    'unitree_h1': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'stompy': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'anymal_c': ['move', 'reach', 'grasp', 'place', 'handover', 'interact'],
}

AGENT_END_EFFECTOR_NUM = {
    'panda': 1,
    'fetch': 1,
    'unitree_go2': 1,
    'unitree_h1': 2,
    'stompy': 2,
    'anymal_c': 1,
}