import re

from .env import SimEnv
from .checker import Checker
from .entities import Position

class Eval:
    def __init__(self):
        self.checker = Checker()
        self.error_desc_code = None
        self.error_desc_table = {
            "INVALID_COMMAND": "invalid format of the command.",
            "NOT_FOUND_ENTITY": "entity not found in the environment.",
            "ACTION_NOT_FEASIBLE": "action not feasible.",
            "FAILED_GOAL_CONSTRAINT": "failed goal constraint.",
            "ACTION_NOT_COMPATIBLE": "action not compatible in one step.",
            "FAILED_TEMPORAL_CONSTRAINT": "failed temporal constraint.",
        }

    def set_env(self, env_metadata):
        """
            metadata: {
                "agents": {
                    "R1": {
                        type: [robot_type],
                        pos: {
                            name: XXXX,
                            **kwargs
                        }
                        params: **
                    }
                },
                "assets": {
                    "A1": {
                        pos: {
                            name: XXXX,
                            **kwargs
                        }
                        params: **
                        [
                            is_container: True,
                            container_params: {
                                name: 
                                is_isoloated: True
                            }
                        ]
                    }
                }
            }
        """
        self.env = SimEnv(metadata=env_metadata)

    def set_constraints(self, constraints):
        """
            "constraints": [
                # all constraints should be satisified.
                [
                    # temporal dependencies [list]: former status should be realized earlier than later.
                    # e.g., 1. bread moved to toaster before toaster being activated
                    [
                        # temporal constraint 1:
                        {    # status 1: bread in toaster
                            "type": asset    # {asset, agent}
                            "name": bread
                            "is_satisfied": True
                            "status": {
                                "pos.name": "toaster"
                            }
                        }
                    ],
                    [
                        # temporal constraint 2:
                        {
                            # status 2: toaster activated
                            "type": asset
                            "name": toaster
                            "is_satisfied": True
                            "status": {
                                "is_activated": True
                            }
                        }
                    ]
                ],
                [
                    # e.g., 2. pot moved to flower before being poured
                    [
                        {    # status 1: pot at flower
                            "type": asset    # {asset, agent}
                            "name": pot
                            "is_satisfied": True
                            "status": {
                                "pos.name": "flower"    # should use aligned position
                                "is_activated": False
                            }
                        },
                    ]
                    [
                        {    # status 2: pot at flower and activated

                            "type": asset    # {asset, agent}
                            "name": pot
                            "is_satisfied": True
                            "status": {
                                "pos.name": "flower"    # should use aligned position
                                "is_activated": True
                            }
                        },
                    ]
                ],
                [
                    # e.g., 3. pot at the table
                    [
                        {
                            "type": asset    # {asset, agent}
                            "name": pot
                            "is_satisfied": True
                            "status": {
                                "pos.name": "table"
                                "is_grasped_by": []
                        }
                    ]
                ]
            ]

        """

    def is_valid_sequence(self, s):
        pattern = r'^<\s*([^,<>][^,<>]*\s*)(\s*,\s*[^,<>][^,<>]*\s*)*>$'
        return bool(re.match(pattern, s))

    def get_error_desc(self):
        if self.error_desc_code in self.error_desc_table:
            return self.error_desc_table[self.error_desc_code]
        else:
            return ""
        
    def parse_command(self, command_desc: str):
        content = command_desc[1:-1].strip()
        elements = [elem.strip() for elem in content.split(',')]
        elements[0] = elements[0].lower()
        return elements

    def nested_getattr(self, obj, attr_path):
        attrs = attr_path.split('.')
        for attr in attrs:
            obj = getattr(obj, attr)
        return obj

    def check_constraint(self, constraint: list[dict]):
        for target_status in constraint:
            if isinstance(target_status, list) and len(target_status) == 1:
                target_status = target_status[0]
            target_entity = getattr(self.env, f'{target_status["type"]}s')[target_status['name']]
            # status_achieved = True
            positive_check = target_status['is_satisfied']
            check_pos_type = target_status.get('check_pos_type', 'static')
            for target_attr, target_value in target_status['status'].items():
                success = True
                if check_pos_type == 'aligned' and 'pos.name' in target_attr:    # check aligned position
                    success = success and (self.checker.check_target_aligned_position(target_entity, Position(name=target_value), self.env.assets, self.env.agents) ^ (not positive_check))
                else:
                    success = (self.nested_getattr(target_entity, target_attr) == target_value) ^ (not positive_check)
                if not success:
                    return False
        return True

    def eval(self, command_records: list):
        """
        command_records: [
            {
                id_1: command,    # <opeartion, param1, ...>
                ...
            }
        ]
        """
        # parse
        all_commands = []
        for command_record in command_records:
            # the same step
            commands = []
            for robot_name, command_desc in command_record.items():
                if not self.is_valid_sequence(command_desc):
                    print(f'Current command: {command_desc}')
                    self.error_desc_code = "INVALID_COMMAND"
                    return False
                parsed_command = self.parse_command(command_desc)
                parsed_command.insert(1, robot_name)    # add the agent name
                commands.append(parsed_command)
            all_commands.append(commands)
        
        # action feasibility
        satisfied_temporal_constraints = [False] * len(self.env.metadata['temporal_constraints'])
        for commands in all_commands:
            step_commands = []    # commands in one step
            for command in commands:
                operation_name = command[0]
                operation_params = command[1:]
                operation_entities = []
                for operation_param in operation_params:
                    if operation_param in self.env.agents:
                        operation_entities.append(self.env.agents[operation_param])
                    elif operation_param in self.env.assets:
                        operation_entities.append(self.env.assets[operation_param])
                    elif operation_name in ['move', 'place']:
                        operation_entities.append(Position(name=operation_param))
                    else:
                        print(f'Not Found Entity: {operation_param}')
                        self.error_desc_code = "NOT_FOUND_ENTITY"
                        return False
                is_available_action = self.checker.check_operation(operation_name=operation_name, params=operation_entities, assets=self.env.assets, agents=self.env.agents)
                if not is_available_action:
                    self.error_desc_code = 'ACTION_NOT_FEASIBLE'
                    return False
                # step env step by step
                robot_inst_params = [operation_name]
                robot_inst_params.extend(operation_entities)
                step_commands.append(robot_inst_params)
            is_compatible_actions = self.checker.check_compatible_constraints(step_commands=step_commands, assets=self.env.assets, agents=self.env.agents)
            if not is_compatible_actions:
                self.error_desc_code = 'ACTION_NOT_COMPATIBLE'
                return False
            self.env.sim_step(step_commands)
            # for step_command in step_commands:
            #     self.env.step(step_command)
            # check temporal constraints
            # if 'temporal_constraints' in self.env.metadata:
            temporal_constraints = self.env.metadata['temporal_constraints']
            for idx, temporal_constraint in enumerate(temporal_constraints):
                if satisfied_temporal_constraints[idx]:
                    continue
                satisfied_temporal_status = True
                for temporal_status in temporal_constraint:
                    if self.check_constraint(temporal_status):
                        if not satisfied_temporal_status:
                            self.error_desc_code = 'FAILED_TEMPORAL_CONSTRAINT'
                            return False
                    else:
                        satisfied_temporal_status = False
                if satisfied_temporal_status:
                    satisfied_temporal_constraints[idx] = True
        
        # check final status
        if len(satisfied_temporal_constraints) != 0 and not all(satisfied_temporal_constraints):
            self.error_desc_code = 'FAILED_TEMPORAL_CONSTRAINT'
            return False
        goal_constraints = self.env.metadata['goal_constraints']
        for goal_constraint in goal_constraints:
            if not self.check_constraint(goal_constraint):
                self.error_desc_code = 'FAILED_GOAL_CONSTRAINT'
                return False
        return True