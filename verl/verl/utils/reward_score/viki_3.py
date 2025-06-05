import re
import ast
import numpy as np
from mathruler.grader import extract_boxed_content, grade_answer

def compute_rmse(pred_traj, gt_traj):
    """计算RMSE"""
    pred_points = np.array(pred_traj)
    gt_points = np.array(gt_traj)
    return np.sqrt(np.mean((pred_points - gt_points) ** 2))


def compute_hausdorff(pred_traj, gt_traj):
    """计算Hausdorff距离"""
    pred_points = np.array(pred_traj)
    gt_points = np.array(gt_traj)
    
    def directed_hausdorff(A, B):
        return np.max([np.min([np.linalg.norm(a - b) for b in B]) for a in A])
    
    return max(directed_hausdorff(pred_points, gt_points),
               directed_hausdorff(gt_points, pred_points))


def compute_discrete_frechet(pred_traj, gt_traj):
    """计算Discrete Fréchet距离"""
    pred_points = np.array(pred_traj)
    gt_points = np.array(gt_traj)
    
    n, m = len(pred_points), len(gt_points)
    
    # 计算所有点对之间的距离矩阵
    dist_matrix = np.zeros((n, m))
    for i in range(n):
        for j in range(m):
            dist_matrix[i, j] = np.linalg.norm(pred_points[i] - gt_points[j])
    
    # 初始化Fréchet距离矩阵，用inf填充
    frechet_matrix = np.full((n, m), np.inf)
    
    # 动态规划填充矩阵
    for i in range(n):
        for j in range(m):
            if i == 0 and j == 0:
                frechet_matrix[i, j] = dist_matrix[i, j]
            elif i == 0:
                frechet_matrix[i, j] = max(frechet_matrix[i, j-1], dist_matrix[i, j])
            elif j == 0:
                frechet_matrix[i, j] = max(frechet_matrix[i-1, j], dist_matrix[i, j])
            else:
                frechet_matrix[i, j] = max(
                    min(
                        frechet_matrix[i-1, j],
                        frechet_matrix[i, j-1],
                        frechet_matrix[i-1, j-1]
                    ),
                    dist_matrix[i, j]
                )
    
    return frechet_matrix[n-1, m-1]

def format_reward(predict_str: str) -> float:
    # 先验证是否包含完整的 <think>…</think> 和 <answer>…</answer> 结构
    structure_pattern = re.compile(r"\s*<think>.*?</think>\s*<answer>.*?</answer>\s*", re.DOTALL)
    if not structure_pattern.search(predict_str):
        return 0.0

    # 提取 <answer> 标签内的内容
    answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
    answer_match = re.search(answer_pattern, predict_str)
    if not answer_match:
        return 0.0

    answer_content = answer_match.group(1).strip()

    # 尝试解析为 Python 对象
    try:
        pred_trajectories = ast.literal_eval(answer_content)
    except Exception as e:
        print(f"format_reward: 解析 answer 失败：{answer_content} -> {e}")
        return 0.0

    # 顶层必须是长度为 2 的列表
    if not (isinstance(pred_trajectories, list) and len(pred_trajectories) == 2):
        return 0.0

    # 每个子列表必须长度为 5，且每个点都是两个数值（整数或浮点数）
    for traj in pred_trajectories:
        if not (isinstance(traj, list) and len(traj) == 5):
            return 0.0
        for pt in traj:
            if not (
                isinstance(pt, (list, tuple)) and
                len(pt) == 2 and
                all(isinstance(coord, (int, float)) for coord in pt)
            ):
                return 0.0

    return 1.0


def acc_reward(predict_str: str, ground_truth: str) -> float:
    try:
        # 提取预测中的 <answer>
        answer_pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
        answer_match = re.search(answer_pattern, predict_str)
        if not answer_match:
            return 0.0

        answer_content = answer_match.group(1).strip()

        # 尝试解析预测和真值
        pred_trajectories = ast.literal_eval(answer_content)
        gt_trajectories = ast.literal_eval(ground_truth)

        # 顶层均为长度为 2 的列表
        if not (isinstance(pred_trajectories, list) and isinstance(gt_trajectories, list)):
            return 0.0
        if len(pred_trajectories) != 2 or len(gt_trajectories) != 2:
            return 0.0

        metrics = []
        # 对每一段轨迹分别计算分数
        for pred_traj, gt_traj in zip(pred_trajectories, gt_trajectories):
            if len(pred_traj) != len(gt_traj):
                return 0.0

            # 校验每个点格式
            for pt in pred_traj + gt_traj:
                if not (
                    isinstance(pt, (list, tuple)) and
                    len(pt) == 2 and
                    all(isinstance(coord, (int, float)) for coord in pt)
                ):
                    return 0.0
            max_rmse = 360.0
            max_hd = 360.0
            max_dtw = 400.0

            rmse = compute_rmse(pred_traj, gt_traj)
            hd = compute_hausdorff(pred_traj, gt_traj)
            frechet_distance = compute_discrete_frechet(pred_traj, gt_traj)

            rmse_score = np.clip(1 - rmse / max_rmse, 0, 1)
            hd_score = np.clip(1 - hd / max_hd, 0, 1)
            frechet_score = np.clip(1 - frechet_distance / max_dtw, 0, 1)

            trajectory_score = (rmse_score + hd_score + frechet_score) / 3
            metrics.append(trajectory_score)

        return sum(metrics) / len(metrics)

    except Exception as e:
        print(f"Error in acc_reward: {e}")
        return 0.0


def compute_score(predict_str: str, ground_truth: str) -> float:
    return 0.1 * format_reward(predict_str) + 0.9 * acc_reward(predict_str, ground_truth)

# 示例测试
if __name__ == "__main__":
    predict_str = "<think>..234.</think> <answer>[[[121, 171], [141, 163], [107, 151], [80, 159], [54, 191]], [[197, 157], [178, 160], [155, 166], [156, 145], [142, 151]]]</answer>"
    ground_truth = "[[[123, 172], [139, 166], [149, 154], [121, 157], [65, 194]], [[201, 157], [178, 164], [158, 167], [163, 146], [153, 153]]]"
    print(compute_score(predict_str, ground_truth))
