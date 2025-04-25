from typing import Union
from itertools import combinations

from .entities import Action, Agent, Asset, Position, ALL_ACTIONS
    

class Checker:
    def check_agent_has_free_end_effector(self, agent: Agent):
        return agent.end_effector_num - len(agent.carried_objects) > 0

    def check_asset_is_activated(self, asset: Asset):
        return asset.is_activated

    def check_asset_pos(self, asset: Asset, pos: Position):
        return asset.pos.name == pos.name

    def check_pos_is_isolated(self, pos: Position):
        return pos.isolated

    def check_asset_is_grasped(self, asset: Asset):
        return len(asset.is_grasped_by) > 0

    def check_asset_is_reached(self, asset: Asset, agent: Agent):
        return asset.name in agent.reached_objects

    # def check_agent_pos(self, agent: Agent, pos: Position):
    #     return agent.pos.name == pos.name

    def check_agent_action(self, agent: Agent, action: Action):
        return action.name in agent.avail_actions

    def check_action_target(self, action: Action, target: list):
        if len(target) != len(action.param_types):
            return False
        for t, p in zip(target, action.param_types):
            if type(t) not in p:
                return False
        if action.param_scopes is not None:
            for t, scope in zip(target, action.param_scopes):
                for k, value_set in scope.items():
                    if getattr(action, k) not in value_set:
                        return False
        return True

    def check_target_aligned_position(self, target: Union[Agent, Asset], pos: Position, assets: dict, agents: dict, finished: list = []):
        # known: possible deadlocks
        if target in finished:
            return False
        finished.append(target)
        if target.pos.name in assets:
            return self.check_target_aligned_position(assets[target.pos.name], pos, assets, agents) or target.pos.name == pos.name
        elif target.pos.name in agents:
            return self.check_target_aligned_position(agents[target.pos.name], pos, assets, agents) or target.pos.name == pos.name
        else:
            return target.pos.name == pos.name
    
    def check_agent_relative_position(self, agent: Agent, target: Union[Agent, Asset]):
        return agent.pos.name == target.name or agent.name == target.pos.name
    
    def check_operation(self, operation_name: str, params: list, assets: dict = None, agents: dict = None):
        if not assets:
            assets = {}
        if not agents:
            agents = {}
        if operation_name not in ALL_ACTIONS:
            return False
        action_type = ALL_ACTIONS[operation_name]
        if not self.check_action_target(action_type, params[1:]):
            return False
        if operation_name == 'move':
            return True
        elif operation_name == 'reach':
            if params[0].type in ['unitree_go2' or 'anymal_c'] and params[1].pos.name != 'ground':    # dog can only reach the ground.
                return False
            return self.check_agent_relative_position(params[0], params[1]) and not params[1].pos.isolated
        elif operation_name == 'grasp':
            return not self.check_asset_is_grasped(params[1]) and self.check_agent_has_free_end_effector(params[0]) and params[0].is_reached_objects(params[1])
        elif operation_name == 'place':
            return self.check_target_aligned_position(params[0], params[1], assets, agents) and len(params[0].get_carried_objects()) > 0
        elif operation_name == 'open':
            return self.check_agent_relative_position(params[0], params[1]) and self.check_agent_has_free_end_effector(params[0]) and self.check_pos_is_isolated(params[1].pos)
        elif operation_name == 'close':
            return self.check_agent_relative_position(params[0], params[1]) and self.check_agent_has_free_end_effector(params[0]) and not self.check_pos_is_isolated(params[1].pos)
        elif operation_name == 'handover':    # handover <asset, agent>
            return self.check_agent_relative_position(params[0], params[2]) and len(params[0].get_carried_objects()) > 0 and self.check_agent_has_free_end_effector(params[2])
        elif operation_name == 'interact':    # known: agent may activate irrelevant assets, can be solved by informing each task of interact scopes
            if params[1] not in params[0].get_carried_objets() and not self.check_agent_has_free_end_effector(params[0]):
                return False
            return self.check_agent_relative_position(params[0], params[1], assets, agents) and not self.check_asset_is_activated(params[1])
        else:    # should never reach
            raise ValueError(f'Unexpected operation: {operation_name}.')
    
    def check_compatible_paired_actions(self, command_x: str, command_y: str):
        """
                        MOVE REACH GRASP PLACE OPEN CLOSE HANDOVER INTERACT
            MOVE         o     o     o     o     o    o      o        o
            REACH        o     o     x     x     x    x      x        x
            GRASP        o     x     x     x     x    x      x        x
            PLACE        o     x     x     o     x    x      x        x
            OPEN         o     x     x     x     x    x      x        x
            CLOSE        o     x     x     x     x    x      x        x
            HANDOVER     o     x     x     x     x    x      x        x
            INTERACT     o     x     x     x     x    x      x        x
        """
        if 'move' in [command_x, command_y]:
            return True
        if command_x == 'reach' and command_y == 'reach':
            return True
        if command_x == 'place' and command_y == 'place':
            return True
        return False

    def check_compatible_constraints(self, step_commands: list, assets: dict = None, agents: dict = None):
        if not assets:
            assets = {}
        if not agents:
            agents = {}
        commands = [command[0] for command in step_commands if command]
        params = [command[1:] for command in step_commands if command]
        target_entities = {}
        for idx, inst_params in enumerate(params):    # params for inst idx
            for param in inst_params:
                if param.name in assets:
                    if param.name not in target_entities:
                        target_entities[param.name] = [idx]
                    else:
                        target_entities[param.name].append(idx)
        for asset, inst_idx  in target_entities.items():
            if len(inst_idx) < 2:
                continue
            operation_names = [commands[i] for i in inst_idx]
            for op1, op2 in combinations(operation_names, 2):
                if not self.check_compatible_paired_actions(op1, op2):
                    return False
                
        # close operation should avoid collisions within the position
        if 'close' in commands:
            target_container = params[commands.index('close')][0]
            for idx, inst_params in enumerate(params):
                for param in inst_params:
                    if isinstance(param, Asset) and param.pos == target_container.container_position and commands[idx] not in ['move', 'close']:
                        return False
        return True