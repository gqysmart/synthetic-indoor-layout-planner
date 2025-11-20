import numpy as np
from skimage.feature import peak_local_max

def local_max_candidates(D: np.ndarray, min_dist_px:int=8, topk:int=512):
    # 选自由度大的位置
    coords = peak_local_max(D, min_distance=min_dist_px, num_peaks=topk, exclude_border=False)
    # 返回 [(y,x), ...]
    return [(int(y), int(x)) for y,x in coords]

def wall_strip_candidates(room_mask: np.ndarray, step_px:int=10):
    # 沿墙根采样（简单版：房间边界膨胀-腐蚀取带状）
    ys, xs = np.where(room_mask == 1)
    # 实际中可替换为“多边形边段均匀采样 + 内缩 offset”
    return list(zip(ys[::step_px], xs[::step_px]))

def rank_by_heuristic(cands_xy, D, prefer_wall=False):
    # 启发：距离场越大越好；可选墙向权
    scored = []
    for (y,x) in cands_xy:
        s = float(D[y,x])
        if prefer_wall:
            s *= 0.95  # 让“贴墙”别压过通透性，按需调整
        scored.append(((y,x), s))
    scored.sort(key=lambda t: -t[1])
    return [p for p,_ in scored]
