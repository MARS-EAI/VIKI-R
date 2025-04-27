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
            "kitchen island area"
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
                        "name": "bread",
                        "is_satisfied": True,
                        "status": {
                            "pos.name": "toaster"
                        }
                    }
                ],
                # Sub-constraints 2: <mask3> should be moved to <mask1>
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
    # 6 - Move 2 objects to one place with Human
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
    # 7 - Wash 1 objects and place to the plate
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
            "Get the <mask1> washed in <mask3> and placed in the <mask2> so it’s ready to eat."
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
]