# Multi-Agent Embodied Intelligence Challenge

## Overview
The [Multi-Agent Plan Track](https://mars-eai.github.io/MARS-Challenge-Webpage/#track1) of the Multi-Agent Embodied Intelligence Challenge focuses on high-level task planning across multiple heterogeneous embodied agents. Participants are required to develop planning systems capable of interpreting natural language instructions and visual observations to generate effective and efficient action sequences for multiple agents.

Each task is formulated as an episode, comprising a natural language instruction and a structured observation (e.g., rendered scene image) of the environment. The core challenge lies in multi-agent coordination and reasoning, where participants must select a subset of appropriate agents and assign them temporally and semantically grounded action sequences to collaboratively accomplish the task. This track emphasizes reasoning under ambiguity, generalization to novel tasks, and alignment between plans and embodied capabilities.

## Important Notice
This GitHub repository provides a baseline example for competition participants. Participants are free to modify any part of the code, implement their own solutions, and develop novel approaches to solve the multi-agent planning challenge.

As a rule, all submitted solutions must use or obtain Vision-Language Model (VLM) as part of the answer generation process.

## Challenge Description
This track is powered by the [ManiSkill](https://www.maniskill.ai/) platform and the [RoboCasa](https://robocasa.ai/) scene and [VIKI-Bench](https://faceong.github.io/VIKI-R/) dataset, featuring a curated set of task scenarios involving diverse robot embodiments and complex collaborative goals. Given a structured scene image with multiple candidate agents (humanoids, quadrupeds, manipulators), participants need to complete the following two core tasks:

1. **Agent Selection**: Choose a subset of appropriate agents from the scene based on a natural language command.
2. **Action Assignment**: Define a sequence of high-level actions for each selected agent to accomplish the collaborative task.

This challenge evaluates the vision-language model's ability to reason over multi-agent allocation, role assignment, and symbolic planning, simulating real-world cooperation among diverse robots.

### 🗓️ Competition Timeline

| Date            | Phase             | Description                                                                 |
|-----------------|-------------------|-----------------------------------------------------------------------------|
| August 18th      | Warmup Round      | Environment opens for teams to explore and get familiar (no prizes).        |
| September 1st   | Official Round    | Competition begins with unseen tasks and prize challenges.                  |
| late October (TBD)  | Official Round Ends | Expected closing of the official round.                                    |
| December        | Award Ceremony    | Final results and awards will be announced.                                 |


## Submission Requirements
All final submissions must include the following two components:

1. **test.json**: A JSON file containing evaluation results on the public test set, to be submitted on Kaggle for leaderboard scoring
2. **code.zip**: A zip file containing the complete source code that generates the evaluation results, used for anti-cheating verification

## Evaluation Methodology

### Scoring Framework
The evaluation system employs a comprehensive scoring mechanism that assesses both agent selection accuracy and action planning quality. The total score is computed as:

**Total Score = 0.1 × Robot Selection Score + 0.9 × Action Planning Score**

### Robot Selection Score (10% weight)
This component evaluates the accuracy of agent selection:
- **Binary scoring**: 1.0 if the predicted robot set exactly matches the ground truth, 0.0 otherwise
- **Case-insensitive**: Robot names are compared in lowercase to handle case variations
- **Set-based comparison**: Only non-null robots from the ground truth are considered

### Action Planning Score (90% weight)
A multi-dimensional scoring system that provides graduated feedback:

- **Step Match** (40%): Step-by-step comparison of action sequences
- **Prefix Match** (30%): Consecutive matches from the beginning of the sequence
- **Action Type Match** (20%): Matching of action types regardless of target objects
- **Length Ratio** (10%): Proportion of matched sequence length

**Action Planning Score = 0.4 × Step Match + 0.3 × Prefix Match + 0.2 × Action Type Match + 0.1 × Length Ratio**

### Evaluation Metrics
Submissions are evaluated on a hidden test set featuring unseen object configurations and domain randomization. The evaluation provides:

1. **Total Score**: The total score of all test cases.
2. **Score Distribution**: Detailed breakdown of performance across different score ranges:
   - Zero (0.0): Complete failure cases
   - Low (0.0-0.3): Minimal partial credit
   - Medium-Low (0.3-0.6): Substantial partial credit
   - Medium-High (0.6-0.9): Near-correct solutions
   - High (0.9-1.0): Almost perfect solutions
   - Perfect (1.0): Complete success

## Installation and Setup

### Dependencies
Install required Python packages:
```bash
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Baseline Example
This repository provides a baseline implementation that participants can use as a starting point. The baseline approach uses GPT-4o for both agent selection and action planning.

### Customization and Development
Participants are encouraged to:

1. **Modify the baseline approach**: Improve the existing implementation
2. **Implement novel methods**: Develop new algorithms for multi-agent planning
3. **Enhance prompt engineering**: Optimize prompts for better performance
4. **Add preprocessing/postprocessing**: Implement additional data processing steps
5. **Integrate different models**: Use alternative language models or vision systems

### Prompt Customization
Before running evaluations, customize the prompt content by editing `plan/prompt.py`:

1. **System Instructions**: Modify `SYSTEM_INSTRUCTION` to adjust AI behavior
2. **Robot Descriptions**: Update `ROBOT_DESCRIPTION` for different robot types
3. **Available Actions**: Customize `AGENT_AVAIL_ACTIONS` for each robot
4. **User Message Templates**: Adjust `get_user_message_template()` function

Example customization:
```python
# System instruction - core prompt content
SYSTEM_INSTRUCTION = """You are a comprehensive robot task planner..."""

# Robot description information
ROBOT_DESCRIPTION = {
    'stompy': 'A bipedal robot designed for...',
    # Other robot descriptions
}

# Available actions for robots
AGENT_AVAIL_ACTIONS = {
    'panda': ['Reach', 'Grasp', 'Place', 'Open', 'Close', 'Interact'],
    # Other robot actions
}
```

### Running Evaluation
Execute the evaluation script:
```bash
cd plan
python viki.py --model gpt-4o --split test
```


### Output Files
Results are generated in the `plan/result/` directory:
- `combined_data_final_{model_name}.json`: Final evaluation results
- `stats_{model_name}_{split}.txt`: Statistical summary
- `combined_data_partial_{count}_{model_name}.json`: Intermediate results (saved every 50 samples)

## Project Structure
```
Multi-Agent_Embodied_Intelligence_Challenge/
├── plan/
│   ├── prompt.py              # 📝 Prompt configuration (user-modifiable)
│   ├── viki.py                # 🚀 Main evaluation script
│   ├── utils/
│   │   └── reward_score/
│   │       ├── viki_2.py      # Scoring mechanism
│   │       └── utils/
│   │           └── eval/      # Evaluation utilities
│   └── result/                # Output directory
├── data/                      # Dataset directory
│   └── test.parquet          # Test dataset
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── README.md                  # This file
```

## Data Preparation
Place dataset files in the `data/` directory:
- `test.parquet`: Test dataset

Data files should be obtained from the original RoboFactory-VIKI project.

## Quick Start Guide

1. **Setup Environment**:
```bash
git clone <repository-url>
cd Multi-Agent_Embodied_Intelligence_Challenge
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

2. **Customize Prompts** (Optional):
```bash
nano plan/prompt.py
```

3. **Run Evaluation**:
```bash
cd plan
python viki.py --model gpt-4o --split test
```

4. **View Results**:
```bash
cat result/stats_gpt-4o_test.txt
cat result/combined_data_final_gpt-4o.json
```

5. **Prepare Submission**:
   - Generate `test.json` from your evaluation results
   - Create `code.zip` with your complete source code
   - Submit both files according to competition guidelines

## Important Notes
- ✅ This is a baseline example - participants should modify and improve it
- ✅ Ensure valid OpenAI API key configuration
- ⚠️ API usage incurs costs - monitor your usage
- ⚠️ Default processing limit is 200 samples (modify in `viki.py` if needed)
- ⚠️ Follow anti-cheating guidelines strictly to avoid disqualification

### Anti-Cheating Policy
**⚠️ Important**: All submissions will undergo rigorous anti-cheating verification. The following behaviors are strictly prohibited:

- **Hardcoded answers**: Directly printing or returning pre-computed answers for specific test cases
- **Brute force sample exploitation**: Using pattern matching or lookup tables to exploit specific test samples
- **Data leakage**: Using any information not available during the official evaluation period
- **Submission manipulation**: Any attempt to game the evaluation system

## Troubleshooting

### Common Issues
1. **ImportError**: Install dependencies with `pip install -r requirements.txt`
2. **API Error**: Verify OpenAI API key in `.env` file
3. **Data Not Found**: Ensure `data/test.parquet` exists
4. **Permission Error**: Check write permissions for `result/` directory

### Debugging Features
- Real-time progress display with current average scores
- Intermediate results saved every 50 samples
- Detailed error messages in console output
- Score distribution statistics for performance analysis

## Disclaimer
This repository provides a baseline implementation for the Multi-Agent Embodied Intelligence Challenge. Participants are free to modify, enhance, or completely rewrite the code to develop their own solutions. The organizing committee reserves all rights to the final interpretation of competition rules and evaluation criteria. 
