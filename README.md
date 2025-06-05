<div align="center">
  <img src="./assets/logo.png" width="150"/>
  <h1 align="center">VIKI-R: Coordinating Embodied Multi-Agent Cooperation via Reinforcement Learning</h1>
  <a href="https://arxiv.org/abs/2503.16408"><img src="https://img.shields.io/badge/arxiv-2506.TODO-b31b1b" alt="arXiv"></a>
  <a href="https://faceong.github.io/VIKI-R/"><img src="https://img.shields.io/badge/Project_Page-green" alt="Project Page"></a>
  <a href='https://huggingface.co/datasets/henggg/VIKI-R'><img src='https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Datasets-blue'></a>
</div>
  
## 🔥 Overview <a name="overview"></a>
<div align="center">
  <img src="./assets/viki-r_v7_page-0001.jpg" width="950"/>
</div>

**VIKI** comprises **VIKI-Bench** (a hierarchical multi-agent visual reasoning benchmark) and **VIKI-R** (a two-stage learning framework).  
- **VIKI-Bench** introduces a three-level evaluation suite—**Agent Activation**, **Task Planning**, **Trajectory Perception**—with 23,737 tasks across 100 scenes, 6 robot morphologies, and over 1,000 asset combinations, offering both global and first-person views.
- **VIKI-R** builds on **Qwen2.5-VL-Instruct** (3B/7B) via:  
  1. **Supervised Fine-Tuning (SFT)** with high quality Chain-of-Thought (CoT) annotations.
  2. **Reinforcement Fine-Tuning (RFT)** using Grouped Relative Policy Optimization (GRPO) and combined diverse rewards.
     
## 🎯 Key Features

- **Hierarchical Dataset**: 23,737 tasks, 100 scenes, 6 robot types, ≥1,000 asset combos. 
- **GRPO RL**: Structured planning with dual-format and correctness rewards.
- **Robotic-Focused**: Home layouts, varied embodied multi-agent tasks.
- **Metrics**: Activation Accuracy, Planning Correctness & Efficiency, Trajectory RMSE/HD/DFD.

## 📊 Datasets <a name="datasets"></a>
<div align="center">
  <img src="./assets/dataset_v5_page-0001.jpg"  width="950" />
</div>

### VIKI-Bench Levels  
- **Level 1: Agent Activation**  
  Select the appropriate subset of agents given a scene and instruction.
- **Level 2: Task Planning**  
  Generate executable multi-agent action sequences within reference length.
- **Level 3: Trajectory Perception**  
  Predict spatial trajectories of visible agents from first-person views; evaluate via RMSE, Hausdorff, and Dynamic Fréchet Distance.

**Statistics:**  
- **23,737** task samples  
- **100** diverse 3D scenes  
- **6** heterogeneous robot morphologies (e.g., dual-arm, tracked, legged, humanoid)  
- **>1,000** asset combinations  
- Global view + multi ego-perspectives  

## 🚀 Quick Start <a name="quick-start"></a>

```bash
# Clone repository
git clone https://github.com/MARS-EAI/VIKI-R.git
cd VIKI-R

# Create Conda environment
conda env create -f roboviki.yml
conda activate roboviki

# Install verl framework
cd verl
pip install --no-deps -e .

# Install FlashAttention
# Download wheel from: https://github.com/Dao-AILab/flash-attention
pip install flash_attn-2.7.4.post1+cu12torch2.6cxx11abiFALSE-cp310-cp310-linux_x86_64.whl

# Example: 3B model SFT training
llamafactory-cli configs/viki-1-3b.yaml

# Example: GRPO RL training (3B)
cd train/3BGRPO/VIKI-L1
bash VIKI-R-zero.sh
bash VIKI-R.sh
````

## 🗂️ Model Zoo <a name="model-zoo"></a>

| Model Size | Levels Supported | Training Stages   | Download           | Status      |
|------------|------------------|-------------------|--------------------|-------------|
| 3B         | L1 / L2 / L3     | SFT + GRPO        | [viki-3b](./models/) | Coming Soon |
| 7B         | L1 / L2 / L3     | SFT + GRPO        | [viki-7b](./models/) | Coming Soon |

## 📑 Citation <a name="citation"></a>

```bibtex
@inproceedings{kang2025viki,
  title={{VIKI-R}: Coordinating Embodied Multi-Agent Cooperation via Reinforcement Learning},
  author={},
  booktitle={},
  year={2025},
  url={https://github.com/your-org/RoboFactory-VIKI}
}
```
