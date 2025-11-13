import numpy as np
from scipy.ndimage import binary_dilation

def reserve_corridors(D: np.ndarray, doors_px: list[tuple[int,int]], main_m: float, aux_m: float, pixel_size_m: float):
    # 简化：以门为源，把 EDT>阈值的“骨架带”保留为禁放
    main_r = int(np.ceil(main_m / pixel_size_m / 2))
    aux_r  = int(np.ceil(aux_m  / pixel_size_m / 2))
    # 粗骨架：D 较大的像素集合
    skel = (D > aux_m)
    # 对门附近增强
    seeds = np.zeros_like(D, np.uint8)
    for (y,x) in doors_px: seeds[y,x] = 1
    # 主通道 = skel 膨胀 main_r；次通道 = skel 膨胀 aux_r
    main_keepout = binary_dilation(skel, iterations=main_r)
    aux_keepout  = binary_dilation(skel, iterations=aux_r)
    return main_keepout.astype(np.uint8), aux_keepout.astype(np.uint8)
