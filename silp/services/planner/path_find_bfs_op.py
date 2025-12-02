from collections import deque
from typing import Dict, Optional, Tuple, List

import numpy as np

from silp.core.geometry.coorinate_system import PixelCoordinateSystem
from silp.core.geometry.shape import Rectangle
from silp.domain.room import Room
from silp.lib.debug.debug import Debug
from silp.services.planner.navigation_field import PixelNavigationField, SimpleAgent
from silp.domain.layout import room_example_a
from silp.domain.furniture import (
    Furniture,
    furniture_example_table,
    furniture_example_desk_round,
    furniture_example_bed,
    furniture_example_wardrobe,
)

State = Tuple[int, int]  # (row, col)
NEIGHBORS: List[Tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 上下左右


def bfs_shortest_path(
    start: State,
    goal: State,
    nav: PixelNavigationField,
    debug: Optional[Debug] = None,
) -> Optional[List[State]]:
    """
    使用广度优先搜索（BFS）算法在网格中找到从起点到终点的最短路径。

    参数:
    - start: 起始状态 (row, col)
    - goal: 目标状态 (row, col)
    - nav: PixelNavigationField 对象，提供网格信息和障碍物检测功能。
    """
  
    sr, sc = start
    gr, gc = goal

    # 起点或终点不可走，直接返回 None
    if not nav.is_walkable(sr, sc) or not nav.is_walkable(gr, gc):
        return None

    width, height = nav.pcs.canvas_size  # (width_px, height_px)
    visited = np.zeros((height, width), dtype=bool)
    parent: Dict[State, Optional[State]] = {}

    q: deque[State] = deque()
    q.append(start)
    visited[sr, sc] = True
    parent[start] = None

    while q:
        r, c = q.popleft()
        cur: State = (r, c)

        if cur == goal:
            # 回溯路径
            path: List[State] = []
            node: Optional[State] = cur
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return path

        for dr, dc in NEIGHBORS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < height and 0 <= nc < width and not visited[nr, nc]:
                if nav.is_walkable(nr, nc):
                    visited[nr, nc] = True
                    parent[(nr, nc)] = cur
                    q.append((nr, nc))

    # 如果队列耗尽也没找到
    return None

