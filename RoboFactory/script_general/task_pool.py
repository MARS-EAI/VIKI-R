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
        "task_name": "place_plate_and_fetch_bottle",
        "description": "Move <mask1> to the dining table and fetch <mask2> from the cabinet",
        "mask1": ["a plate", "a bowl", "a cup"],
        "mask2": ["a bottle", "a can", "a jar"],
        "robot_roles": ["humanoid", "wheeled"],
        "ground_truth": [
            {"R1": ["Move", "cabinet"],        "R2": ["Move", "<mask1>"]},
            {"R1": ["Reach", "cabinet"],       "R2": ["Reach", "<mask1>"]},
            {"R1": ["Pull", "cabinet"],        "R2": ["Grasp", "<mask1>"]},
            {"R1": ["Reach", "<mask2>"],       "R2": ["Move", "table"]},
            {"R1": ["Grasp", "<mask2>"],       "R2": ["Place", "table"]},
            {"R1": ["Move", "<mask1>"]},
            {"R1": ["Reach", "<mask1>"]}
        ]
    },
    {
        "task_name": "wipe_counter",
        "description": "Use <mask1> to wipe the kitchen counter",
        "mask1": ["a towel", "a sponge", "a cloth"],
        "robot_roles": ["humanoid"],
        "ground_truth": [
            {"R1": ["Move", "sink"]},
            {"R1": ["Grasp", "<mask1>"]},
            {"R1": ["Move", "counter"]},
            {"R1": ["Wipe", "counter"]},
            {"R1": ["Place", "<mask1>"]}
        ]
    },
    {
        "task_name": "transfer_bottles",
        "description": "Pick <mask1> and place them into <mask2>",
        "mask1": ["three bottles", "two cans", "four jars"],
        "mask2": ["the sink", "the dishwasher", "the container"],
        "robot_roles": ["wheeled"],
        "ground_truth": [
            {"R1": ["Move", "rack"]},
            {"R1": ["Grasp", "<mask1>"]},
            {"R1": ["Move", "<mask2>"]},
            {"R1": ["Place", "<mask2>"]}
        ]
    },
    {
        "task_name": "fridge_to_table_pass",
        "description": "Take <mask1> out of the fridge and pass it to <mask2>",
        "mask1": ["a bottle of juice", "a milk carton", "a soda can"],
        "mask2": ["the arm robot", "the panda arm", "the stationary arm"],
        "robot_roles": ["humanoid", "arm"],
        "ground_truth": [
            {"R1": ["Move", "fridge"]},
            {"R1": ["Reach", "fridge"]},
            {"R1": ["Open", "fridge"]},
            {"R1": ["Grasp", "<mask1>"]},
            {"R2": ["Move", "handover"]},
            {"R1": ["Pass", "<mask1>"],       "R2": ["Grasp", "<mask1>"]},
            {"R2": ["Move", "table"]},
            {"R2": ["Place", "table"]}
        ]
    }
]
