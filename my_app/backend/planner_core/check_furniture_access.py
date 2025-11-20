#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
从入户门判断是否存在通道可以到达各个家具的“可达区域”。

房间采用 0/1 网格表示：
    1 = 可走
    0 = 障碍（家具、墙体等）

可达判断逻辑：
    1. 从门位置作为种子，用 binary_propagation 在可走区域内扩散，
       得到 reachable mask。
    2. 对每个家具，根据类型 + 朝向，构造其“可达区域” access_zone。
    3. 若 np.any(reachable & access_zone) 为 True，则该家具可从门到达。
"""

import numpy as np
import cv2
from scipy.ndimage import binary_propagation, binary_dilation
from dataclasses import dataclass


# -----------------------------------------------------------------------------
# 数据结构
# -----------------------------------------------------------------------------
@dataclass
class Furniture:
    name: str
    kind: str          # 'bed' / 'desk' / 'wardrobe'
    y1: int            # 包含，top
    y2: int            # 不包含，bottom
    x1: int            # 包含，left
    x2: int            # 不包含，right
    facing: str        # 'N' / 'S' / 'E' / 'W' —— 家具“正前方”的朝向


# -----------------------------------------------------------------------------
# 房间 + 家具 + 门的示例构造
# -----------------------------------------------------------------------------
def build_demo_room():
    """
    构造一个简单示例：
    - 3m x 5m 房间（像素大小 5cm）
    - 一张床、一张书桌、一个衣柜
    - 门在底边中间，宽度 0.9m
    """
    pixel_size_m = 0.05
    H, W = 60, 100   # 3m x 5m

    # 房间：先全部设为可走
    room = np.ones((H, W), dtype=np.uint8)

    furnitures: list[Furniture] = []

    # -------------------------
    # 家具1：床，放左上，头朝北（head 靠北侧），人从南侧和两侧接近
    # 尺寸：2.0m(宽, x方向) x 1.5m(高, y方向)
    # -------------------------
    bed_w_px = int(2.0 / pixel_size_m)   # 40
    bed_h_px = int(1.5 / pixel_size_m)   # 30
    bed_y1, bed_x1 = 5, 5
    bed_y2, bed_x2 = bed_y1 + bed_h_px, bed_x1 + bed_w_px
    room[bed_y1:bed_y2, bed_x1:bed_x2] = 0
    furnitures.append(Furniture(
        name="Bed",
        kind="bed",
        y1=bed_y1, y2=bed_y2,
        x1=bed_x1, x2=bed_x2,
        facing="S"     # 人站在床尾(南)这边
    ))

    # -------------------------
    # 家具2：书桌，放中左，前方朝南
    # 尺寸：1.2m x 0.6m
    # -------------------------
    desk_w_px = int(1.2 / pixel_size_m)  # 24
    desk_h_px = int(0.6 / pixel_size_m)  # 12
    desk_y1, desk_x1 = 30, 15
    desk_y2, desk_x2 = desk_y1 + desk_h_px, desk_x1 + desk_w_px
    room[desk_y1:desk_y2, desk_x1:desk_x2] = 0
    furnitures.append(Furniture(
        name="Desk",
        kind="desk",
        y1=desk_y1, y2=desk_y2,
        x1=desk_x1, x2=desk_x2,
        facing="S"
    ))

    # -------------------------
    # 家具3：衣柜，右上，前方朝南
    # 尺寸：1.0m x 0.5m
    # -------------------------
    cab_w_px = int(1.0 / pixel_size_m)   # 20
    cab_h_px = int(0.5 / pixel_size_m)   # 10
    cab_y1, cab_x1 = 5, 75
    cab_y2, cab_x2 = cab_y1 + cab_h_px, cab_x1 + cab_w_px
    room[cab_y1:cab_y2, cab_x1:cab_x2] = 0
    furnitures.append(Furniture(
        name="Wardrobe",
        kind="wardrobe",
        y1=cab_y1, y2=cab_y2,
        x1=cab_x1, x2=cab_x2,
        facing="S"
    ))

    # -------------------------
    # 门：底边中间，宽度 0.9m
    # -------------------------
    door_width_m = 0.9
    door_w_px = int(round(door_width_m / pixel_size_m))
    door_w_px = max(1, door_w_px)

    door_y = H - 2
    door_x_center = W // 2
    half = door_w_px // 2
    x1 = max(0, door_x_center - half)
    x2 = min(W - 1, door_x_center + half)

    # 在底边挖一个门洞（高度 2 像素）
    room[door_y - 1:door_y + 1, x1:x2 + 1] = 1

    doors_px = [(door_y, x) for x in range(x1, x2 + 1)]

    return room, furnitures, doors_px


# -----------------------------------------------------------------------------
# 家具可达区域构造
# -----------------------------------------------------------------------------
def build_access_zone(room: np.ndarray,
                      furn: Furniture,
                      access_depth_px: int = 4,
                      side_margin_px: int = 2) -> np.ndarray:
    """
    根据家具类型 + 朝向，构造 “人可以站立/接近” 的区域。

    参数：
        room            : 0/1 房间网格
        furn            : Furniture 对象
        access_depth_px : 可达区域向外延伸的深度（像素）
        side_margin_px  : 床两侧留出的宽度（像素）
    返回：
        access_zone     : bool 数组，True 表示该格属于该家具的可达区域
    """
    H, W = room.shape
    access = np.zeros_like(room, dtype=bool)

    # 家具 footprint mask
    mask = np.zeros_like(room, dtype=bool)
    mask[furn.y1:furn.y2, furn.x1:furn.x2] = True

    # 先做一圈膨胀（得到环形操作区）
    ring = binary_dilation(mask, iterations=access_depth_px) & (~mask) & (room == 1)

    if furn.kind == "bed":
        # 床：床尾 + 两侧
        # 假设 facing 的方向为床尾所在方向
        if furn.facing == "S":
            # 床尾在南侧
            tail_band = np.zeros_like(room, dtype=bool)
            y_tail_start = furn.y2
            y_tail_end = min(H, furn.y2 + access_depth_px)
            tail_band[y_tail_start:y_tail_end, furn.x1:furn.x2] = True

            # 两侧：在床左右各一条带状区域
            side_band = np.zeros_like(room, dtype=bool)
            # 左侧
            x_left_start = max(0, furn.x1 - access_depth_px)
            side_band[furn.y1:furn.y2, x_left_start:furn.x1] = True
            # 右侧
            x_right_end = min(W, furn.x2 + access_depth_px)
            side_band[furn.y1:furn.y2, furn.x2:x_right_end] = True

            access = ring & (tail_band | side_band)

        else:
            # 为简单起见，其他朝向先统一用 ring（你可以按需要扩展）
            access = ring

    elif furn.kind in ("desk", "wardrobe"):
        # 书桌 & 衣柜：只要“正前方”一条带状区域
        front_band = np.zeros_like(room, dtype=bool)
        if furn.facing == "S":
            y_start = furn.y2
            y_end = min(H, furn.y2 + access_depth_px)
            front_band[y_start:y_end, furn.x1:furn.x2] = True
        elif furn.facing == "N":
            y_start = max(0, furn.y1 - access_depth_px)
            y_end = furn.y1
            front_band[y_start:y_end, furn.x1:furn.x2] = True
        elif furn.facing == "E":
            x_start = furn.x2
            x_end = min(W, furn.x2 + access_depth_px)
            front_band[furn.y1:furn.y2, x_start:x_end] = True
        elif furn.facing == "W":
            x_start = max(0, furn.x1 - access_depth_px)
            x_end = furn.x1
            front_band[furn.y1:furn.y2, x_start:x_end] = True

        access = ring & front_band

    else:
        # 未知类型：先用环形操作区
        access = ring

    return access


# -----------------------------------------------------------------------------
# 从门出发判断可达性
# -----------------------------------------------------------------------------
def compute_reachable(room: np.ndarray, doors_px: list[tuple[int, int]]) -> np.ndarray:
    """
    room: 0/1，可走/障碍
    doors_px: 门口像素列表（y, x）
    返回 reachable: bool 数组
    """
    H, W = room.shape
    free = (room == 1)

    seeds = np.zeros_like(free, dtype=bool)
    for (y, x) in doors_px:
        if 0 <= y < H and 0 <= x < W:
            seeds[y, x] = True

    if not seeds.any():
        return np.zeros_like(free, dtype=bool)

    reachable = binary_propagation(seeds, mask=free)
    return reachable


# -----------------------------------------------------------------------------
# 主流程：判断每个家具是否可达，并可视化
# -----------------------------------------------------------------------------
def main():
    room, furnitures, doors_px = build_demo_room()

    reachable = compute_reachable(room, doors_px)

    H, W = room.shape
    vis = np.zeros((H, W, 3), dtype=np.uint8)

    # 背景：可走区域设为白色，障碍（家具）设为黑色
    vis[room == 1] = (255, 255, 255)
    vis[room == 0] = (0, 0, 0)

    # 从门可达的地方：浅绿色
    vis[reachable & (room == 1)] = (200, 255, 200)

    # 标记门：亮绿色
    for (y, x) in doors_px:
        vis[y, x] = (0, 255, 0)

    # 对每件家具，计算可达区域并判断
    for furn in furnitures:
        access_zone = build_access_zone(room, furn, access_depth_px=4)

        # 可达区域用黄色表示
        vis[access_zone] = (0, 255, 255)

        # 真正可达（从门能走到家具可达区）的部分：品红色
        reachable_access = access_zone & reachable
        vis[reachable_access] = (255, 0, 255)

        accessible = bool(reachable_access.any())
        print(f"{furn.name:9s} 可达? -> {accessible}")

    # 放大显示
    vis_large = cv2.resize(vis, None, fx=6, fy=6, interpolation=cv2.INTER_NEAREST)
    cv2.imshow("Furniture Accessibility from Door", vis_large)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
