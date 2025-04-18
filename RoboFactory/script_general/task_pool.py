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
    }
]
