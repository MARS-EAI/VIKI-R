# Example

## Competition Workflow

### 1. Prompt
Edit the `plan/prompt.py` file to optimize system prompts and user message templates:

```python
SYSTEM_INSTRUCTION = """
Your system prompt...
Including robot capability descriptions, available actions, task understanding strategies, etc.
"""

def get_user_message_template():
    return """
Task description: {task_description}
Please analyze the scene and output:
<answer>
{
  "selected_robots": ["robot_name"],
  "action_plan": [...]
}
</answer>
"""
```

### 2. Run Inference Script
Execute `plan/viki.py` to generate inference results:

```bash
python plan/viki.py --model gpt-4o
```

This script will:
- Read test data and images
- Perform inference using your prompts
- Generate `result/inference_data_final_gpt-4o.json` file

### 3. Convert to Submission Format
Use `release_example/convert_csv.py` to convert JSON to CSV:

```bash
python release_example/convert_csv.py
```

The generated CSV file contains the following columns:
- `task_id`: Task identifier (e.g., task_10, task_11)
- `task_description`: Task description text
- `answer.selected_robots`: List of selected robots (e.g., ['Stompy'])
- `answer.action_plan`: Detailed action sequence plan

### 4. Submit to Kaggle
Submit the generated CSV file to the Kaggle platform to receive your score.

## Scoring Mechanism

### Scoring Formula
**Total Score = 0.1 × Robot Selection Score + 0.9 × Action Planning Score**

#### Robot Selection Score (10% weight)
- Predicted robot set completely matches ground truth: 1.0 points
- Incomplete match: 0.0 points
- Case-insensitive, set-based comparison

#### Action Planning Score (90% weight)
Multi-dimensional partial matching scoring:
- **Step Match (40%)**: Step-by-step comparison of action sequences
- **Prefix Match (30%)**: Consecutive matches from the beginning of sequence
- **Action Type Match (20%)**: Matching action types, ignoring target objects
- **Length Ratio (10%)**: Proportion of matched sequence length

## Output Format Requirements

### selected_robots Format
```json
["Robot1", "Robot2"]  // List of robot names
```

Available robot types:
- `Stompy`: General-purpose humanoid robot
- `Fetch`: Mobile manipulation robot
- `Panda`: Precision manipulation arm
- `Unitree_H1`: High-mobility robot

### action_plan Format
```json
[
  {
    "step": 1,
    "actions": {
      "Robot1": ["Action", "Target"],
      "Robot2": ["Action", "Target"]
    }
  },
  {
    "step": 2,
    "actions": {
      "Robot1": ["Action", "Target"]
    }
  }
]
```

Available action types:
- `Move`: Move to target location
- `Reach`: Reach towards target
- `Grasp`: Grasp object
- `Place`: Place object
- `Open`: Open container/device
- `Close`: Close container/device
- `Interact`: Interact with object

## Example Analysis (Based on Real Test Results)

### 🟢 Excellent Examples (Score ≥ 0.7)

**Task 10: Perfect Execution (1.0000)**
```csv
task_10,"Scan the table for any missing fruits-the pear or the tomato. Place them on the table, checking cabinet if necessary.",['Stompy'],"[{'step': 1, 'actions': {'Stompy': ['Move', 'tomato']}}, {'step': 2, 'actions': {'Stompy': ['Reach', 'tomato']}}, {'step': 3, 'actions': {'Stompy': ['Grasp', 'tomato']}}, {'step': 4, 'actions': {'Stompy': ['Move', 'table']}}, {'step': 5, 'actions': {'Stompy': ['Place', 'table']}}]"
```
- ✅ Perfect robot selection (Stompy)
- ✅ Complete action sequence match
- ✅ Optimal task understanding and execution

**Task 13: High-Quality Partial Match (0.7480)**
```csv
task_13,Transfer the apple over to the kitchen island area.,['Fetch'],"[{'step': 1, 'actions': {'Fetch': ['Move', 'apple']}}, {'step': 2, 'actions': {'Fetch': ['Reach', 'apple']}}, {'step': 3, 'actions': {'Fetch': ['Grasp', 'apple']}}, ...]"
```
- ✅ Correct robot selection (Fetch)
- ✅ 72% action sequence accuracy
- ✅ Proper basic manipulation sequence

