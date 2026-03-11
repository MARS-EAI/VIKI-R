<div align="center">
<h1>VIKI-R: Coordinating Embodied Multi-Agent Cooperation via Reinforcement Learning</h1>

<a href="https://arxiv.org/pdf/2506.09049" target="_blank" rel="noopener noreferrer">
  <img src="https://img.shields.io/badge/Paper-VIKI--R" alt="Paper PDF">
</a>
<a href="https://arxiv.org/abs/2506.09049"><img src="https://img.shields.io/badge/arxiv-2506.09049-b31b1b" alt="arXiv"></a>
<a href="https://faceong.github.io/VIKI-R/"><img src="https://img.shields.io/badge/Project_Page-green" alt="Project Page"></a>
<a href='https://huggingface.co/datasets/henggg/VIKI-R'><img src='https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Datasets-blue'></a>
<a href='https://huggingface.co/datasets/FACEONG/VIKI-Assets'><img src='https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Assets-yellow'></a>
</div>

## Overview

This repository provides the **data production pipeline** for [VIKI-Bench](https://faceong.github.io/VIKI-R/), the first hierarchical benchmark for embodied multi-agent cooperation. It enables automated generation of large-scale training data across three task levels:

| Level | Task | Description |
|---|---|---|
| **L1** | Agent Activation | Determine which agents to deploy for a given task |
| **L2** | Task Planning | Generate step-by-step action plans for multiple robots |
| **L3** | Trajectory Perception | Understand egocentric visual observations of robot actions |

The pipeline takes **task templates** as input, instantiates them with randomized robots, objects, and scene layouts, then renders visual observations through [ManiSkill3](https://www.maniskill.ai/) simulation to produce complete training samples.

> For model training and inference code, please refer to the [`main` branch](https://github.com/MARS-EAI/VIKI-R/tree/main).

## Installation

```bash
git clone -b data-pipeline https://github.com/MARS-EAI/VIKI-R.git
cd VIKI-R
conda create -n viki-r python=3.9
conda activate viki-r
pip install -r RoboFactory/requirements.txt
conda install -c conda-forge networkx=2.5
```

Download 3D assets:
```bash
cd RoboFactory
python script/download_assets.py
```

Download [RoboCasa](https://github.com/robocasa/robocasa) kitchen scenes (required for data generation):
```bash
python -m mani_skill.utils.download_asset RoboCasa
```

## Data Production Pipeline

### Project Structure

```
RoboFactory/
├── script_general/                              # Data production scripts
│   ├── task_pool.py                             # Task template definitions
│   ├── generate_prompt.py                       # Instantiate tasks from templates
│   ├── generate_prompt_json.py                  # Batch generate task instance JSONs
│   ├── generate_tasks_from_json.py              # Render scenes & produce L1/L2 image data
│   ├── generate_perception_prompt.py            # Expand L3 perception task descriptions
│   └── generate_perception_task_from_json.py    # Render L3 perception task data
│
├── utils/eval/                                  # Data validation tools
│   ├── eval.py                                  # Eval orchestrator
│   ├── env.py                                   # SimEnv – lightweight state simulator
│   ├── checker.py                               # Action feasibility & constraint checker
│   └── entities.py                              # Agent, Asset, Action, Position definitions
│
├── eval_gt.py                                   # Batch validate generated data
├── tasks/                                       # ManiSkill task environments
│   ├── viki_bench_task.py                       # VikiBenchTask – L1/L2 scene environment
│   └── viki_bench_perception.py                 # VikiBenchPerception – L3 scene environment
├── planner/                                     # Motion planning & scene rendering
├── configs/layouts/                             # Scene layout configurations (layout_0 ~ layout_9)
└── script/                                      # Simulation utility scripts
```

### L1 / L2: Agent Activation & Task Planning Data

The L1 and L2 levels share the same three-step pipeline:

**Step 1 – Define Task Templates** (`task_pool.py`)

Task templates use `<maskX>` placeholders that get filled with randomized objects, locations, and robots during instantiation:

```python
# Example template in task_pool.py
{
    "task_id": "1-1",
    "task_name": "single_move_asset_to_target",
    "description": ["Move the <mask1> to the <mask2> ..."],
    "mask1": ["meat", "bread", "apple", ...],          # object candidates
    "mask2": ["kitchen work area", "rack", ...],       # target location candidates
    "robot_roles": ["humanoid"],                       # required robot categories
    "idle_robot_roles": ["dog", "arm"],                # distractor robots
    "ground_truth": [                                  # action sequence
        {"R1": ["Move", "<mask1>"]},
        {"R1": ["Reach", "<mask1>"]},
        {"R1": ["Grasp", "<mask1>"]},
        {"R1": ["Move", "<mask2>"]},
        {"R1": ["Place", "<mask2>"]}
    ],
    "goal_constraints": [...],
    "temporal_constraints": [...]
}
```

**Step 2 – Generate Task Instances as JSON** (`generate_prompt.py` → `generate_prompt_json.py`)

Instantiate N tasks by randomly sampling templates, layouts, robot assignments, and mask values:

```bash
cd RoboFactory/script_general

# Generate 1000 task instances
python generate_prompt_json.py -n 1000 -o output.json
```

Each generated instance contains: task description, robot assignments (with concrete robot types like `unitree_h1`, `fetch`, etc.), ground-truth action plans, initial positions, and goal/temporal constraints.

**Step 3 – Render Scene Images** (`generate_tasks_from_json.py`)

Read the JSON file, generate ManiSkill configurations for each task, and launch simulation to render visual observations:

```bash
cd RoboFactory

# Generate image data from task instances
python script_general/generate_tasks_from_json.py --data script_general/output.json
```

This script:
1. Loads the layout config matching each task's `layout_id`
2. Places the required robots and objects at randomized positions
3. Runs ManiSkill simulation to render scene images
4. Saves the complete data sample (image + metadata + ground truth)

### L3: Trajectory Perception Data

L3 uses a separate pipeline with perception-specific cameras and task configurations:

```bash
cd RoboFactory/script_general

# Step 1: Generate perception task descriptions and batch generate JSON
python generate_perception_prompt.py
python generate_prompt_json.py -n 1000 -o output.json

# Step 2: Render perception data with egocentric observations
cd ..
python script_general/generate_perception_task_from_json.py --data script_general/output.json
```

### Supported Robots & Actions

| Robot | Category | Actions |
|---|---|---|
| Panda | Arm | Reach, Grasp, Place, Open, Close, Handover, Interact |
| Fetch | Wheeled | Move, Reach, Grasp, Place, Open, Close, Handover, Interact |
| Unitree H1 | Humanoid | Move, Reach, Grasp, Place, Open, Close, Handover, Interact |
| Stompy | Humanoid | Move, Reach, Grasp, Place, Open, Close, Handover, Interact |
| Unitree Go2 | Quadruped | Move, Push, Interact |
| AnymalC | Quadruped | Move, Push, Interact |

## Output Data Structure

After running the pipeline, generated data is saved under `demos/`:

```
demos/VikiBenchTask/
├── images/                           # Rendered scene images
│   ├── 0.png
│   ├── 1.png
│   └── ...
└── meta_data.json                    # Task metadata & ground truth
```

Each entry in `meta_data.json` contains:

```json
{
    "image": "0.png",
    "gt": {
        "description": "Put the bread into the toaster, turn on the device ...",
        "task_id": "0_4-1",
        "task_name": "toast_bread_and_set_plate",
        "layout_id": 8,
        "robots": {"R1": "stompy", "R2": "fetch"},
        "idle_robots": [],
        "init_pos": {
            "bowl_2": ["kitchen work area"],
            "bread_0": ["kitchen work area", "kitchen island area"],
            "toaster_1": ["room_toaster"]
        },
        "ground_truth": [
            {"R1": ["Move", "bread"], "R2": ["Move", "bowl"]},
            {"R1": ["Reach", "bread"], "R2": ["Reach", "bowl"]},
            ...
        ],
        "goal_constraints": [...],
        "temporal_constraints": [...]
    }
}
```

| Field | Description |
|---|---|
| `description` | Natural language task instruction |
| `robots` | Robot ID → type mapping for active robots |
| `idle_robots` | Distractor robots present but not involved in the task |
| `init_pos` | Initial positions of objects (asset_id → list of possible areas) |
| `ground_truth` | Step-by-step action plan; each step maps robot IDs to `[Action, Target]` |
| `goal_constraints` | Required end-state conditions (object positions, device states) |
| `temporal_constraints` | Ordering dependencies between sub-goals |

## Data Validation

The `utils/eval/` module provides a lightweight state simulator for validating generated data **without physics simulation**. Use it to verify that ground-truth action plans in the generated JSON are logically correct before rendering images.

It checks:
- **Action feasibility** – whether each robot type can perform the assigned action
- **Goal constraints** – whether objects reach the correct target positions
- **Temporal constraints** – whether actions follow the required ordering
- **Simultaneous compatibility** – whether parallel actions are conflict-free

**Validate generated data with `eval_gt.py`:**

```bash
cd RoboFactory

# Validate all task instances in a JSON file
# Reports success/failure count and error details for each failed instance
python eval_gt.py -d script_general/output.json
```

## Community & Contact

For questions or research collaboration, please reach out: faceong02@gmail.com, yiranqin@link.cuhk.edu.cn.

## Acknowledgements

This project is built upon [RoboFactory](https://github.com/MARS-EAI/RoboFactory) and [ManiSkill](https://www.maniskill.ai/). We thank the developers for their excellent work.

## BibTeX

```bibtex
@inproceedings{kang2025viki,
  title={VIKI-R: Coordinating Embodied Multi-Agent Cooperation via Reinforcement Learning},
  author={Kang, Li and Song, Xiufeng and Zhou, Heng and Qin, Yiran and Yang, Jie and Liu, Xiaohong and Torr, Philip and Bai, Lei and Yin, Zhenfei},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS), Datasets and Benchmarks Track},
  year={2025}
}
```
