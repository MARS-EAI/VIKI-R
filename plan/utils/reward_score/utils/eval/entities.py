from typing import Optional

class Action:
    def __init__(
        self, 
        name: str,
        param_types: Optional[list[set]] = None,
        param_scopes: Optional[list[dict]] = None,
    ):
        self.name = name
        self.param_types = param_types if param_types else []
        self.param_scopes = param_scopes if param_scopes else []


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
        is_grasped_by: Optional[list] = None,
        is_activated: bool = False,    # whether the asset is interacted
        is_container: bool = False,    # whether the asset can serve as a container (holding other assets)
        position_kwargs: Optional[dict] = None,
    ):
        self.name = name
        self.pos = pos
        self.is_grasped_by = is_grasped_by if is_grasped_by else []
        self.is_activated = is_activated
        self.is_container = is_container
        if self.is_container:
            position_kwargs = {"name": name, "isolated": False} if not position_kwargs else position_kwargs
            self.container_position = Position(**position_kwargs)


class Agent:
    def __init__(
        self,
        name: str,
        type: str, 
        pos: Position,
        avail_actions: list[str],    # available action list
        end_effector_num: int = 0,
        reached_objects: Optional[list] = None,
        carried_objects: Optional[list] = None,
    ):
        self.name = name    # R1
        self.type = type    # panda
        self.pos = pos
        self.avail_actions = avail_actions
        self.end_effector_num = end_effector_num
        self.reached_objects = reached_objects if reached_objects else []
        self.carried_objects = carried_objects if carried_objects else []
    
    def get_reached_objects(self):
        return self.reached_objects
    
    def get_carried_objects(self):
        return self.carried_objects
    
    def is_reached_objects(self, asset: Asset):
        return asset in self.reached_objects
    
    def is_carried_objects(self, asset: Asset):
        return asset in self.carried_objects
    
    # def info(self):
    #     print(f'name: {self.name}')
    #     print(f'type: {self.type}')
    #     print(f'pos: {self.pos}')
    #     print(f'reached_objects: {self.reached_objects}')
    #     print(f'carried_objects: {self.carried_objects}')
              
ALL_ACTIONS  = {
    'move': Action(name='move', param_types=[{Agent, Asset, Position}]),
    'reach': Action(name='reach', param_types=[{Agent, Asset}]),
    'grasp': Action(name='grasp', param_types=[{Asset}]),
    'place': Action(name='place', param_types=[{Asset, Position}]),
    'open': Action(name='open', param_types=[{Asset}], param_scopes=[{"name": {'cabinet', 'drawer', 'kitchen cabinet', 'kitchen drawer'}}]),
    'close': Action(name='close', param_types=[{Asset}], param_scopes=[{"name": {'cabinet', 'drawer', 'kitchen cabinet', 'kitchen drawer'}}]),
    'push': Action(name='push', param_types=[{Asset}, {Asset, Position, Agent}], param_scopes=[{"name": {"box", "cardboardbox"}}, {}]),
    'handover': Action(name='handover', param_types=[{Asset}, {Agent}]),
    'interact': Action(name='interact', param_types=[{Asset}]),
}

AGENT_AVAIL_ACTIONS = {
    'panda': ['reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'fetch': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'unitree_go2': ['move', 'push', 'interact'],
    'unitree_h1': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'stompy': ['move', 'reach', 'grasp', 'place', 'open', 'close', 'handover', 'interact'],
    'anymal_c': ['move', 'push', 'interact'],
}

AGENT_END_EFFECTOR_NUM = {
    'panda': 1,
    'fetch': 1,
    'unitree_go2': 0,
    'unitree_h1': 2,
    'stompy': 2,
    'anymal_c': 0,
}