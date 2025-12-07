# import numpy as np
# import cv2 as cv
# from collections import deque
# import heapq
# from typing import Tuple, List, Optional, Dict

# Coord = Tuple[int, int]          # (row, col)
# State = Tuple[int, int, int]     # (row, col, theta_idx)


# def rotate_shape_mask(shape_mask: np.ndarray, angle_deg: float) -> np.ndarray:
#     """
#     旋转 shape_mask（0/1 或 bool），保持中心不变，返回旋转后的掩码（同尺寸）。
#     """
#     h, w = shape_mask.shape
#     center = (w / 2.0, h / 2.0)
#     M = cv.getRotationMatrix2D(center, angle_deg, 1.0)
#     rotated = cv.warpAffine(
#         shape_mask.astype(np.uint8),
#         M,
#         (w, h),
#         flags=cv.INTER_NEAREST,
#         borderMode=cv.BORDER_CONSTANT,
#         borderValue=0,
#     )
#     return (rotated > 0).astype(np.uint8)


# def precompute_rotated_masks(shape_mask: np.ndarray, angle_step: int) -> List[np.ndarray]:
#     """
#     预计算每个离散角度下的形状掩码。
#     例如 angle_step=45 => 8 个方向：0,45,...,315 度
#     """
#     num_angles = 360 // angle_step
#     masks = []
#     for i in range(num_angles):
#         angle = i * angle_step
#         masks.append(rotate_shape_mask(shape_mask, angle))
#     return masks


# def is_state_valid(
#     occ: np.ndarray,
#     masks: List[np.ndarray],
#     r: int,
#     c: int,
#     theta_idx: int,
# ) -> bool:
#     """
#     判定给定状态 (r,c,theta_idx) 是否碰撞：
#     - occ: 0 = free, 1 = obstacle
#     - masks[theta_idx]: 以中心为物体位置的掩码
#     """
#     h, w = occ.shape
#     mask = masks[theta_idx]
#     mh, mw = mask.shape

#     # 把 (r,c) 视为 mask 的中心
#     top = r - mh // 2
#     left = c - mw // 2
#     bottom = top + mh
#     right = left + mw

#     # 出界就视为非法
#     if top < 0 or left < 0 or bottom > h or right > w:
#         return False

#     roi = occ[top:bottom, left:right]
#     # 只要 mask=1 的地方，碰到 occ=1 就碰撞
#     collision = np.any((mask == 1) & (roi == 1))
#     return not collision


# def reconstruct_path(
#     came_from: Dict[State, Optional[State]],
#     current: State
# ) -> List[State]:
#     """
#     从 came_from 字典中回溯路径。
#     """
#     path = [current]
#     while came_from[current] is not None:
#         current = came_from[current]
#         path.append(current)
#     path.reverse()
#     return path


# def find_path_with_shape(
#     img: np.ndarray,
#     start: Coord,
#     goal: Coord,
#     bg_thresh: int,
#     shape_mask: np.ndarray,
#     angle_step: int = 45,
#     strategy: str = "astar",
# ) -> Optional[List[State]]:
#     """
#     在灰度图 img 上，从 start 到 goal 寻路：
#     - img: 2D uint8 灰度图
#     - start / goal: (row, col)
#     - bg_thresh: 像素 >= bg_thresh 视为可走；< bg_thresh 视为障碍
#     - shape_mask: 物体形状掩码（2D，0/1，中心为物体参考点）
#     - angle_step: 角度离散步长（例如 45 -> 0..315，共 8 个朝向）
#     - strategy: "bfs" 或 "astar"

#     返回：
#     - None: 无路
#     - List[State]: 路径序列，每个元素为 (row, col, theta_idx)
#                    实际朝向角度 = theta_idx * angle_step
#     """
#     assert img.ndim == 2, "img 必须为灰度图 (H,W)"

#     H, W = img.shape
#     # 生成 occupancy grid：1=obstacle, 0=free
#     occ = (img < bg_thresh).astype(np.uint8)

#     # 预计算不同角度的 shape 掩码
#     masks = precompute_rotated_masks(shape_mask, angle_step)
#     num_angles = len(masks)

#     sr, sc = start
#     gr, gc = goal

#     # 起点、终点从 orientation=0 开始（也可以参数化）
#     start_state: State = (sr, sc, 0)

#     # 起点或终点如果本身就碰撞，直接失败
#     if not is_state_valid(occ, masks, *start_state):
#         print("起点无效（碰撞或出界）")
#         return None
#     # 终点只要求某个朝向可行（不强制 orientation=0）
#     goal_valid_any_orientation = any(
#         is_state_valid(occ, masks, gr, gc, theta_idx)
#         for theta_idx in range(num_angles)
#     )
#     if not goal_valid_any_orientation:
#         print("终点无效（所有朝向均碰撞）")
#         return None

#     # 8 邻域平移动作
#     moves = [
#         (-1, 0),  # 上
#         (1, 0),   # 下
#         (0, -1),  # 左
#         (0, 1),   # 右
#         (-1, -1), # 左上
#         (-1, 1),  # 右上
#         (1, -1),  # 左下
#         (1, 1),   # 右下
#     ]