**Task 30: Good Performance (0.7000)**
```csv
task_30,Move to the refrigerator and make it open.,['Fetch'],"[{'step': 1, 'actions': {'Fetch': ['Move', 'refrigerator']}}, {'step': 2, 'actions': {'Fetch': ['Reach', 'refrigerator handle']}}, {'step': 3, 'actions': {'Fetch': ['Open', 'refrigerator']}}]"
```
- ✅ Correct robot selection
- ⚠️ Minor detail difference (handle specification)
- ✅ Overall logical sequence correct

### 🟡 Medium Performance Examples (0.3-0.7)

**Task 15: Object Identification Issue (0.4900)**
```csv
task_15,Collect every food and drink on the table and store them properly on the rack.,['Fetch'],"[{'step': 1, 'actions': {'Fetch': ['Move', 'table']}}, {'step': 2, 'actions': {'Fetch': ['Reach', 'bottle']}}, ...]"
```
- ✅ Correct robot selection
- ❌ Target object mismatch (GT: bread, Pred: bottle)
- **Issue**: Different interpretation of "every food and drink"

**Task 35: Strategy Difference (0.3340)**
```csv
task_35,"Store the tomato and the pumpkin safely in the plate.",['Unitree_H1'],"[{'step': 1, 'actions': {'Unitree_H1': ['Move', 'table']}}, {'step': 2, 'actions': {'Unitree_H1': ['Reach', 'tomato']}}, ...]"
```
- ✅ Correct robot selection
- ❌ Different approach (GT: direct to tomato, Pred: table first)
- **Issue**: Task execution strategy divergence

### 🔴 Low Performance Examples (Score < 0.3)

**Task 11: Multi-Robot Collaboration Failure (0.1125)**
```csv
task_11,"Begin by placing the bowl onto the kitchen work area, then fetch the banana from the cabinet...",['Stompy', 'Panda'],"[{'step': 1, 'actions': {'Stompy': ['Move', 'bowl']}}, ...]"
```
- ❌ Wrong robot selection (GT: Fetch+Stompy, Pred: Stompy+Panda)
- ❌ Missing parallel collaboration
- **Critical Issues**: Robot capability mismatch + poor coordination

**Task 36: Robot Type Error (0.2400)**
```csv
task_36,"Place the bread into the toaster, turn it on, and meanwhile set the plate onto the kitchen island area...",['Fetch', 'Panda'],"[...]"
```
- ❌ Wrong robot selection (GT: Stompy+Fetch, Pred: Fetch+Panda)
- ❌ Coordination problems
- **Issue**: Fundamental robot capability understanding error

**Task 46: Multiple Issues (0.1543)**
```csv
task_46,"Store the tomato together with the scissors inside the cabinet...",['Panda', 'Unitree_H1'],"[...]"
```
- ❌ Wrong robot selection (GT: Fetch+Unitree_H1, Pred: Panda+Unitree_H1)
- ❌ Poor action sequence alignment
- **Issue**: Both robot selection and execution planning errors

## Optimization Strategies

### 1. Robot Selection Optimization
- **Task Complexity Analysis**: Use single robot for simple tasks, consider multi-robot for complex tasks
- **Capability Matching**: Select most suitable robot types based on task requirements
- **Efficiency Consideration**: Avoid unnecessary multi-robot collaboration

### 2. Action Planning Improvement
- **Parallelism**: Reasonably arrange parallel actions in multi-robot tasks
- **Target Accuracy**: Carefully analyze images to accurately identify operation targets
- **Action Rationality**: Ensure action sequences comply with physical constraints and task logic

### 3. Prompt Engineering Tips
- **Structured Output**: Explicitly require JSON format output
- **Scene Analysis**: Guide model to carefully analyze image content
- **Task Decomposition**: Teach model to break down complex tasks into basic actions
- **Error Prevention**: Include strategies to avoid common errors

## Common Errors and Solutions

