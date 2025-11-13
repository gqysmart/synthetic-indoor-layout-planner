import numpy as np
from scipy.ndimage import distance_transform_edt

def edt_from_obstacles(obstacle: np.ndarray, pixel_size_m: float) -> np.ndarray:
    # obstacle: 1=blocked, 0=free
    # 返回以“米”为单位的距离场
    D_pix = distance_transform_edt(1 - obstacle)  # free=1
    return D_pix * pixel_size_m

def edt_update_local(D: np.ndarray, obstacle: np.ndarray, changed_bbox, pixel_size_m: float):
    # 简化版：对 bbox 区域重算（足够快）。工程上可做更小域+刷波
    t, l, b, r = changed_bbox
    pad = 6  # 经验：留点边界
    t = max(0, t-pad); l = max(0, l-pad); b = min(D.shape[0], b+pad); r = min(D.shape[1], r+pad)
    sub_obs = obstacle[t:b, l:r]
    sub = edt_from_obstacles(sub_obs, pixel_size_m)
    D[t:b, l:r] = sub
    return D
