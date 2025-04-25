import random
from copy import deepcopy
from collections import Counter
from task_pool import TASK_POOL
import json, pprint
import re

# ---------- 1) layout → 允许的角色多重集 ----------
# 例子（请根据之前文档把其它 layout 填完整）
LAYOUT_COMBINATIONS = {
    0: [["humanoid", "wheeled", "dog",]],
    1: [["humanoid", "wheeled", "dog", "arm"]],
    2: [["humanoid", "wheeled", "dog"]],
    3: [["humanoid", "wheeled", "dog", "arm", "arm"]],
    4: [["humanoid", "wheeled", "dog", "arm"]],
    5: [["humanoid", "wheeled", "dog", "arm"]],
    6: [["humanoid", "wheeled", "dog", "dog", "arm", "arm", "arm"]],
    7: [["humanoid", "wheeled", "dog", "dog", "arm", "arm"]],
    8: [["humanoid", "wheeled", "dog", "dog", "arm"]],
    9: [["humanoid", "wheeled", "dog", "dog", "arm", "arm"]],
}

# ---------- 2) 机器人类别到具体 ID ----------
CATEGORY2IDS = {
    "humanoid": ["unitree_h1", "stompy"],
    "wheeled":  ["fetch"],
    "arm":      ["panda"],
    "dog":      ["anymal_c", "unitree_go2"],
}

# ---------- 3) 工具函数 ----------
def is_compatible(layout_id, role_seq):
    """判断任务要求的 role_seq 是否能在给定 layout 内找到足够名额"""
    avail = Counter()
    for combo in LAYOUT_COMBINATIONS.get(layout_id, []):
        avail.update(combo)            # 统计该 layout 能提供的总类别数量
    needed = Counter(role_seq)
    return all(avail[c] >= n for c, n in needed.items())

def _choose_ids(role_seq):
    """抽取 ID 并返回 (乱序后的 id 列表, 置换表 perm)"""
    ids = [random.choice(CATEGORY2IDS[cat]) for cat in role_seq]
    perm = list(range(len(ids)))
    random.shuffle(perm)
    shuffled_ids = [ids[i] for i in perm]
    return shuffled_ids, perm          # perm[i]=原 idx？我们用 perm.index 逆查

def _permute_gt(gt_steps, perm):
    """根据 perm 映射 ground_truth 的 key 和 value 中的 Rk"""
    def remap_robot_str(s):
        """若 s 是 Rk 形式的机器人代号，则返回重映射后的 Rj"""
        if isinstance(s, str) and re.fullmatch(r"R\d+", s):
            idx = int(s[1:]) - 1
            new_idx = perm.index(idx)
            return f"R{new_idx+1}"
        return s

    new_steps = []
    for step in gt_steps:
        new_step = {}
        for old_key, action in step.items():
            # 替换键名 Rk → Rj
            old_idx = int(old_key[1:]) - 1
            new_idx = perm.index(old_idx)
            new_key = f"R{new_idx+1}"

            # 替换动作参数中可能出现的 Rk
            if isinstance(action, list):
                new_action = [remap_robot_str(x) for x in action]
            else:
                new_action = action  # 非预期格式，保持原样

            new_step[new_key] = new_action
        new_steps.append(new_step)

    return new_steps


def _fill_masks(obj, mask_map):
    """递归替换 <maskX> 占位符"""
    if isinstance(obj, str):
        for k, v in mask_map.items():
            obj = obj.replace(f"<{k}>", v)
        return obj
    if isinstance(obj, list):
        return [_fill_masks(x, mask_map) for x in obj]
    if isinstance(obj, dict):
        return {k: _fill_masks(v, mask_map) for k, v in obj.items()}
    return obj

# ---------- 4) 主实例化函数 ----------
def instantiate_task(template):

    tpl = deepcopy(template)
    layout_id = 0

    # a) 随机选取并打乱 robot IDs
    ids, perm = _choose_ids(tpl["robot_roles"])
    robots = {f"R{i+1}": rid for i, rid in enumerate(ids)}
    ids_idle, perm_idle = _choose_ids(tpl["idle_robot_roles"])
    idle_robots = {f"R{i+1}": rid for i, rid in enumerate(ids_idle)}

    KEEP_PROB = 0.5
    core_roles = tpl["robot_roles"]
    idle_roles = tpl.get("idle_robot_roles", [])
    ids_idle   = ids_idle

    selected_idle_roles = []
    selected_idle_ids   = []

    for role, rid in zip(idle_roles, ids_idle):
        if random.random() < KEEP_PROB:
            selected_idle_roles.append(role)
            selected_idle_ids.append(rid)

    combined_roles = core_roles + selected_idle_roles
    idle_robots_list = selected_idle_ids


    if not is_compatible(layout_id, combined_roles):
        raise ValueError(f"layout_id {layout_id} cannot satisfy robot_roles {combined_roles}")

    # b) 随机选择 mask 值并替换
    mask_map = {mk: random.choice(tpl[mk]) for mk in tpl if mk.startswith("mask")}
    desc_template = random.choice(tpl["description"])
    desc_filled = _fill_masks(desc_template, mask_map)
    gt_masked  = [_fill_masks(step, mask_map) for step in tpl["ground_truth"]]

    # c) 根据置换表同步 ground_truth 键
    gt_final = _permute_gt(gt_masked, perm)

    # d) 处理 init_pos
    init_pos = {}
    init_pos_meta = tpl["init_pos"]
    for idx, item_pos in enumerate(init_pos_meta):
        if 'name_key' in item_pos:
            item_name = mask_map[item_pos['name_key']]
        else:
            raise ValueError
        cur_pos = item_pos["pos"]
        removed_pos = []
        if 'exclude_keys' in item_pos:
            for exclude_key in item_pos['exclude_keys']:
                removed_pos.append(mask_map[exclude_key])
        for p in removed_pos:
            if p in cur_pos:
                cur_pos.remove(p)
        if "aligned_keys" in item_pos:
            assert len(item_pos['aligned_keys']) == 1
            cur_pos = [mask_map[item_pos["aligned_keys"][0]]]
        init_pos[f'{item_name}_{idx}'] = cur_pos

    # e) add constraints
    constraints = []
    if 'constraints' in tpl:
        constraints = tpl['constraints']
        for con in constraints:
            for tcon in con:
                for i in range(len(tcon)):
                    new_tcon = deepcopy(tcon[i])
                    for k, v in tcon[i].items():
                        # if 'mask' in v:
                        #     # print(v)
                        #     pass
                            # new_tcon[k] = mask_map[v.replace('<', '').replace('>', '')]
                            # print(mask_map[v.replace('<', '').replace('>', '')])
                            # print(tcon[i])
                        if k == 'status':
                            # print('in')
                            for ik, iv in tcon[i]['status'].items():
                                if 'mask' in iv:
                                    new_tcon['status'][ik] = mask_map[iv.replace('<', '').replace('>', '')]
                        elif k == 'name':
                            new_tcon[k] = mask_map[v.replace('<', '').replace('>', '')]
                    tcon[i] = new_tcon
            
    return {
        "task_id": tpl["task_id"],
        "task_name": tpl["task_name"],
        "layout_id": layout_id,
        "description": desc_filled,
        "robots": robots,
        "ground_truth": gt_final,
        "init_pos": init_pos,
        "idle_robots": idle_robots_list,
        "constraints": constraints,
    }

# ---------- 5) 小测试 ----------
if __name__ == "__main__":
    sample = instantiate_task(random.choice(TASK_POOL))
    pprint.pprint(sample, width=120, sort_dicts=False)
