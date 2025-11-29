from collections import deque
from typing import Dict, Optional, Tuple, List
import heapq
import math

from silp.lib.debug.debug import Debug

import numpy as np

from silp.core.geometry.coorinate_system import PixelCoordinateSystem
from silp.core.geometry.shape import Rectangle
from silp.services.planner.navigation_field import PixelNavigationField, SimpleAgent
from silp.domain.layout import room_example_a
from silp.domain.furniture import (
    furniture_example_table,
    furniture_example_desk_round,
    furniture_example_bed,
    furniture_example_wardrobe,
)

State = Tuple[int, int]  # (row, col)
NEIGHBORS: List[Tuple[int, int]] = [
    (-1, 0),  # up
    (1, 0),   # down
    (0, -1),  # left
    (0, 1),   # right
]


def heuristic(a: State, b: State) -> float:
    """A* 的启发式：用像素网格上的欧氏距离。"""
    ar, ac = a
    br, bc = b
    return math.hypot(ar - br, ac - bc)


def astar_shortest_path(
    start: State,
    goal: State,
    nav: PixelNavigationField,
    debug: Optional[Debug] = None,
) -> Optional[List[State]]:
    """
    在 nav.walkable_mask 上用 A* 寻找从 start 到 goal 的最短路径。

    参数:
    - start: 起点 (row, col)
    - goal: 终点 (row, col)
    - nav: PixelNavigationField，提供 is_walkable 和 canvas_size

    返回:
    - 如果有路径，返回状态列表 [ (r0,c0), (r1,c1), ... ]
    - 如果无路径，返回 None
    """
    if debug is not None:
        nav.set_debug(debug)

    sr, sc = start
    gr, gc = goal

    if not nav.is_walkable(sr, sc) or not nav.is_walkable(gr, gc):
        return None

    width, height = nav.pcs.canvas_size  # (w, h)
    # 注意：数组 shape 是 (height, width)
    g_score = np.full((height, width), np.inf, dtype=float)
    g_score[sr, sc] = 0.0

    # open set: (f_score, g_score, (r,c))
    open_heap: List[Tuple[float, float, State]] = []
    heapq.heappush(open_heap, (heuristic(start, goal), 0.0, start))

    came_from: Dict[State, Optional[State]] = {start: None}

    while open_heap:
        f_cur, g_cur, current = heapq.heappop(open_heap)
        r, c = current

        # 如果这个条目已经过时（有更好的 g_score 了），跳过
        if g_cur > g_score[r, c]:
            continue

        if current == goal:
            # 回溯路径
            path: List[State] = []
            node: Optional[State] = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path

        for dr, dc in NEIGHBORS:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < height and 0 <= nc < width):
                continue
            if not nav.is_walkable(nr, nc):
                continue

            tentative_g = g_cur + 1.0  # 每一步代价 = 1

            if tentative_g < g_score[nr, nc]:
                g_score[nr, nc] = tentative_g
                neighbor: State = (nr, nc)
                came_from[neighbor] = current
                f_neighbor = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f_neighbor, tentative_g, neighbor))

    # open set 耗尽仍没找到
    return None

if __name__ == "__main__":
    room = room_example_a
    furniture_list = [
        # furniture_example_table,
        # furniture_example_desk_round,
        # furniture_example_bed,
        # furniture_example_wardrobe
    ]

    rect: Rectangle = room.shape
    room_w = rect.width
    room_h = rect.height

    pixels_per_meter = 100
    pcs = PixelCoordinateSystem(
        pixels_per_meter=pixels_per_meter,
        canvas_size=(
            int(np.ceil(room_w * pixels_per_meter)) + 40,
            int(np.ceil(room_h * pixels_per_meter)) + 40,
        ),
        center_world=(0.0, 0.0),
    )

    agent = SimpleAgent(radius_m=0.3)

    nav = PixelNavigationField(pcs).from_room_and_furniture_with_simple_agent(
        room=room,
        furniture_list=furniture_list,
        agent=agent,
    )

    start = (50, 50)
    goal = (220, 300) 

    path = astar_shortest_path(start, goal, nav)
    print("Found path:", path)
