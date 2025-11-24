from __future__ import annotations
from collections import deque
from dataclasses import replace
from typing import List, Tuple, Dict, Optional
import math
from silp.core.geometry.placed_entity import PlacedEntity
from silp.core.geometry.coorinate_system import PixelCoordinateSystem, Transform


import numpy as np
import cv2 as cv
from enum import Enum
import time

from silp.domain.layout import layout_example_a, layout_example_b 

State = Tuple[int, int, int]  # (row, col, theta_deg)

class MaskValue(Enum):
    CONTAINER = 200
    OBSTACLE = 10
    FURNITURE = 1

path_states_debug: List[State] = []
image_debug: np.ndarray = None
debug_time_start: float = 0.0
debug_time_end: float = 0.0

debug = True

def find_path_bfs(
    entity: PlacedEntity,
    container: PlacedEntity,
    obstacle_list: List[PlacedEntity],
    start: Transform,      # 假定 start.r 是“度”
    goal: Transform,       # 假定 goal.r 也是“度”
    pcs: PixelCoordinateSystem,
    step_theta: float = 90.0,   # 以度为单位
) -> List[Transform]:
    # ======== 角度离散：全用“度” ========
    ###debug
    global debug_time_start
    debug_time_start = time.perf_counter()
    ### debug end

    step_theta_deg = step_theta
    num_theta = int(360 / step_theta_deg)

    def theta_to_idx(theta_deg: int) -> int:
        return int(theta_deg // step_theta_deg) % num_theta

    # ======== 1. State -> Transform / PlacedEntity ========

    def make_transform_from_state(state: State) -> Transform:
        r, c, theta_deg = state
        x, y = pcs.pixel_to_world(c, r)
        # 用 start 作为模板，只改 x, y, r
        return Transform(x=x, y=y, r=theta_deg)

    entity_tempt = entity.clone()

    def make_temp_placed_entity_from_state(state: State) -> PlacedEntity:
        new_t = make_transform_from_state(state)
        return replace(entity_tempt, transform=new_t)

    # ======== 2. goal 判定（像素 + 角度） ========

    gr, gc = pcs.world_to_pixel(goal.x, goal.y)
    # 把 goal 的角度 snap 到离散网格（比如 37° → 45°）
    goal_theta_snapped = round(goal.r / step_theta_deg) * step_theta_deg % 360

    def is_goal_state(state: State) -> bool:
        r, c, theta_deg = state
        return (r == gr) and (c == gc) and (theta_deg == goal_theta_snapped)

    # ======== 3. 建立 mask（略，沿用你那一段） ========

    height_px, width_px = pcs.canvas_size
    base_mask = np.zeros((height_px, width_px), dtype=np.uint8)

    container_poly_world = container.world_polygon()
    container_mask = pcs.polygon_to_mask(container_poly_world, value=MaskValue.CONTAINER.value)
    base_mask[container_mask == MaskValue.CONTAINER.value] = MaskValue.CONTAINER.value
 

    obstacle_mask = pcs.empty_mask()
    for obs in obstacle_list:
        poly_world = obs.world_polygon()
        m = pcs.polygon_to_mask(poly_world, value=MaskValue.OBSTACLE.value)
        obstacle_mask[m == MaskValue.OBSTACLE.value] = MaskValue.OBSTACLE.value

    free_mask = (
        (obstacle_mask != MaskValue.OBSTACLE.value)
        & (base_mask == MaskValue.CONTAINER.value)
    )

    h, w = free_mask.shape

    # ======== 4. 状态合法性检查 ========

    def is_state_valid(state: State) -> bool:
        r, c, theta_deg = state
        if not (0 <= r < h and 0 <= c < w):
            return False
        if not free_mask[r, c]:
            return False

        e_tmp = make_temp_placed_entity_from_state(state)
        entity_mask = pcs.polygon_to_mask(e_tmp.world_polygon(), value=MaskValue.FURNITURE.value)

        if np.any(
            (entity_mask == MaskValue.FURNITURE.value)
            & (container_mask != MaskValue.CONTAINER.value)
        ):
            return False

        if np.any(
            (entity_mask == MaskValue.FURNITURE.value)
            & (obstacle_mask == MaskValue.OBSTACLE.value)
        ):
            return False

        return True

    # ======== 5. BFS 搜索 ========

    sx, sy = start.x, start.y
    start_theta_deg = start.r % 360
    sr, sc = pcs.world_to_pixel(sx, sy)

    start_state: State = (sr, sc, int(start_theta_deg))

    if not is_state_valid(start_state):
        return []

    from collections import deque
    q: deque[State] = deque()
    q.append(start_state)

    visited = np.zeros((h, w, num_theta), dtype=bool)
    visited[sr, sc, theta_to_idx(start_theta_deg)] = True

    parent: Dict[State, Optional[State]] = {start_state: None}

    move_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    found_goal: Optional[State] = None

    while q:
        state = q.popleft()

        if is_goal_state(state):
            found_goal = state
            break

        r, c, theta_deg = state
        theta_idx = theta_to_idx(theta_deg)

        # 1）平移：角度不变
        for dr, dc in move_dirs:
            nr, nc = r + dr, c + dc
            ntheta_deg = theta_deg
            ntheta_idx = theta_idx
            next_state: State = (nr, nc, ntheta_deg)

            if (
                0 <= nr < h
                and 0 <= nc < w
                and not visited[nr, nc, ntheta_idx]
                and is_state_valid(next_state)
            ):
                visited[nr, nc, ntheta_idx] = True
                parent[next_state] = state
                q.append(next_state)

        # 2）旋转：原地转动
        for d in (-1, 1):
            ntheta_deg = (theta_deg + d * step_theta_deg) % 360
            ntheta_idx = theta_to_idx(ntheta_deg)
            next_state: State = (r, c, int(ntheta_deg))

            if not visited[r, c, ntheta_idx] and is_state_valid(next_state):
                visited[r, c, ntheta_idx] = True
                parent[next_state] = state
                q.append(next_state)

    # ======== 6. 回溯 ========

    if found_goal is None:
        return []

    path_states: List[State] = []
    cur: Optional[State] = found_goal
    while cur is not None:
        path_states.append(cur)
        cur = parent[cur]

    path_states.reverse()
    ###debug
    global image_debug
    image_debug = base_mask.copy()
    global path_states_debug
    path_states_debug= path_states
    global debug_time_end
    debug_time_end = time.perf_counter()
    
    if debug:
        print(f"BFS pathfinding took {debug_time_end - debug_time_start:.4f} seconds")  
    ### debug end

    path_transforms: List[Transform] = [make_transform_from_state(s) for s in path_states]
    return path_transforms

if __name__ == "__main__":
    furniture = layout_example_a.furnitures[0]
    container = layout_example_a.room
    obstacles: List[PlacedEntity] = []

    start_t = Transform  # 假定 r 是角度
    goal_t = furniture.transform.clone()

    pcs = PixelCoordinateSystem(
        pixels_per_meter=100,
        canvas_size=(500, 500),      # 建议约定为 (height, width)
        center_world=(0.0, 0.0),
    )

    path = find_path_bfs(
        entity=furniture,
        container=container,
        obstacle_list=obstacles,
        start=start_t,
        goal=goal_t,
        pcs=pcs,
        step_theta=90.0,
    )

    # === Debug 图像 ===
    # image_debug 此时应该是 (H, W) 的 uint8 灰度图
    if image_debug is None:
        raise RuntimeError("image_debug 还没被设置，检查 find_path_bfs 里的 global 代码")

    # 扩成三通道
    W,H = pcs.canvas_size
    image = np.zeros((H, W, 3), dtype=np.uint8)
    image[:] = image_debug[..., np.newaxis]  # broadcast 到 3 个通道

    # 把 BFS 路径画出来（红色小点）
    print("Debug BFS path steps:", len(path_states_debug))
    for (r, c, theta_deg) in path_states_debug:
        print(f"Path step: row={r}, col={c}, theta={theta_deg}")
        cv.circle(image, (c, r), 2, (0, 0, 255), -1)

    cv.imshow("Debug Pathfinding", image)
    cv.waitKey(0)
    cv.destroyAllWindows()
