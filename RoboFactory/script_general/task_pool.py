"""
Task template pool for multi‑agent embodied data generation.

Each template dict contains:
  • task_name        – unique identifier
  • description      – English sentence with <maskX> placeholders
  • mask*            – lists of strings to substitute for each placeholder
  • robot_roles      – ordered list of abstract robot categories
  • ground_truth     – list of timestep dictionaries mapping Ri to [Primitive, Target
]

Add or modify templates as needed; the main pipeline can import TASK_POOL
and sample/instantiate concrete tasks.
"""

__all__ = [
    "TASK_POOL"
]

TASK_POOL = [
    # 1 - Move 1 objects to one place with 1 robots
    {
        "task_id": "1-1",
        "task_name": "single_move_asset_to_target",
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "description": [
            "Move the <mask1> to the <mask2> so it is ready for the next step.",
            "Please carefully place the <mask1> onto the <mask2> to continue the preparation.",
            "Transfer the <mask1> over to the <mask2> and ensure it is positioned correctly.",
            "Put the <mask1> on the <mask2> so it can be used later.",
            "Take the <mask1> and move it to the <mask2> in an orderly manner.",
            "Gently move the <mask1> onto the <mask2> to complete this part of the task.",
            "Relocate the <mask1> to the <mask2> as instructed.",
            "Pick up the <mask1> and place it on the <mask2> to set things up.",
            "Move the <mask1> from its current location to the <mask2>.",
            "Ensure that the <mask1> is moved properly onto the <mask2> for the next operation."
        ],
        "mask1": [
            "meat",
            "cardboardbox",
            "pumpkin",
            "cooling fan",
            "cup",
            "bread",
            "plate",
            "bottle",
            "pizza",
            "scissors",
            "wine",
            "banana",
            "apple",
            "kettle",
            "tomato",
            "spoon",
            "pear",
            "peach",
            "fork"
        ],
        "mask2": [
            "kitchen work area",
            "kitchen island area",
            "rack"
        ],
        "robot_roles": [
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask2>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
        # G-Constraint 1: <mask1> should be moved to <mask2>
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask2>"
                    }
                }
            ]
        ],
    },
    {
        "task_id": "1-2",
        "task_name": "single_move_asset_to_target",
        "description": [
            "Move the <mask1> to the <mask2> so it is ready for the next step.",
            "Please carefully place the <mask1> onto the <mask2> to continue the preparation.",
            "Transfer the <mask1> over to the <mask2> and ensure it is positioned correctly.",
            "Put the <mask1> on the <mask2> so it can be used later.",
            "Take the <mask1> and move it to the <mask2> in an orderly manner.",
            "Gently move the <mask1> onto the <mask2> to complete this part of the task.",
            "Relocate the <mask1> to the <mask2> as instructed.",
            "Pick up the <mask1> and place it on the <mask2> to set things up.",
            "Move the <mask1> from its current location to the <mask2>.",
            "Ensure that the <mask1> is moved properly onto the <mask2> for the next operation."
        ],
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "mask1": [
            "meat",
            "cardboardbox",
            "pumpkin",
            "cooling fan",
            "cup",
            "bread",
            "plate",
            "bottle",
            "pizza",
            "scissors",
            "wine",
            "banana",
            "apple",
            "kettle",
            "tomato",
            "spoon",
            "pear",
            "peach",
            "fork"
        ],
        "mask2": [
            "kitchen work area",
            "kitchen island area"
        ],
        "robot_roles": [
            "wheeled"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask2>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
        # G-Constraint 1: <mask1> should be moved to <mask2>
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask2>"
                    }
                }
            ]
        ]
    },
    
    # 2 - Move 2 objects to one place with 2 robots
    {
        "task_id": "2-1",
        "task_name": "parallel_human_dual_asset_to_plate_or_bowl",
        "description": [
            "Transport the <mask1> and the <mask2> into the <mask3> together.",
            "Move both the <mask1> and the <mask2> into the <mask3> to prepare for serving.",
            "Carry the <mask1> along with the <mask2> and place them into the <mask3>.",
            "Relocate the <mask1> and <mask2> side by side into the <mask3>.",
            "Ensure the <mask1> and <mask2> are transferred into the <mask3> at the same time.",
            "Pick up the <mask1> and <mask2>, and transport them into the <mask3> together.",
            "Gather the <mask1> and <mask2>, and carefully place them into the <mask3> for organization.",
            "Move the <mask1> together with the <mask2> into the <mask3> to complete this step.",
            "Load the <mask1> and <mask2> into the <mask3> simultaneously.",
            "Bring both the <mask1> and <mask2> over and place them into the <mask3> for the next operation."
        ],
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "mask1": [
            "meat",
            "pumpkin",
            "bread",
            "pear"
        ],
        "mask2": [
            "pizza",
            "banana",
            "apple",
            "tomato"
        ],
        "mask3": [
            "plate",
            "bowl"
        ],
        "robot_roles": [
            "humanoid",
            "wheeled"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ],
                "R2": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ],
                "R2": [
                    "Reach",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ],
                "R2": [
                    "Grasp",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ],
                "R2": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ],
                "R2": [
                    "Place",
                    "<mask3>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
            }
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
            # G-Constraint 1: <mask1> should be moved to <mask3>
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
            # G-Constraint 2: <mask2> should be moved to <mask3>
            [
                {
                    "type": "asset",
                    "name": "<mask2>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
        ],
    },
   
    # 3 - Move plate/bowl to table and move 1 objects from cabinet to it with 2 robots
    # Note: Human should open cabinet for it have two hands.
    {
        "task_id": "3-1",
        "task_name": "set_plate_and_fork_on_table",
        "description": [
            "Place the <mask1> on the <mask2>, then fetch the <mask3> from the <mask4> and put it into the <mask1> to prepare the dining setup.",
            "Set the <mask1> onto the <mask2>, and retrieve the <mask3> from the <mask4>, placing it neatly inside the <mask1> for serving.",
            "Put the <mask1> on the <mask2> as the base, then collect the <mask3> from the <mask4> and place it into the <mask1> to get ready for a meal.",
            "Begin by placing the <mask1> onto the <mask2>, then fetch the <mask3> from the <mask4> and load it into the <mask1> to complete the preparation.",
            "Arrange the <mask1> on the <mask2>, and afterwards, retrieve the <mask3> from the <mask4>, placing it into the <mask1> to finalize the table setup.",
            "Start by setting the <mask1> on the <mask2>, then pick up the <mask3> from the <mask4> and put it into the <mask1> for organizing utensils.",
            "Place the <mask1> onto the <mask2> to create space for serving, then gather the <mask3> from the <mask4> and deposit it into the <mask1>.",
            "First, position the <mask1> on the <mask2>, then carefully retrieve the <mask3> from the <mask4> and place it inside the <mask1> to complete the dining arrangement."
        ],
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "mask1": [
            "plate",
            "bowl"
        ],
        "mask2": [
            "kitchen work area",
            "kitchen island area"
        ],
        "mask3": [
            "bread",
            "apple",
            "tomato",
            "banana"
        ],
        "mask4": [
            "cabinet"
        ],
        "robot_roles": [
            "humanoid",
            "wheeled"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask4>"
                ],
                "R2": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask4>"
                ],
                "R2": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Open",
                    "<mask4>"
                ],
                "R2": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ],
                "R2": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask3>"
                ],
                "R2": [
                    "Place",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask1>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "cabinet"
                ],
                "aligned_keys": [
                    "mask4"
                ]
            },
            {
                "name_key": "mask4",
                "pos": [
                    "room_cabinet"
                ],
            },
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "temporal_constraints": [
            # T-Constraint 1: <mask3> should be moved to <mask1>
            [
                # Sub-constraints 1: <mask1> should be moved to <mask2>
                [
                    {
                        "type": "asset",
                        "name": "<mask1>",
                        "is_satisfied": True,
                        "status": {
                            "pos.name": "<mask2>"
                        }
                    }
                ],
                # Sub-constraints 2: <mask3> should be moved to <mask1>
                [
                    {
                        "type": "asset",
                        "name": "<mask3>",
                        "is_satisfied": True,
                        "status": {
                            "pos.name": "<mask1>"
                        }
                    }
                ],
            ]
        ],
        "goal_constraints": [
            # G-Constraint 1: <mask1> should be moved to <mask2>
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask2>"
                    }
                }
            ],
            # G-Constraint 2: <mask3> should be moved to <mask1>
            [
                {
                    "type": "asset",
                    "name": "<mask3>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask1>"
                    }
                }
            ],
        ],
    },
    
    # 4 - Toaster bread and move 1 objects to table with 2 robots
    {
        "task_id": "4-1",
        "task_name": "toast_bread_and_set_plate",
        "description": [
            "Insert the <mask1> into the <mask2>, activate it to start the process, and place the <mask3> on the <mask4> to prepare for serving.",
            "Place the <mask1> into the <mask2>, turn it on, and meanwhile set the <mask3> onto the <mask4> for the breakfast setup.",
            "Begin by inserting the <mask1> into the <mask2>, switch it on, and at the same time place the <mask3> on the <mask4> to organize the workspace.",
            "Load the <mask1> into the <mask2>, start its operation, and arrange the <mask3> neatly on the <mask4>.",
            "Put the <mask1> into the <mask2>, turn on the device to begin, and place the <mask3> on the <mask4> to complete the setup."
        ],
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "mask1": [
            "bread"
        ],
        "mask2": [
            "toaster"
        ],
        "mask3": [
            "plate",
            "bowl"
        ],
        "mask4": [
            "kitchen work area",
            "kitchen island area"
        ],
        "robot_roles": [
            "humanoid",
            "wheeled"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ],
                "R2": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ],
                "R2": [
                    "Reach",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ],
                "R2": [
                    "Grasp",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ],
                "R2": [
                    "Move",
                    "<mask4>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask2>"
                ],
                "R2": [
                    "Place",
                    "<mask4>"
                ]
            },
            {
                "R1": [
                    "Interact",
                    "<mask2>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
            },
            {
                "name_key": "mask2",
                "pos": [
                    "room_toaster",
                ],
            },
            {
                "name_key": "mask3",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask4"
                ]
            },
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "temporal_constraints": [
            # T-Constraint 1: <mask1> should be moved to <mask2> and activate it
            [
                # Sub-constraints 1: <mask1> should be moved to <mask2>
                [
                    {
                        "type": "asset",
                        "name": "<mask1>",
                        "is_satisfied": True,
                        "status": {
                            "pos.name": "<mask2>"
                        }
                    }
                ],
                # Sub-constraints 2: toaster should be activated
                [
                    {
                        "type": "asset",
                        "name": "toaster",
                        "is_satisfied": True,
                        "status": {
                            "is_activated": True
                        }
                    }
                ],
            ],
        ],
        "goal_constraints": [
            # G-Constraint 1: <mask3> should be moved to <mask4>
            [
                {
                    "type": "asset",
                    "name": "<mask3>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask4>"
                    }
                }
            ],
            # G-Constraint 2: toaster should be activated
            [
                {
                    "type": "asset",
                    "name": "toaster",
                    "is_satisfied": True,
                    "status": {
                        "is_activated": True
                    }
                }
            ]
        ]
    },
    
    # 5 - Move 2 objects to cabinet with 2 robots
    # Note: Human should open cabinet for it have two hands.
    {
        "task_id": "5-1",
        "task_name": "clear_table_with_two_robots_and_put_in_cabinet",
        "description": [
            "Put the <mask1> and the <mask2> into the <mask3> to clean up the workspace.",
            "Carefully place both the <mask1> and the <mask2> into the <mask3> to tidy up the area.",
            "Transfer the <mask1> along with the <mask2> into the <mask3> for proper storage.",
            "Move the <mask1> and the <mask2> together into the <mask3> to keep the workspace organized.",
            "Collect the <mask1> and <mask2>, and place them neatly into the <mask3> to finish cleaning.",
            "Gather the <mask1> and the <mask2>, and store them inside the <mask3> to clear the space.",
            "Ensure that both the <mask1> and <mask2> are placed into the <mask3> to maintain order in the workspace.",
            "Pick up the <mask1> and <mask2> and carefully deposit them into the <mask3> for cleanup.",
            "Put away the <mask1> and <mask2> by placing them into the <mask3> to prepare for the next task.",
            "Store the <mask1> together with the <mask2> inside the <mask3> to make the area neat and clean."
        ],
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "mask1": [
            "pumpkin",
            "bread",
            "apple",
            "peach",
            "tomato",
        ],
        "mask2": [
            "scissors",
            "spoon",
            "fork",
            "knife",
        ],
        "mask3": [
            "cabinet"
        ],
        "robot_roles": [
            "humanoid",
            "wheeled"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ],
                "R2": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ],
                "R2": [
                    "Reach",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ],
                "R2": [
                    "Grasp",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ],
                "R2": [
                    "Move",
                    "<mask3>"
                ],
            },
            {
                "R1": [
                    "Reach",
                    "<mask3>"
                ],
            },
            {
                "R1": [
                    "Open",
                    "<mask3>"
                ],
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ],
                "R2": [
                    "Place",
                    "<mask3>"
                ]
            },
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
            },
            {
                "name_key": "mask3",
                "pos": [
                    "room_cabinet"
                ],
            },
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
            # G-Constraint 1: <mask3> should be moved to <mask4>
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
            [
                {
                    "type": "asset",
                    "name": "<mask2>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },
    {
        "task_id": "5-2",
        "task_name": "clear_table_with_two_robots_and_put_in_cabinet",
        "description": [
            "Put the <mask1> and the <mask2> into the <mask3> to clean up the workspace.",
            "Carefully place both the <mask1> and the <mask2> into the <mask3> to tidy up the area.",
            "Transfer the <mask1> along with the <mask2> into the <mask3> for proper storage.",
            "Move the <mask1> and the <mask2> together into the <mask3> to keep the workspace organized.",
            "Collect the <mask1> and <mask2>, and place them neatly into the <mask3> to finish cleaning.",
            "Gather the <mask1> and the <mask2>, and store them inside the <mask3> to clear the space.",
            "Ensure that both the <mask1> and <mask2> are placed into the <mask3> to maintain order in the workspace.",
            "Pick up the <mask1> and <mask2> and carefully deposit them into the <mask3> for cleanup.",
            "Put away the <mask1> and <mask2> by placing them into the <mask3> to prepare for the next task.",
            "Store the <mask1> together with the <mask2> inside the <mask3> to make the area neat and clean."
        ],
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "mask1": [
            "pumpkin",
            "bread",
            "apple",
            "peach",
            "tomato",
        ],
        "mask2": [
            "scissors",
            "spoon",
            "fork",
            "knife",
        ],
        "mask3": [
            "cabinet"
        ],
        "robot_roles": [
            "wheeled",
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ],
                "R2": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ],
                "R2": [
                    "Reach",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ],
                "R2": [
                    "Grasp",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ],
                "R2": [
                    "Move",
                    "<mask3>"
                ],
            },
            {
                "R2": [
                    "Reach",
                    "<mask3>"
                ],
            },
            {
                "R2": [
                    "Open",
                    "<mask3>"
                ],
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ],
                "R2": [
                    "Place",
                    "<mask3>"
                ]
            },
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
            },
            {
                "name_key": "mask3",
                "pos": [
                    "room_cabinet"
                ],
            },
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
            # G-Constraint 1: <mask3> should be moved to <mask4>
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
            [
                {
                    "type": "asset",
                    "name": "<mask2>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },
    
    # 6 - Move 2 objects to one place with 1 Human
    # Note: Human have two hands and should pick up two objects together
    {
        "task_id": "6-1",
        "task_name": "sequential_pick_two_and_place",
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "description": [
            "Please tidy up by getting the <mask1> and <mask2> into the <mask3>.",
            "Both the <mask1> and <mask2> belong in the <mask3>; make it happen.",
            "Could you place the <mask1> along with the <mask2> inside the <mask3>?",
            "Let's store the <mask1> and the <mask2> safely in the <mask3>.",
            "Move those two items — the <mask1> and <mask2> — into the <mask3>.",
            "I need the <mask1> with the <mask2> transferred to the <mask3> pronto!",
            "Organise things by dropping the <mask1> and <mask2> into the <mask3>.",
            "Make sure the <mask1> and <mask2> end up inside the <mask3>.",
            "Time to clear the counter: get <mask1> and <mask2>, put them in the <mask3>.",
            "Kindly relocate both <mask1> and <mask2> to the <mask3> for me."
        ],
        "mask1": [
            "banana",
            "apple",
            "tomato",
            "meat"
        ],
        "mask2": [
            "pear",
            "bread",
            "pumpkin",
            "green peas"
        ],
        "mask3": [
            "bowl",
            "plate"
        ],
        "robot_roles": [
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ]
            }
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
            [
                {
                    "type": "asset",
                    "name": "<mask2>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },
    
    # 7 - Wash 1 objects and place to the plate with 1 robot
    {
        "task_id": "7-1",
        "task_name": "wash_fruit_and_serve",
        "layout_idx": [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "description": [
            "Rinse the <mask1> in <mask3> and set it into the <mask2> for serving.",
            "Freshen the <mask1> under the tap on <mask3>, then drop it in the <mask2>.",
            "Give the <mask1> a quick wash at the <mask3> and place it inside the <mask2>.",
            "Clean the <mask1> at the <mask3>, then deliver it into the <mask2>.",
            "Make sure the <mask1> is washed at the <mask3> before resting it in the <mask2>.",
            "Run water over the <mask1> at the <mask3>, then arrange it neatly in the <mask2>.",
            "Wash off the <mask1> at the <mask3> and move it into the <mask2>.",
            "Rinse off the <mask1> at the <mask3> and leave it in the <mask2> when finished.",
            "Use the tap to clean the <mask1> at the <mask3>; afterward, transfer it to the <mask2>.",
            "Get the <mask1> washed in <mask3> and placed in the <mask2> so it's ready to eat."
        ],
        "mask1": [
            "apple",
            "pear",
            "tomato",
            "peach",
            "banana"
        ],
        "mask2": [
            "bowl",
            "plate"
        ],
        "mask3": [
            "sink",
        ],
        "robot_roles": [
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "sink"
                ]
            },
            {
                "R1": [
                    "Place",
                    "sink"
                ]
            },
            {
                "R1": [
                    "Interact",
                    "sink"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask2>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "room"
                ]
            }
        ],
        "idle_robot_roles": [
            "dog",
            "wheeled"
        ],
        "temporal_constraints": [
            [
                [
                    {
                        "type": "asset",
                        "name": "<mask1>",
                        "is_satisfied": True,
                        "status": {
                            "pos.name": "sink"
                        }
                    }
                ],
                [
                    {
                        "type": "asset",
                        "name": "<mask3>",
                        "is_satisfied": True,
                        "status": {
                            "is_activated": True
                        }
                    }
                ]
            ]
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask2>"
                    }
                }
            ]
        ]
    },
    {
        "task_id": "7-2",
        "task_name": "wash_fruit_and_serve",
        "layout_idx": [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "description": [
            "Rinse the <mask1> in <mask3> and set it into the <mask2> for serving.",
            "Freshen the <mask1> under the tap on <mask3>, then drop it in the <mask2>.",
            "Give the <mask1> a quick wash at the <mask3> and place it inside the <mask2>.",
            "Clean the <mask1> at the <mask3>, then deliver it into the <mask2>.",
            "Make sure the <mask1> is washed at the <mask3> before resting it in the <mask2>.",
            "Run water over the <mask1> at the <mask3>, then arrange it neatly in the <mask2>.",
            "Wash off the <mask1> at the <mask3> and move it into the <mask2>.",
            "Rinse off the <mask1> at the <mask3> and leave it in the <mask2> when finished.",
            "Use the tap to clean the <mask1> at the <mask3>; afterward, transfer it to the <mask2>.",
            "Get the <mask1> washed in <mask3> and placed in the <mask2> so it's ready to eat."
        ],
        "mask1": [
            "apple",
            "pear",
            "tomato",
            "peach",
            "banana"
        ],
        "mask2": [
            "bowl",
            "plate"
        ],
        "mask3": [
            "sink",
        ],
        "robot_roles": [
            "wheeled"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "sink"
                ]
            },
            {
                "R1": [
                    "Place",
                    "sink"
                ]
            },
            {
                "R1": [
                    "Interact",
                    "sink"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask2>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "room"
                ]
            }
        ],
        "idle_robot_roles": [
            "dog",
            "arm",
            "wheeled"
        ],
        "temporal_constraints": [
            [
                [
                    {
                        "type": "asset",
                        "name": "<mask1>",
                        "is_satisfied": True,
                        "status": {
                            "pos.name": "sink"
                        }
                    }
                ],
                [
                    {
                        "type": "asset",
                        "name": "<mask3>",
                        "is_satisfied": True,
                        "status": {
                            "is_activated": True
                        }
                    }
                ]
            ]
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask2>"
                    }
                }
            ]
        ]
    },
        
    # 8 - Cut 1 objects using knife on the board with human and wheeled
    {
        "task_id": "8-1",
        "task_name": "cut_fruit_on_board",
        "description": [
            "Use the <mask1> to slice the <mask3> on the <mask2>.",
            "Cut the <mask3> with the <mask1> once everything is on the <mask2>.",
            "Get the <mask3> to the <mask2> and give it a clean cut with the <mask1>.",
            "Lay the <mask3> on the <mask2> and carve it using the <mask1>.",
            "Set the <mask3> on the <mask2>, then apply the <mask1> to slice it.",
            "Prepare the <mask2> with the <mask3> and proceed to cut it using the <mask1>.",
            "Position the <mask3> on the <mask2>; slice it neatly with the <mask1>.",
            "Place the <mask3> on the <mask2> and finish by cutting it with the <mask1>.",
        ],
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "mask1": [
            "knife"
        ],
        "mask2": [
            "wooden cutting board"
        ],
        "mask3": [
            "apple",
            "pear",
            "peach"
        ],
        "robot_roles": [
            "humanoid",
            "wheeled"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ],
                "R2": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ],
                "R2": [
                    "Reach",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ],
                "R2": [
                    "Grasp",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ],
                "R2": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask2>"
                ],
                "R2": [
                    "Place",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Interact",
                    "<mask1>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen island area"
                ]
            }
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "temporal_constraints": [
            [
                [   # 先确保水果已在砧板上
                    {
                        "type": "asset",
                        "name": "<mask3>",
                        "is_satisfied": True,
                        "status": {
                            "pos.name": "<mask2>"
                        }
                    },
                    # 刀在砧板上
                    {
                        "type": "asset",
                        "name": "<mask1>",
                        "is_satisfied": True,
                        "check_pos_type": "aligned",
                        "status": {
                            "pos.name": "<mask2>"
                        }
                    }
                ],
                [   # 然后刀被激活（表示切割已执行）
                    {
                        "type": "asset",
                        "name": "<mask1>",
                        "is_satisfied": True,
                        "status": {
                            "is_activated": True
                        }
                    }
                ]
            ]
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "is_activated": True
                    }
                }
            ]
        ]
    },
    {
        "task_id": "8-2",
        "task_name": "cut_fruit_on_board",
        "description": [
            "Use the <mask1> to slice the <mask3> on the <mask2>.",
            "Cut the <mask3> with the <mask1> once everything is on the <mask2>.",
            "Get the <mask3> to the <mask2> and give it a clean cut with the <mask1>.",
            "Lay the <mask3> on the <mask2> and carve it using the <mask1>.",
            "Set the <mask3> on the <mask2>, then apply the <mask1> to slice it.",
            "Prepare the <mask2> with the <mask3> and proceed to cut it using the <mask1>.",
            "Position the <mask3> on the <mask2>; slice it neatly with the <mask1>.",
            "Place the <mask3> on the <mask2> and finish by cutting it with the <mask1>."
        ],
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "mask1": [
            "knife"
        ],
        "mask2": [
            "wooden cutting board"
        ],
        "mask3": [
            "apple",
            "pear",
            "peach"
        ],
        "robot_roles": [
            "wheeled",
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ],
                "R2": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ],
                "R2": [
                    "Reach",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ],
                "R2": [
                    "Grasp",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ],
                "R2": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask2>"
                ],
                "R2": [
                    "Place",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Interact",
                    "<mask1>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen island area"
                ]
            }
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "temporal_constraints": [
            [
                [   # 先确保水果已在砧板上
                    {
                        "type": "asset",
                        "name": "<mask3>",
                        "is_satisfied": True,
                        "status": {
                            "pos.name": "<mask2>"
                        }
                    },
                    # 刀在砧板上
                    {
                        "type": "asset",
                        "name": "<mask1>",
                        "is_satisfied": True,
                        "check_pos_type": "aligned",
                        "status": {
                            "pos.name": "<mask2>"
                        }
                    }
                ],
                [   # 然后刀被激活（表示切割已执行）
                    {
                        "type": "asset",
                        "name": "<mask1>",
                        "is_satisfied": True,
                        "status": {
                            "is_activated": True
                        }
                    }
                ]
            ]
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "is_activated": True
                    }
                }
            ]
        ]
    },

    # 9 - Cut 2 objects using knife on the board with human and wheeled
    # Note: Human have two hands and should pick up two objects together, fetch should pick knife to cut the fruit
    {
        "task_id": "9-1",
        "task_name": "cut_two_fruits_on_board",
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "description": [
            "Slice the <mask3> and <mask4> on the <mask2> using the <mask1>.",
            "Bring the <mask3> and <mask4> to the <mask2> and chop them with the <mask1>.",
            "Move the <mask3> together with the <mask4> onto the <mask2>, then cut them using the <mask1>.",
            "Carry the <mask3> plus the <mask4> to the <mask2>; the <mask1> will handle the slicing.",
            "Place both the <mask3> and <mask4> on the <mask2> for cutting with the <mask1>.",
            "Transport the <mask3> with the <mask4> onto the <mask2> and dice them with the <mask1>.",
            "Deliver the <mask3> alongside the <mask4> to the <mask2> for a neat cut with the <mask1>.",
            "Set the <mask3> and <mask4> on the <mask2>, then slice them cleanly with the <mask1>.",
            "Lay the <mask3> and <mask4> on the <mask2>, then carve them using the <mask1>.",
            "Arrange the <mask3> next to the <mask4> on the <mask2> and chop them briskly with the <mask1>.",
            "Quick, give both the <mask3> and <mask4> a good chop on the <mask2> with that <mask1>!",
            "Would you mind setting the <mask3> and <mask4> on the <mask2> and slicing them with the <mask1>?",
            "Let's get cooking—move the <mask3> plus <mask4> onto the <mask2> and work the <mask1> on them.",
            "When you have a moment, place the <mask3> beside the <mask4> on the <mask2>, then trim them with the <mask1>.",
            "All right, partner: line up the <mask3> and <mask4> on the <mask2> for a tidy cut using the <mask1>.",
            "Time's ticking—transport the <mask3> with the <mask4> to the <mask2> and dice them up using the <mask1>.",
            "Kindly arrange the <mask3> and <mask4> on the <mask2>; the <mask1> will handle the rest.",
            "Could you pop the <mask3> next to the <mask4> on the <mask2> and slice them clean with the <mask1>?",
            "Let's tidy the board: deliver the <mask3> plus the <mask4>, then carve away with the <mask1>.",
            "Here's the plan—stack the <mask3> and <mask4> on the <mask2>, then give them a brisk chop with the <mask1>."
        ],
        "mask1": [
            "knife"
        ],
        "mask2": [
            "wooden cutting board"
        ],
        "mask3": [
            "apple",
            "pear",
            "peach"
        ],
        "mask4": [
            "banana",
            "tomato",
            "bread"
        ],
        "robot_roles": [
            "humanoid",
            "wheeled"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ],
                "R2": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask3>"
                ],
                "R2": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask3>"
                ],
                "R2": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask4>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask4>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask4>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ],
                "R2": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask2>"
                ]
            },
            {
                "R2": [
                    "Interact",
                    "<mask1>"
                ]
            }        # slicing action
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask4",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen island area"
                ]
            }
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "temporal_constraints": [
            [
                [   
                    # 两种水果都在砧板上
                    {
                        "type": "asset",
                        "name": "<mask3>",
                        "is_satisfied": True,
                        "status": {
                            "pos.name": "<mask2>"
                        }
                    },
                    {
                        "type": "asset",
                        "name": "<mask4>",
                        "is_satisfied": True,
                        "status": {
                            "pos.name": "<mask2>"
                        }
                    },
                    # 刀在砧板上
                    {
                        "type": "asset",
                        "name": "<mask1>",
                        "is_satisfied": True,
                        "check_pos_type": "aligned",
                        "status": {
                            "pos.name": "<mask2>"
                        }
                    }
                ],
                [   
                    # ❷ 才能激活刀（表示切割完成）
                    {
                        "type": "asset",
                        "name": "<mask1>",
                        "is_satisfied": True,
                        "status": {
                            "is_activated": True
                        }
                    }
                ]
            ]
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "is_activated": True
                    }
                }
            ]
        ]
    },

    # 10 - Visual-searching for the object in the cabinet and serve it
    # Note: The bread is in the cabinet and the robot should check the cabinet first
    #       before serving it on the plate or bowl
    {
        "task_id": "10-1",
        "task_name": "serve_bread_after_checking_cabinet",
        "description": [
            "Put the <mask1> on the <mask3>; if it's not out here, it could be hiding in the <mask2>, so look carefully.",
            "Place the <mask1> onto the <mask3>. Should it be missing, check the <mask2> before proceeding.",
            "Serve the <mask1> on the <mask3>. If you don't see it nearby, it might be inside the <mask2>—have a look.",
            "Get the <mask1> onto the <mask3>; remember, it may have been stored in the <mask2>.",
            "Move the <mask1> to the <mask3>. In case it isn't visible, inspect the <mask2> first.",
            "Transfer the <mask1> to the <mask3>. If it's nowhere outside, open the <mask2> and fetch it.",
            "Lay the <mask1> on the <mask3>. Sometimes it's kept in the <mask2>, so check there if needed.",
            "Set the <mask1> onto the <mask3>; when it's not in sight, it could be inside the <mask2>—take a peek.",
            "Place the <mask1> neatly on the <mask3>. If it's absent, the <mask2> is worth checking.",
            "Deliver the <mask1> to the <mask3>. Should it be hidden, open the <mask2> and retrieve it."
        ],
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "mask1": [
            "bread",
            "apple",
            "banana"
        ],
        "mask2": [
            "cabinet"
        ],
        "mask3": [
            "plate",
            "bowl"
        ],
        "robot_roles": [
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Open",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "cabinet"
                ],          # 当前确实在柜子里
                "exclude_keys": []
            },
            {
                "name_key": "mask2",
                "pos": [
                    "room_cabinet"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "kitchen island area",
                    "kitchen work area"
                ]
            }
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },
    {
        "task_id": "10-2",
        "task_name": "serve_bread_from_counter",
        "description": [
            "Put the <mask1> on the <mask3>; if it isn't on the counter, it might still be in the <mask2>, so check there.",
            "Place the <mask1> onto the <mask3>. Should it be missing, have a quick look inside the <mask2>.",
            "Serve the <mask1> on the <mask3>. If it's not out here, the <mask2> is worth a peek.",
            "Move the <mask1> to the <mask3>. In case it's not visible, you may need to inspect the <mask2>.",
            "Transfer the <mask1> to the <mask3>. If you can't spot it, open the <mask2> and retrieve it."
        ],
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
        ],
        "mask1": [
            "bread",
            "apple",
            "banana"
        ],
        "mask2": [
            "cabinet"
        ],
        "mask3": [
            "plate",
            "bowl"
        ],
        "robot_roles": [
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area",
                    "kitchen island area"
                ],
                "exclude_keys": [
                    "mask2"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "room_cabinet"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "kitchen island area",
                    "kitchen work area"
                ]
            }
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },

    # 11 - Visual-searching for ensuring bowl & plate on the table
    {
        "task_id": "11-1",
        "task_name": "bring_plate_to_table_bowl_already_there",
        "layout_idx": [
            1,
            3,
            6,
            9
        ],
        "description": [
            "Take a look at the <mask3>. If you don't see both a <mask1> and a <mask2> there, bring over whichever dish is missing.",
            "Survey the <mask3> first; once you spot which item isn't present—the <mask1> or the <mask2>—carry it to the table.",
            "Glance at the <mask3> and confirm it holds one <mask1> and one <mask2>. Fetch the dish that's still absent.",
            "Check the <mask3> with your sensors. Should it lack either the <mask1> or the <mask2>, deliver the missing one.",
            "Observe the <mask3> for both the <mask1> and <mask2>. Bring along whichever plate or bowl you don't detect.",
            "Scan the <mask3>. If one of the two dishes—the <mask1> or the <mask2>—isn't present, place it there.",
            "Look over the <mask3>; whichever of the <mask1> or <mask2> is not already resting there, go get it and set it down.",
            "Examine the <mask3> visually. When you find only one dish, supply the other so both the <mask1> and <mask2> are in position.",
            "Inspect the <mask3>. Any dish you can't see—whether it's the <mask1> or the <mask2>—needs to be fetched and placed.",
            "Verify with a quick look that the <mask3> hosts both the <mask1> and <mask2>. Retrieve and add the missing one if necessary."
        ],
        "mask1": [
            "bowl"
        ],
        "mask2": [
            "plate"
        ],
        "mask3": [
            "table"
        ],
        "robot_roles": [
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "table"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen work area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            },
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
            [
                {
                    "type": "asset",
                    "name": "<mask2>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },
    {
        "task_id": "11-2",
        "task_name": "bring_bowl_to_table_plate_already_there",
        "layout_idx": [
            1,
            3,
            6,
            9
        ],
        "description": [
            "Take a look at the <mask3>. If you don't see both a <mask1> and a <mask2> there, bring over whichever dish is missing.",
            "Survey the <mask3> first; once you spot which item isn't present—the <mask1> or the <mask2>—carry it to the table.",
            "Glance at the <mask3> and confirm it holds one <mask1> and one <mask2>. Fetch the dish that's still absent.",
            "Check the <mask3> with your sensors. Should it lack either the <mask1> or the <mask2>, deliver the missing one.",
            "Observe the <mask3> for both the <mask1> and <mask2>. Bring along whichever plate or bowl you don't detect.",
            "Scan the <mask3>. If one of the two dishes—the <mask1> or the <mask2>—isn't present, place it there.",
            "Look over the <mask3>; whichever of the <mask1> or <mask2> is not already resting there, go get it and set it down.",
            "Examine the <mask3> visually. When you find only one dish, supply the other so both the <mask1> and <mask2> are in position.",
            "Inspect the <mask3>. Any dish you can't see—whether it's the <mask1> or the <mask2>—needs to be fetched and placed.",
            "Verify with a quick look that the <mask3> hosts both the <mask1> and <mask2>. Retrieve and add the missing one if necessary."
        ],
        "mask1": [
            "bowl"
        ],
        "mask2": [
            "plate"
        ],
        "mask3": [
            "table"
        ],
        "robot_roles": [
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask2",
                "pos": [
                    "table"
                ]
            },
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            },
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
            [
                {
                    "type": "asset",
                    "name": "<mask2>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },
    {
        "task_id": "11-3",
        "task_name": "bring_plate_and_bowl_to_table",
        "layout_idx": [
            1,
            3,
            6,
            9
        ],
        "description": [
            "Take a look at the <mask3>. If you don't see both a <mask1> and a <mask2> there, bring over whichever dish is missing.",
            "Survey the <mask3> first; once you spot which item isn't present—the <mask1> or the <mask2>—carry it to the table.",
            "Glance at the <mask3> and confirm it holds one <mask1> and one <mask2>. Fetch the dish that's still absent.",
            "Check the <mask3> with your sensors. Should it lack either the <mask1> or the <mask2>, deliver the missing one.",
            "Observe the <mask3> for both the <mask1> and <mask2>. Bring along whichever plate or bowl you don't detect.",
            "Scan the <mask3>. If one of the two dishes—the <mask1> or the <mask2>—isn't present, place it there.",
            "Look over the <mask3>; whichever of the <mask1> or <mask2> is not already resting there, go get it and set it down.",
            "Examine the <mask3> visually. When you find only one dish, supply the other so both the <mask1> and <mask2> are in position.",
            "Inspect the <mask3>. Any dish you can't see—whether it's the <mask1> or the <mask2>—needs to be fetched and placed.",
            "Verify with a quick look that the <mask3> hosts both the <mask1> and <mask2>. Retrieve and add the missing one if necessary."
        ],
        "mask1": [
            "bowl"
        ],
        "mask2": [
            "plate"
        ],
        "mask3": [
            "table"
        ],
        "robot_roles": [
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen work area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            },
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
            [
                {
                    "type": "asset",
                    "name": "<mask2>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },

    # 12 - Visual-searching for ensuring all fruit on the table
    {
        "task_id": "12-1",
        "task_name": "ensure_all_fruits_on_table",
        "layout_idx": [
            1,
            3,
            6
        ],
        "description": [
            "Inspect the <mask3> thoroughly. If you find that both a <mask1> and a <mask2> are missing, fetch the absent fruit from wherever it may be, including cabinet.",
            "Survey the <mask3> closely. Identify which fruit—the <mask1> or the <mask2>—is absent, then bring it to the table from its current location, which may include cabinet.",
            "Glance at the <mask3> to confirm both a <mask1> and a <mask2> are present. If not, retrieve the missing fruit, ensuring to check all possible locations, including cabinet.",
            "Utilize your sensors to check the <mask3>. If either the <mask1> or the <mask2> is missing, retrieve it from wherever it might be, including cabinet.",
            "Observe the <mask3> for both the <mask1> and <mask2>. If one is missing, bring it along from any location, such as cabinet.",
            "Scan the <mask3> for any missing fruits—the <mask1> or the <mask2>. Place them on the table, checking cabinet if necessary.",
            "Examine the <mask3> closely. If either the <mask1> or the <mask2> is not present, retrieve it from its current location, including cabinet, and place it on the table.",
            "Inspect the <mask3> visually. Ensure both the <mask1> and the <mask2> are present. If not, fetch and place the missing fruit, checking all areas including cabinet.",
            "Verify with a quick inspection that the <mask3> holds both the <mask1> and the <mask2>. Retrieve the missing fruit from wherever it is, including cabinet, if necessary.",
            "Thoroughly check the <mask3> to ensure both the <mask1> and the <mask2> are present. Retrieve the missing fruit, checking all possible locations, including cabinet."
        ],
        "mask1": [
            "apple",
            "pear",
            "peach"
        ],
        "mask2": [
            "banana",
            "tomato"
        ],
        "mask3": [
            "table"
        ],
        "robot_roles": [
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "table"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen work area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            }
        ],
        "idle_robot_roles": [
            "dog",
            "arm",
            "wheeled"
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
            [
                {
                    "type": "asset",
                    "name": "<mask2>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },
    {
        "task_id": "12-2",
        "task_name": "ensure_all_fruits_on_table",
        "layout_idx": [
            1,
            3,
            6
        ],
        "description": [
            "Inspect the <mask3> thoroughly. If you find that both a <mask1> and a <mask2> are missing, fetch the absent fruit from wherever it may be, including cabinet.",
            "Survey the <mask3> closely. Identify which fruit—the <mask1> or the <mask2>—is absent, then bring it to the table from its current location, which may include cabinet.",
            "Glance at the <mask3> to confirm both a <mask1> and a <mask2> are present. If not, retrieve the missing fruit, ensuring to check all possible locations, including cabinet.",
            "Utilize your sensors to check the <mask3>. If either the <mask1> or the <mask2> is missing, retrieve it from wherever it might be, including cabinet.",
            "Observe the <mask3> for both the <mask1> and <mask2>. If one is missing, bring it along from any location, such as cabinet.",
            "Scan the <mask3> for any missing fruits—the <mask1> or the <mask2>. Place them on the table, checking cabinet if necessary.",
            "Examine the <mask3> closely. If either the <mask1> or the <mask2> is not present, retrieve it from its current location, including cabinet, and place it on the table.",
            "Inspect the <mask3> visually. Ensure both the <mask1> and the <mask2> are present. If not, fetch and place the missing fruit, checking all areas including cabinet.",
            "Verify with a quick inspection that the <mask3> holds both the <mask1> and the <mask2>. Retrieve the missing fruit from wherever it is, including cabinet, if necessary.",
            "Thoroughly check the <mask3> to ensure both the <mask1> and the <mask2> are present. Retrieve the missing fruit, checking all possible locations, including cabinet."
        ],
        "mask1": [
            "apple",
            "pear",
            "peach"
        ],
        "mask2": [
            "banana",
            "tomato"
        ],
        "mask3": [
            "table"
        ],
        "robot_roles": [
            "humanoid"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask2",
                "pos": [
                    "table"
                ]
            },
            {
                "name_key": "mask1",
                "pos": [
                    "kitchen work area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            }
        ],
        "idle_robot_roles": [
            "dog",
            "arm",
            "wheeled"
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
            [
                {
                    "type": "asset",
                    "name": "<mask2>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },
    {
        "task_id": "12-3",
        "task_name": "ensure_all_fruits_on_table",
        "layout_idx": [
            1,
            3,
            6
        ],
        "description": [
            "Inspect the <mask3> thoroughly. If you find that both a <mask1> and a <mask2> are missing, fetch the absent fruit from wherever it may be, including <mask4>.",
            "Survey the <mask3> closely. Identify which fruit—the <mask1> or the <mask2>—is absent, then bring it to the table from its current location, which may include <mask4>.",
            "Glance at the <mask3> to confirm both a <mask1> and a <mask2> are present. If not, retrieve the missing fruit, ensuring to check all possible locations, including <mask4>.",
            "Utilize your sensors to check the <mask3>. If either the <mask1> or the <mask2> is missing, retrieve it from wherever it might be, including <mask4>.",
            "Observe the <mask3> for both the <mask1> and <mask2>. If one is missing, bring it along from any location, such as <mask4>.",
            "Scan the <mask3> for any missing fruits—the <mask1> or the <mask2>. Place them on the table, checking <mask4> if necessary.",
            "Examine the <mask3> closely. If either the <mask1> or the <mask2> is not present, retrieve it from its current location, including <mask4>, and place it on the table.",
            "Inspect the <mask3> visually. Ensure both the <mask1> and the <mask2> are present. If not, fetch and place the missing fruit, checking all areas including <mask4>.",
            "Verify with a quick inspection that the <mask3> holds both the <mask1> and the <mask2>. Retrieve the missing fruit from wherever it is, including <mask4>, if necessary.",
            "Thoroughly check the <mask3> to ensure both the <mask1> and the <mask2> are present. Retrieve the missing fruit, checking all possible locations, including <mask4>."
        ],
        "mask1": [
            "apple",
            "pear",
            "peach"
        ],
        "mask2": [
            "banana",
            "tomato"
        ],
        "mask3": [
            "table"
        ],
        "mask4": [
            "cabinet"
        ],
        "robot_roles": [
            "humanoid",
            "wheeled"
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask4>"
                ],
                "R2": [
                    "Move",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask4>"
                ],
                "R2": [
                    "Reach",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Open",
                    "<mask4>"
                ],
                "R2": [
                    "Grasp",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ],
                "R2": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Reach",
                    "<mask1>"
                ],
                "R2": [
                    "Place",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Move",
                    "<mask3>"
                ]
            },
            {
                "R1": [
                    "Place",
                    "<mask3>"
                ]
            },
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "cabinet"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "kitchen work area"
                ],
                "exclude_keys": [
                    "mask3"
                ]
            },
            {
                "name_key": "mask4",
                "pos": [
                    "room_cabinet"
                ]
            },
        ],
        "idle_robot_roles": [
            "dog",
            "arm"
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
            [
                {
                    "type": "asset",
                    "name": "<mask2>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ]
        ]
    },
    
    # 13 - dog problem200
    {
        "task_id": "13-1",
        "task_name": "dog_check_environment",
        "layout_idx": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
        ],
        "description": [
            "Inspect the environment of <mask1>.",
            "Take a look around <mask1> and check its surroundings.",
            "Examine the environment near <mask1>.",
            "Observe the space around <mask1>.",
            "Explore the nearby environment of <mask1>.",
            "Assess the area surrounding <mask1>.",
            "Inspect the vicinity of <mask1> carefully.",  
        ],
        "mask1": [
            "drawer",
            "fridge",
            "oven"
        ],
        "robot_roles": [
            "dog",
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask1>"
                ],
            },
            {
                "R1": [
                    "Interact",
                    "<mask1>"
                ],
            },
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "mask1"
                ]
            },
        ],
        "idle_robot_roles": [
            "arm"
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "is_activated": True
                    }
                }
            ],
        ]
    },
    {
        "task_id": "13-2",
        "task_name": "dog_push_box_for_two_panda_transport",
        "layout_idx": [
            3,
            6,
        ],
        "description": [
            "Move the <mask1> to the <mask3>. If the destination is too far, use the <mask2> to house the <mask1>, transport the <mask2> and fetch the <mask1>.",
            "Carry the <mask1> over to the <mask3>. If it's a long way, place the <mask1> into a <mask2> first, then move the <mask2> and retrieve the <mask1> afterwards.",
            "Relocate the <mask1> to the <mask3>. If it's too far to carry directly, <mask2> the <mask1>, move the <mask2>, and then remove the <mask1>.",
            "Bring the <mask1> to the <mask3>. When the <mask3> is too far away, pack the <mask1> into a <mask2>, transport the <mask2>, and take out the <mask1> at the destination.",
            "Move the <mask1> toward the <mask3>; if the route is too long, use a <mask2> to enclose the <mask1>, transfer the <mask2>, then retrieve the <mask1>.",
            "Shift the <mask1> to the <mask3> location. If carrying it directly isn't feasible, first house the <mask1> in a <mask2>, move the <mask2>, and extract the <mask1> at the sink.",
            "Deliver the <mask1> to the <mask3>. If distance makes direct handling difficult, load the <mask1> into a <mask2>, transport the <mask2>, and then unload the <mask1>.",
            "Take the <mask1> to the <mask3>. If it's too far to move it conveniently, first secure it inside a <mask2>, move the <mask2>, and fetch the <mask1> afterward.",
            "Get the <mask1> over to the <mask3>. In case it's too distant, put the <mask1> into a <mask2>, shift the <mask2> to the <mask3>, and then retrieve the <mask1>.",
        ],
        "mask1": [
            "apple",
            "pumpkin",
            "meat",
            "pear",
            "peach",
            "fork",
            "spoon"
        ],
        "mask2": [
            "cardboardbox"
        ],
        "mask3": [
            "sink"
        ],
        "robot_roles": [
            "dog",
            "arm",
            "arm",
        ],
        "ground_truth": [
            {
                "R1": [
                    "Move",
                    "<mask2>"
                ],
                "R2": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R1": [
                    "Push",
                    "<mask2>",
                    "R2"
                ],
                "R2": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R2": [
                    "Place",
                    "<mask2>"
                ]
            },
            {
                "R1": [
                    "Push",
                    "<mask2>",
                    "R3"
                ]
            },
            {
                "R3": [
                    "Reach",
                    "<mask1>"
                ]
            },
            {
                "R3": [
                    "Grasp",
                    "<mask1>"
                ]
            },
            {
                "R3": [
                    "Place",
                    "<mask3>"
                ]
            }
        ],
        "init_pos": [
            {
                "name_key": "mask1",
                "pos": [
                    "R2"
                ]
            },
            {
                "name_key": "mask2",
                "pos": [
                    "groundA"
                ]
            },
            {
                "name_key": "mask3",
                "pos": [
                    "R3"
                ]
            },
            {
                "name_key": "R2",
                "pos": [
                    "pandaB"
                ]
            },
            {
                "name_key": "R3",
                "pos": [
                    "pandaA"
                ]
            },
        ],
        "idle_robot_roles": [
        ],
        "goal_constraints": [
            [
                {
                    "type": "asset",
                    "name": "<mask1>",
                    "is_satisfied": True,
                    "status": {
                        "pos.name": "<mask3>"
                    }
                }
            ],
        ]
    },
    
]