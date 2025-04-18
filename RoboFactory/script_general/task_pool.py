"""
Task template pool for multi‑agent embodied data generation.

Each template dict contains:
  • task_name        – unique identifier
  • description      – English sentence with <maskX> placeholders
  • mask*            – lists of strings to substitute for each placeholder
  • robot_roles      – ordered list of abstract robot categories
  • ground_truth     – list of timestep dictionaries mapping Ri to [Primitive, Target]

Add or modify templates as needed; the main pipeline can import TASK_POOL
and sample/instantiate concrete tasks.
"""

__all__ = ["TASK_POOL"]

TASK_POOL = [
    {
        "task_id": "0-1",
        "task_name": "move_asset_to_target",
        "description": "Move <mask1> to <mask2>",
        "mask1": ["a plate", "a cup", "a book", "a pan"],
        "mask2": ["the dining table", "the counter", "the sink area", "the stove"],
        "robot_roles": ["humanoid"],
        "ground_truth": [
            {"R1": ["Move", "<mask1>"]},
            {"R1": ["Reach", "<mask1>"]},
            {"R1": ["Grasp", "<mask1>"]},
            {"R1": ["Move", "<mask2>"]},
            {"R1": ["Place", "<mask2>"]}
        ]
    },
    {
        "task_id": "0-2",
        "task_name": "move_asset_to_target",
        "description": "Move <mask1> to <mask2>",
        "mask1": ["a plate", "a cup", "a book", "a pan"],
        "mask2": ["the dining table", "the counter", "the sink area", "the stove"],
        "robot_roles": ["wheeled"],
        "ground_truth": [
            {"R1": ["Move", "<mask1>"]},
            {"R1": ["Reach", "<mask1>"]},
            {"R1": ["Grasp", "<mask1>"]},
            {"R1": ["Move", "<mask2>"]},
            {"R1": ["Place", "<mask2>"]}
        ]
    },
    {
        "task_id": "0-3",
        "task_name": "move_asset_to_target",
        "description": "Move <mask1> to <mask2>",
        "mask1": ["a bottle", "a screwdriver", "a box", "a tool"],
        "mask2": ["the kitchen counter", "the toolbox", "the sink", "the shelf"],
        "robot_roles": ["arm", "dog", "arm"],
        "ground_truth": [
            {"R1": ["Move", "<mask1>"],    "R2": ["Move", "R1"]},
            {"R1": ["Reach", "<mask1>"]},
            {"R1": ["Grasp", "<mask1>"]},
            {"R1": ["Handover", "R2"]},
            {"R2": ["Move", "R3"]},
            {"R3": ["Reach", "<mask1>"]},
            {"R3": ["Grasp", "<mask1>"]},
            {"R3": ["Place", "<mask2>"]}
        ]
    },
    {
        "task_id": "1-1",
        "task_name": "parallel_dual_asset_to_plate",
        "description": "Transport the <mask1> and the <mask2> into the <mask3> together",
        "mask1": ["apple", "tomato", "bun"],
        "mask2": ["banana", "pear", "peach"],
        "mask3": ["plate", "bowl", "tray"],
        "robot_roles": ["humanoid", "wheeled"],
        "ground_truth": [
            {"R1": ["Move", "<mask1>"],      "R2": ["Move", "<mask2>"]},
            {"R1": ["Reach", "<mask1>"],     "R2": ["Reach", "<mask2>"]},
            {"R1": ["Grasp", "<mask1>"],     "R2": ["Grasp", "<mask2>"]},
            {"R1": ["Move", "<mask3>"],      "R2": ["Move", "<mask3>"]},
            {"R1": ["Place", "<mask3>"],     "R2": ["Place", "<mask3>"]}
        ]
    },
    {
        "task_id": "1-2",
        "task_name": "parallel_dual_asset_to_plate",
        "description": "Transport the <mask1> and the <mask2> into the <mask3> together",
        "mask1": ["apple", "tomato", "bun"],
        "mask2": ["banana", "pear", "peach"],
        "mask3": ["plate", "bowl", "tray"],
        "robot_roles": ["wheeled", "humanoid"],
        "ground_truth": [
            {"R1": ["Move", "<mask1>"],      "R2": ["Move", "<mask2>"]},
            {"R1": ["Reach", "<mask1>"],     "R2": ["Reach", "<mask2>"]},
            {"R1": ["Grasp", "<mask1>"],     "R2": ["Grasp", "<mask2>"]},
            {"R1": ["Move", "<mask3>"],      "R2": ["Move", "<mask3>"]},
            {"R1": ["Place", "<mask3>"],     "R2": ["Place", "<mask3>"]}
        ]
    },
    {
        "task_id": "2-1",
        "task_name": "set_plate_and_fork_on_table",
        "description": "Place the <mask1> on the <mask2> and fetch the <mask3> from the <mask4> into the <mask1>",
        "mask1": ["plate", "bowl", "tray"],
        "mask2": ["table", "counter", "stove"],
        "mask3": ["fork", "spoon", "knife"],
        "mask4": ["drawer", "cabinet", "shelf"],
        "robot_roles": ["humanoid", "wheeled"],
        "ground_truth": [
            {"R1": ["Move", "<mask4>"],      "R2": ["Reach", "<mask1>"]},
            {"R1": ["Reach", "<mask4>"],     "R2": ["Grasp", "<mask1>"]},
            {"R1": ["Pull", "<mask4>"],      "R2": ["Move", "<mask2>"]},
            {"R1": ["Reach", "<mask3>"],     "R2": ["Place", "<mask2>"]},
            {"R1": ["Grasp", "<mask3>"]},
            {"R1": ["Move", "<mask1>"]},
            {"R1": ["Place", "<mask1>"]}
        ]
    },
    {
        "task_id": "3-1",
        "task_name": "toast_bread_and_set_plate",
        "description": "Insert the <mask1> into the <mask2> and place the <mask3> on the <mask4>",
        "mask1": ["bread", "bun", "slice"],
        "mask2": ["toaster", "oven"],
        "mask3": ["plate", "tray", "dish"],
        "mask4": ["table", "counter", "rack"],
        "robot_roles": ["humanoid", "wheeled"],
        "ground_truth": [
            {"R1": ["Move", "<mask1>"],        "R2": ["Move", "<mask3>"]},
            {"R1": ["Reach", "<mask1>"],        "R2": ["Reach", "<mask3>"]},
            {"R1": ["Grasp", "<mask1>"],        "R2": ["Grasp", "<mask3>"]},
            {"R1": ["Move", "<mask2>"],         "R2": ["Move", "<mask4>"]},
            {"R1": ["Reach", "<mask2>"],        "R2": ["Place", "<mask4>"]},
            {"R1": ["Place", "<mask2>"]},
            {"R1": ["Interact", "<mask2>"]}
        ]
    },
    {
        "task_id": "4-1",
        "task_name": "push_box_and_store_item",
        "description": "Push the <mask1> on the ground to the goal region and put the <mask2> into the <mask1>",
        "mask1": ["box", "crate", "bin"],
        "mask2": ["bottle", "book", "tool"],
        "robot_roles": ["dog", "humanoid"],
        "ground_truth": [
            {"R1": ["Move", "<mask1>"],       "R2": ["Reach", "<mask2>"]},
            {"R1": ["Reach", "<mask1>"],      "R2": ["Grasp", "<mask2>"]},
            {"R1": ["Push", "<mask1>"]},       
            {"R2": ["Move", "<mask1>"]},
            {"R2": ["Place", "<mask1>"]}
        ]
    }
]