#     # 旋转动作：朝向索引 +/- 1（也可以扩展成 +/-k）
#     rot_actions = [-1, 1]

#     # visited[r,c,theta_idx]
#     visited = np.zeros((H, W, num_angles), dtype=bool)
#     visited[sr, sc, 0] = True

#     came_from: Dict[State, Optional[State]] = {start_state: None}

#     def is_goal(r: int, c: int) -> bool:
#         return (r == gr) and (c == gc)

#     # 启发式：位置距离（忽略角度）
#     def heuristic(r: int, c: int) -> float:
#         return np.hypot(r - gr, c - gc)

#     # 根据策略选择容器
#     if strategy == "bfs":
#         frontier = deque()
#         frontier.append(start_state)
#         cost_so_far = None  # BFS 不需要代价表
#     elif strategy == "astar":
#         frontier = []
#         # 元素：(f, g, (r,c,theta_idx))
#         heapq.heappush(frontier, (heuristic(sr, sc), 0.0, start_state))
#         cost_so_far: Dict[State, float] = {start_state: 0.0}
#     else:
#         raise ValueError("strategy 必须是 'bfs' 或 'astar'")

#     while frontier:
#         if strategy == "bfs":
#             r, c, theta_idx = frontier.popleft()
#             g_cost = 0.0  # BFS 不使用
#         else:  # A*
#             f, g_cost, (r, c, theta_idx) = heapq.heappop(frontier)

#         # 如果位置到达终点（不要求角度），结束
#         if is_goal(r, c):
#             # 在这里不再检查终点角度是否碰撞，因为前面展开邻居时已经检查过
#             return reconstruct_path(came_from, (r, c, theta_idx))

#         # 1) 平移动作（8 邻域）
#         for dr, dc in moves:
#             nr, nc = r + dr, c + dc
#             ntheta = theta_idx

#             if not (0 <= nr < H and 0 <= nc < W):
#                 continue

#             # 这里既要检查 occ 也要检查 shape 碰撞
#             if occ[nr, nc] == 1:
#                 continue
#             if not is_state_valid(occ, masks, nr, nc, ntheta):
#                 continue

#             next_state: State = (nr, nc, ntheta)
#             if strategy == "bfs":
#                 if not visited[nr, nc, ntheta]:
#                     visited[nr, nc, ntheta] = True
#                     came_from[next_state] = (r, c, theta_idx)
#                     frontier.append(next_state)
#             else:  # A*
#                 new_cost = g_cost + np.hypot(dr, dc)  # 对角 约 1.414，直线 1
#                 if (not visited[nr, nc, ntheta]) or (next_state not in cost_so_far) or (new_cost < cost_so_far[next_state]):
#                     visited[nr, nc, ntheta] = True
#                     cost_so_far[next_state] = new_cost
#                     priority = new_cost + heuristic(nr, nc)
#                     heapq.heappush(frontier, (priority, new_cost, next_state))
#                     came_from[next_state] = (r, c, theta_idx)

#         # 2) 原地旋转动作（不改变 r,c）
#         for dtheta in rot_actions:
#             ntheta = (theta_idx + dtheta) % num_angles
#             nr, nc = r, c

#             if not is_state_valid(occ, masks, nr, nc, ntheta):
#                 continue

#             next_state = (nr, nc, ntheta)
#             if strategy == "bfs":
#                 if not visited[nr, nc, ntheta]:
#                     visited[nr, nc, ntheta] = True
#                     came_from[next_state] = (r, c, theta_idx)
#                     frontier.append(next_state)
#             else:  # A*
#                 # 旋转也给一个小代价（比如 0.5）
#                 new_cost = g_cost + 0.5
#                 if (not visited[nr, nc, ntheta]) or (next_state not in cost_so_far) or (new_cost < cost_so_far[next_state]):
#                     visited[nr, nc, ntheta] = True
#                     cost_so_far[next_state] = new_cost
#                     priority = new_cost + heuristic(nr, nc)
#                     heapq.heappush(frontier, (priority, new_cost, next_state))
#                     came_from[next_state] = (r, c, theta_idx)

#     # 没有找到路径
#     return None

# if __name__ == "__main__":
#     img = cv.imread("room.png", cv.IMREAD_GRAYSCALE)

#     # 背景色阈值：比如 200 以上算可走
#     bg_thresh = 200

#     # 定义一个简单的矩形形状（3x5 像素），中心为参考点
#     shape_mask = np.zeros((5, 9), dtype=np.uint8)
#     shape_mask[1:4, 2:7] = 1    # 中间一块矩形

#     start = (10, 10)  # (row, col)
#     goal  = (80, 120)

#     path = find_path_with_shape(
#         img,
#         start,
#         goal,
#         bg_thresh,
#         shape_mask,
#         angle_step=45,
#         strategy="astar",
#     )

#     if path is None:
#         print("无路径")
#     else:
#         print(f"找到路径，长度 = {len(path)}")
#         # 画一下路径（只画位置，忽略角度）
#         img_color = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
#         for r, c, theta_idx in path:
#             img_color[r, c] = (0, 0, 255)  # 红色
#         cv.imshow("path", img_color)
#         cv.waitKey(0)
#         cv.destroyAllWindows()
