from typing import Union

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
            if t not in p:
                return False
        if action.param_scopes is not None:
            for t, scope in zip(target, action.param_scopes):
                for k, value_set in scope.items():
                    if getattr(action, k) not in value_set:
                        return False
        return True

    def check_target_aligned_position(self, target: Union[Agent, Asset], pos: Position, assets: dict, agents: dict):
        if target.pos.name in assets:
            return self.check_target_aligned_position(assets[target.pos.name], pos, assets, agents) or target.pos.name == pos.name
        elif target.pos.name in agents:
            return self.check_target_aligned_position(agents[target.pos.name], pos, assets, agents) or target.pos.name == pos.name
        else:
            return target.pos.name == pos.name
    
    def check_agent_relative_position(self, agent: Agent, target: Union[Agent, Asset]):
        return agent.pos.name == target.name or agent.name == target.pos.name
    
    def check_operation(self, operation_name: str, params: list, assets: dict = {}, agents: dict = {}):
        if operation_name not in ALL_ACTIONS:
            return False
        action_type = ALL_ACTIONS[operation_name]
        if not self.check_action_target(action_type, params):
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
            return False
