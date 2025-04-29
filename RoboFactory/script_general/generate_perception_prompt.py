import re
import itertools

def expand_task(task):
    description = task["description"]

    # 找到所有 mask 占位符，如 <mask1>, <mask2>
    masks = sorted(set(re.findall(r"<(mask\d+)>", description)))

    # 提取对应的内容列表
    choices = [task[mask] for mask in masks]

    # 枚举所有组合
    all_combinations = list(itertools.product(*choices))

    # 替换所有 mask 生成具体描述
    descriptions = []
    for combo in all_combinations:
        filled = description
        for mask, value in zip(masks, combo):
            filled = filled.replace(f"<{mask}>", value)
        descriptions.append(filled)

    return descriptions
