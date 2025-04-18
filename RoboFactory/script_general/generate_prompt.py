"""
task_templates.py
──────────────────
以 JSON‑friendly 的 Python dict 定义任务范式，并提供实例化函数
"""

import random
import json
from copy import deepcopy
from task_pool import TASK_POOL

# ------------------------------
# 1. 机器人类别到具体 ID 的映射
# ------------------------------
CATEGORY2IDS = {
    "humanoid": ["unitree_h1", "stompy"],
    "wheeled":  ["fetch"],
    "arm":      ["panda"],
    "dog":      ["anymal_c", "unitree_go2"],
}

# ------------------------------
# 2. layout 组合规则（与之前保持一致，可放到 utils/layout_rules.py）
# ------------------------------
LAYOUT_COMBINATIONS = {
    0: [["humanoid"], ["wheeled"]],
    1: [["humanoid"], ["wheeled"], ["humanoid", "wheeled"]],
    2: [["humanoid"], ["wheeled"], ["humanoid", "wheeled"]],
    3: [["arm", "dog", "arm"], ["humanoid"], ["wheeled"], ["humanoid", "wheeled"]],
    4: [["humanoid"], ["wheeled"]],
    5: [["humanoid"], ["wheeled"], ["humanoid", "wheeled"]],
    7: [["humanoid"], ["wheeled"], ["humanoid", "wheeled"], [["humanoid", "wheeled"], "arm"]],
    8: [["humanoid"], ["wheeled"], ["humanoid", "wheeled"], ["humanoid", "arm"]],
    9: [["humanoid"], ["wheeled"], ["humanoid", "wheeled"], ["humanoid", "arm"],
        ["arm", "dog", "arm"], ["arm", "dog", "dog", "arm"]],
}

# ------------------------------
# 3. 实例化工具函数
# ------------------------------
def _choose_ids(role_sequence):
    """从 CATEGORY2IDS 抽取并随机打乱返回 {R1: id1, R2: id2, ...}"""
    ids = [random.choice(CATEGORY2IDS[cat]) for cat in role_sequence]
    random.shuffle(ids)
    return {f"R{i+1}": rid for i, rid in enumerate(ids)}

def _fill_masks(text_or_action, mask_map):
    """递归替换字符串或动作中的 <maskX>"""
    if isinstance(text_or_action, str):
        for mk, val in mask_map.items():
            text_or_action = text_or_action.replace(f"<{mk}>", val)
        return text_or_action
    elif isinstance(text_or_action, list):
        return [_fill_masks(t, mask_map) for t in text_or_action]
    elif isinstance(text_or_action, dict):
        return {k: _fill_masks(v, mask_map) for k, v in text_or_action.items()}
    return text_or_action

def instantiate_task(template, layout_id):
    """给定模板 & layout，输出完整 JSON 样本"""
    tpl = deepcopy(template)

    # 1) 确定 robot IDs（这里不做 layout 合法性检查，按 roles 抽取并打乱）
    robots = _choose_ids(tpl["robot_roles"])

    # 2) 随机填充 mask 值
    mask_map = {mk: random.choice(tpl[mk]) for mk in tpl if mk.startswith("mask")}
    description_filled = _fill_masks(tpl["description"], mask_map)
    gt_filled = [_fill_masks(step, mask_map) for step in tpl["ground_truth"]]

    return {
        "task_name": tpl["task_name"],
        "layout_id": layout_id,
        "description": description_filled,
        "robots": robots,
        "ground_truth": gt_filled
    }

# ------------------------------
# 4. demo – 生成 3 条样本并打印 JSON
# ------------------------------
if __name__ == "__main__":
    samples = [instantiate_task(random.choice(TASK_POOL), layout_id=random.choice(list(LAYOUT_COMBINATIONS)))
               for _ in range(1)]
    print(json.dumps(samples, indent=2, ensure_ascii=False))
