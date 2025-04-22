class Action:
    def __init__(
        self, 
        name: str,
        param_types: list[set] = []
    ):
        self.name = name
        self.param_types = param_types

ALL_ACTIONS  = {
    'move': Action(name='move', param_types=[{'agent', 'asset'}]),
    'reach': Action(name='reach', param_types=[{'asset'}]),
    'grasp': Action(name='grasp', param_types=[{'asset'}]),
    'place': Action(name='place', param_types=[{'asset'}]),
    'pull': Action(name='pull', param_types=[{'asset'}]),
    'push': Action(name='push', param_types=[{'asset'}]),
    'open': Action(name='open', param_types=[{'asset'}]),
    'close': Action(name='close', param_types=[{'asset'}]),
    'handover': Action(name='handover', param_types=[{'asset'}, {'agent'}]),
    'interact': Action(name='interact', param_types=[{'asset'}]),
}

AGENT_AVAIL_ACTIONS = {
    'panda': ['reach', 'grasp', 'place', 'pull', 'push', 'open', 'close', 'handover', 'interact'],
    'fetch': ['move', 'reach', 'grasp', 'place', 'pull', 'push', 'open', 'close', 'handover', 'interact'],
    'unitree_go2': ['move', 'reach', 'grasp', 'place', 'pull', 'push', 'open', 'close', 'handover', 'interact'],
    'unitree_h1': ['move', 'reach', 'grasp', 'place', 'pull', 'push', 'open', 'close', 'handover', 'interact'],
    'stompy': ['move', 'reach', 'grasp', 'push', 'handover', 'interact'],
    'anymal_c': ['move', 'reach', 'grasp', 'push', 'handover', 'interact'],
}