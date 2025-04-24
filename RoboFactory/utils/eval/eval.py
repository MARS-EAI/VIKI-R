from .env import SimEnv
from .checker import Checker

class Eval:
    def __init__(self):
        self.checker = Checker()

    def set_env(self, env_metadata):
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
    def parse_command(self, command):
        pass

    def eval(self, commands):
        pass
