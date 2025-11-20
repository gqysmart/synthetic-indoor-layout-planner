import numpy as np
import cv2
from scipy.ndimage import distance_transform_edt, binary_dilation, binary_propagation

# ---------------------------------------------------------
# 修正版 reserve_corridors（含单位修正 + 门传播 + 通道膨胀）
# ---------------------------------------------------------
def reserve_corridors(D, doors_px, main_m, aux_m, pixel_size_m):
    """
    D           : EDT 距离图（单位：像素距离）
    doors_px    : 门像素列表 [(y, x), ...]
    main_m      : 主通道宽度（米）
    aux_m       : 辅助通道宽度（米）
    pixel_size_m: 每像素表示多少米
    """
    # 像素 → 米
    D_m = D * pixel_size_m

    # 候选可走区域：至少有 aux_m 的通道宽度（半宽）
    # 即：人中心到障碍距离 >= aux_m/2
    skel_candidates = (D_m >= (aux_m / 2.0))

    H, W = D.shape

    # seeds（门像素），只在 skel_candidates 内生效
    seeds = np.zeros_like(skel_candidates, dtype=bool)
    for (y, x) in doors_px:
        if 0 <= y < H and 0 <= x < W:
            # 保证门口本身可走
            skel_candidates[y, x] = True
            seeds[y, x] = True

    # 如果门口附近完全不可走，直接返回空的 keepout 区
    if not seeds.any():
        return np.zeros_like(D, np.uint8), np.zeros_like(D, np.uint8)

    # 从门开始，在可走区域中传播：得到“从门可达”的区域
    door_skel = binary_propagation(seeds, mask=skel_candidates)

    # 通道宽度 → 膨胀半径（像素半径）
    main_r_px = int(np.ceil((main_m / 2.0) / pixel_size_m))
    aux_r_px  = int(np.ceil((aux_m  / 2.0) / pixel_size_m))

    # 膨胀骨架 → 形成主/辅通道保护区（禁止摆放家具）
    main_keepout = binary_dilation(door_skel, iterations=main_r_px).astype(np.uint8)
    aux_keepout  = binary_dilation(door_skel, iterations=aux_r_px).astype(np.uint8)

    return main_keepout, aux_keepout


# ---------------------------------------------------------
# Demo：真实房间 + 家具 + 通道 + OpenCV 显示
# ---------------------------------------------------------
def demo_room_with_furniture_corridor():
    pixel_size_m = 0.05        # 1 像素 = 5cm
    H, W = 60, 100             # 3m × 5m 房间（像素大小）

    # 房间：1 = free, 0 = obstacle
    room = np.ones((H, W), dtype=np.uint8)

    # -------------------------
    # 家具（矩形）示例（单位 = 像素）
    # -------------------------

    # 家具1：床（2m × 1.5m）放左上
    bed_w_px = int(2.0 / pixel_size_m)   # 40 px
    bed_h_px = int(1.5 / pixel_size_m)   # 30 px
    room[5:5 + bed_h_px, 5:5 + bed_w_px] = 0

    # 家具2：柜子（1m × 0.5m）放右上
    cab_w_px = int(1.0 / pixel_size_m)   # 20 px
    cab_h_px = int(0.5 / pixel_size_m)   # 10 px
    room[5:5 + cab_h_px, 75:75 + cab_w_px] = 0

    # 家具3：桌子（1.2m × 0.6m）放在中左
    desk_w_px = int(1.2 / pixel_size_m)  # 24 px
    desk_h_px = int(0.6 / pixel_size_m)  # 12 px
    room[30:30 + desk_h_px, 15:15 + desk_w_px] = 0

    # -------------------------
    # 门：底边中心，宽度 0.9m
    # -------------------------
    door_width_m = 0.9                     # 900 mm
    door_w_px = int(round(door_width_m / pixel_size_m))
    door_w_px = max(1, door_w_px)

    door_y = H - 2                         # 门所在的行（往上留一点空间）
    door_x_center = W // 2

    half = door_w_px // 2
    x1 = max(0, door_x_center - half)
    x2 = min(W - 1, door_x_center + half)

    # 在房间下边墙上“挖一个门洞”，高度设为 2 像素
    room[door_y - 1:door_y + 1, x1:x2 + 1] = 1

    # seeds：门整条宽度上的像素
    doors_px = [(door_y, x) for x in range(x1, x2 + 1)]

    # -------------------------
    # EDT（基于 free=1, obstacle=0）
    # -------------------------
    D = distance_transform_edt(room == 1)

    # 主通道 1.0m，次通道 0.6m
    main_m = 1.0
    aux_m  = 0.6

    main_keepout, aux_keepout = reserve_corridors(
        D, doors_px, main_m, aux_m, pixel_size_m
    )

    # -------------------------
    # OpenCV 彩色可视化图
    # -------------------------
    vis = np.zeros((H, W, 3), dtype=np.uint8)

    # 白色 = free
    vis[room == 1] = (255, 255, 255)

    # 黑色 = 家具/障碍
    vis[room == 0] = (0, 0, 0)

    # 蓝色 = 次通道保护区
    vis[(aux_keepout == 1) & (room == 1)] = (255, 0, 0)

    # 红色 = 主通道保护区（覆盖次通道）
    vis[(main_keepout == 1) & (room == 1)] = (0, 0, 255)

    # 用绿色标记门区域（整条）
    for _, x in doors_px:
        vis[door_y, x] = (0, 255, 0)

    # 放大显示
    vis_large = cv2.resize(vis, None, fx=6, fy=6, interpolation=cv2.INTER_NEAREST)

    cv2.imshow("Room + Furniture + Corridor Keepout", vis_large)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    demo_room_with_furniture_corridor()