| Error Type | Specific Manifestation | Solution |
|------------|----------------------|----------|
| Robot Selection Error | Task needs Stompy but chose Fetch | Strengthen task-robot capability matching logic |
| Target Identification Error | Should operate tomato but identified table | Optimize image understanding and object recognition |
| Unreasonable Action Sequence | Missing Grasp action, directly Place | Strengthen basic action sequence logic |
| Multi-robot Collaboration Failure | Multiple robots but no parallel actions | Improve collaborative planning algorithms |
| Output Format Error | JSON format doesn't meet requirements | Strictly follow example format for output |

## Performance Statistics from Real Test Results

### Overall Performance (10 Test Cases)
- **Average Score**: 0.4318/1.0
- **Perfect Execution**: 1/10 (10%)
- **High Performance** (≥0.7): 3/10 (30%)
- **Robot Selection Accuracy**: 6/10 (60%)
- **Multi-Robot Task Success Rate**: 1/6 (17%)

### Detailed Performance Breakdown

**Score Distribution:**
- **Excellent (≥0.7)**: Tasks 10 (1.0000), 13 (0.7480), 30 (0.7000)
- **Medium (0.3-0.7)**: Tasks 15 (0.4900), 35 (0.3340), 52 (0.3040)
- **Poor (<0.3)**: Tasks 36 (0.2400), 42 (0.2350), 46 (0.1543), 11 (0.1125)

### Error Pattern Analysis

**Robot Selection Errors (40% of tasks):**
- Task 11: Fetch+Stompy → Stompy+Panda
- Task 36: Stompy+Fetch → Fetch+Panda  
- Task 46: Fetch+Unitree_H1 → Panda+Unitree_H1

**Multi-Robot Collaboration Issues:**
- **Parallel Action Planning**: 5/6 multi-robot tasks showed poor coordination
- **Task Division**: Unclear robot role separation
- **Synchronization**: Lack of simultaneous action execution

**Target Object Misidentification:**
- Task 15: GT targeted bread, prediction targeted bottles
- Task 35: Different movement strategies (direct vs. table-first approach)
- Task 42: Generic "food" vs. specific items

**Action Sequence Problems:**
- **Length Mismatch**: Task 42 (GT: 10 steps, Pred: 5 steps)
- **Strategy Differences**: Various approaches to achieve same goal
- **Incomplete Sequences**: Missing critical intermediate steps

## Success Strategies

1. **Deep Understanding of Scoring Mechanism**: Focus on optimizing action planning quality (90% weight)
2. **Balance Accuracy and Innovation**: Innovate appropriately based on standard answers
3. **Fully Utilize Image Information**: Carefully analyze objects and spatial relationships in scenes
4. **Iterative Prompt Optimization**: Continuously improve prompt strategies based on scoring feedback
5. **Test and Validate**: Thoroughly test in local environment before submission

## Key Takeaways from Analysis

### Critical Success Factors
1. **Perfect Execution is Achievable**: Task 10 demonstrates that 100% scores are possible with precise understanding
2. **Single-Robot Tasks Perform Better**: 3/4 single-robot tasks scored ≥0.3, vs 1/6 multi-robot tasks
3. **Robot Selection is Crucial**: 40% of tasks failed primarily due to wrong robot choices
4. **Action Planning Dominates Scoring**: 90% weight means sequence accuracy is paramount

### Major Challenge Areas
1. **Multi-Robot Coordination**: Only 17% success rate, indicating fundamental algorithmic gaps
2. **Object Identification**: Scene understanding directly impacts target selection accuracy
3. **Task Interpretation**: Different valid approaches can lead to scoring penalties
4. **Sequence Completeness**: Missing steps significantly impact partial match scores

### Optimization Priorities
1. **Focus on Robot-Task Matching**: Build robust capability mapping (addresses 40% of errors)
2. **Improve Parallel Planning**: Critical for multi-robot task success (83% failure rate)
3. **Enhance Scene Analysis**: Better object recognition and spatial reasoning
4. **Validate Sequence Logic**: Ensure complete, physically plausible action chains

### Competition Strategy
- **Start with Single-Robot Tasks**: Higher success probability for baseline performance
- **Master Basic Sequences**: Move→Reach→Grasp→Place patterns are foundational
- **Invest in Multi-Robot Logic**: High payoff but requires sophisticated coordination algorithms
- **Test Thoroughly**: Use local evaluation to catch robot selection and format errors

Best of luck to all participants in achieving excellent results!