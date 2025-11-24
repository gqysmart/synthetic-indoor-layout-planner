# app/planner_core/solver_MVT.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, List

Vec = Tuple[float, float]
Rect = Tuple[float, float, float, float]  # (x_min, y_min, x_max, y_max)
EPS = 1e-12

# -----------------------------
# 基础数据结构
# -----------------------------

@dataclass
class Pose:
    x: float
    y: float
    theta: int = 0  # 0 or 90 (degrees), 仅轴对齐旋转

@dataclass
class Furniture:
    id: str
    w: float                  # 宽（m）
    h: float                  # 高（m）
    margin: float = 0.0       # 与他物/墙的净距（m），用于膨胀
    pose: Pose = field(default_factory=lambda: Pose(0.0, 0.0, 0))  # 左上角 + 朝向（0/90）

@dataclass
class Room:
    width: float
    height: float
    wall_clearance: float = 0.0  # 房间内缩量，用于墙面净距

@dataclass
class Options:
    step: float = 0.02          # 邻域平移步长（m）
    mtv_scale: float = 1.0      # 沿 MTV 的缩放（1.0 = 一次到位）
    max_steps: int = 800
    first_improvement: bool = False  # 邻域内是否“见好就收”；False = 选最优更稳

# -----------------------------
# 几何辅助
# -----------------------------

def dims_with_theta(w: float, h: float, theta: int) -> Tuple[float, float]:
    return (h, w) if (theta // 90) % 2 == 1 else (w, h)

def rect_of_furniture(f: Furniture, pose: Pose, inflate: float = 0.0) -> Rect:
    # 以 pose 为左上角（x,y），theta 仅 0/90：尺寸互换
    w, h = dims_with_theta(f.w, f.h, pose.theta)
    xin = pose.x - inflate
    yin = pose.y - inflate
    win = w + 2 * inflate
    hin = h + 2 * inflate
    return (xin, yin, xin + win, yin + hin)

def rect_area(r: Rect) -> float:
    x1, y1, x2, y2 = r
    if x2 <= x1 or y2 <= y1:
        return 0.0
    return (x2 - x1) * (y2 - y1)


def rect_intersection(a: Rect, b: Rect) -> Rect:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    x1 = max(ax1, bx1)
    y1 = max(ay1, by1)
    x2 = min(ax2, bx2)
    y2 = min(ay2, by2)
# 没有交集时，返回空矩形
    if x1 >= x2 or y1 >= y2:
        return (0.0, 0.0, 0.0, 0.0)
    
    return (x1, y1, x2, y2)

def rect_outside_area(r: Rect, room_inner: Rect) -> float:
    """r 为膨胀后的矩形；返回越界面积。"""
    rin = rect_intersection(r, room_inner)
    return max(0.0, rect_area(r) - rect_area(rin))

def mtv_rect_rect(a: Rect, b: Rect) -> Optional[Vec]:
    """
    轴对齐矩形最小平移向量（让 a 与 b 分离）。若不相交，返回 None。
    方向取“把 a 推离 b”的向量；长度为最小分离距离。
    """
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    # 无相交
    if ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1:
        return None

    # 四个分离候选（取最小）
    move_left   = ax2 - bx1   # a 向左
    move_right  = bx2 - ax1   # a 向右
    move_up     = ay2 - by1   # a 向上
    move_down   = by2 - ay1   # a 向下
    candidates: List[Tuple[float, Vec]] = [
        (abs(move_left),  (-move_left, 0.0)),
        (abs(move_right), (move_right, 0.0)),
        (abs(move_up),    (0.0, -move_up)),
        (abs(move_down),  (0.0, move_down)),
    ]
    return min(candidates, key=lambda t: t[0])[1]

def mtv_to_interior(r: Rect, room_inner: Rect) -> Optional[Vec]:
    """
    若 r 越界 room_inner，则给出最小修复向量（把 r 推回 room_inner）。若未越界返回 None。
    """
    rx1, ry1, rx2, ry2 = r
    kx1, ky1, kx2, ky2 = room_inner

    left_over  = max(0.0, kx1 - rx1)  # 向右
    right_over = max(0.0, rx2 - kx2)  # 向左
    top_over   = max(0.0, ky1 - ry1)  # 向下
    bot_over   = max(0.0, ry2 - ky2)  # 向上

    moves: List[Tuple[float, Vec]] = []
    if left_over  > 0: moves.append((left_over,  ( left_over, 0.0)))
    if right_over > 0: moves.append((right_over, (-right_over, 0.0)))
    if top_over   > 0: moves.append((top_over,   (0.0,  top_over)))
    if bot_over   > 0: moves.append((bot_over,   (0.0, -bot_over)))

    return None if not moves else min(moves, key=lambda t: t[0])[1]

def apply_vec(p: Pose, v: Vec, scale: float = 1.0) -> Pose:
    return Pose(p.x + v[0] * scale, p.y + v[1] * scale, p.theta)

def rotate90(p: Pose) -> Pose:
    # 注意：绕左上角旋转（AABB 模式足够）。如需绕中心，需改为按中心回推。
    return Pose(p.x, p.y, (p.theta + 90) % 180)

# -----------------------------
# 违约度 J 及全局选择
# -----------------------------
# J = total cost

def room_inner_rect(room: Room) -> Rect:
    c = room.wall_clearance
    return (c, c, room.width - c, room.height - c)

def overlap_with_others(fid: str,
                        rect_i: Rect,
                        placed_rects: Dict[str, Rect]) -> float:
    """与其他（膨胀后）矩形求交面积之和。"""
    s = 0.0
    for gid, r in placed_rects.items():
        if gid == fid:
            continue
        inter = rect_intersection(rect_i, r)
        s += rect_area(inter)
    return s

def compute_J_for_item(fid: str,
                       rect_i: Rect,
                       room_inner: Rect,
                       placed_rects: Dict[str, Rect]) -> Tuple[float, float, float]:
    """返回 (J_i, A_i, B_i)，J_i = 与他物交叠面积 A_i + 越界面积 B_i。"""
    A_i = overlap_with_others(fid, rect_i, placed_rects)
    B_i = rect_outside_area(rect_i, room_inner)
    return (A_i + B_i, A_i, B_i)

def pick_item_to_move(placed: Dict[str, Furniture],
                      room: Room) -> Tuple[str, float, float, float, Rect, Dict[str, Rect]]:
    """全局扫描每件家具，返回 J 最大者的信息。"""
    rin = room_inner_rect(room)
    placed_rects: Dict[str, Rect] = {fid: rect_of_furniture(f, f.pose, inflate=f.margin)
                                     for fid, f in placed.items()}

    best_fid = None
    best_J, best_A, best_B = -1.0, 0.0, 0.0
    best_rect = (0.0, 0.0, 0.0, 0.0)
    for fid, f in placed.items():
        rect_i = placed_rects[fid]
        J, A, B = compute_J_for_item(fid, rect_i, rin, placed_rects)
        if J > best_J:
            best_fid, best_J, best_A, best_B, best_rect = fid, J, A, B, rect_i

    # 这里保证至少返回一个 fid（若全 0，不会走到这里；solve_MVT 开头会先 all_clear）
    return best_fid, best_J, best_A, best_B, best_rect, placed_rects

# -----------------------------
# 单步移动（对选中的家具）
# -----------------------------

def step_move_one(fid: str,
                  placed: Dict[str, Furniture],
                  room: Room,
                  placed_rects: Dict[str, Rect],
                  rect_i: Rect,
                  A_i: float,
                  B_i: float,
                  opts: Options) -> bool:
    """
    为 fid 生成候选：
      1) MTV 连续推进（最多 3 次）——优先；
      2) 小邻域：±step 平移、旋转 90°。
    评估 J 最小，若改进则提交。
    """
    f = placed[fid]
    rin = room_inner_rect(room)

    # 选择优先修复的 MTV：越界 vs 他物，按贡献大的优先
    def choose_mtv(rect_now: Rect) -> Optional[Vec]:
        mtv_out = mtv_to_interior(rect_now, rin)
        mtv_obj: Optional[Vec] = None
        if overlap_with_others(fid, rect_now, placed_rects) > 0.0:
            best_mtv = None
            best_len = float("inf")
            for gid, r in placed_rects.items():
                if gid == fid:
                    continue
                mv = mtv_rect_rect(rect_now, r)
                if mv is None:
                    continue
                L = abs(mv[0]) + abs(mv[1])  # L1 足够；也可用 L2
                if L < best_len:
                    best_len = L
                    best_mtv = mv
            mtv_obj = best_mtv
        # A_i 与 B_i 的比较基于初始估计；此处做一次简单选择
        return (mtv_obj or mtv_out) if A_i >= B_i else (mtv_out or mtv_obj)

    base_J = A_i + B_i
    best_pose = f.pose
    best_J = base_J

    # --- (1) MTV 连续推进（最多 3 次），尽量一次把重叠彻底分开 ---
    pose_try = f.pose
    rect_try = rect_i
    for _ in range(3):
        mtv_pick = choose_mtv(rect_try)
        if mtv_pick is None:
            break
        pose_try = apply_vec(pose_try, mtv_pick, opts.mtv_scale)
        rect_try = rect_of_furniture(f, pose_try, inflate=f.margin)
        J_q, _, _ = compute_J_for_item(fid, rect_try, rin, placed_rects | {fid: rect_try})
        if J_q + EPS < best_J:
            best_J = J_q
            best_pose = pose_try
        # 若没有继续下降，就停止连续推进
        else:
            break

    if best_J + EPS < base_J:
        placed[fid].pose = best_pose
        return True

    # --- (2) 小邻域：±step 平移 + 旋转 90° ---
    neigh: List[Pose] = []
    s = opts.step
    for dx, dy in [(s,0), (-s,0), (0,s), (0,-s), (2*s,0), (-2*s,0), (0,2*s), (0,-2*s)]:
        neigh.append(Pose(f.pose.x + dx, f.pose.y + dy, f.pose.theta))
    neigh.append(rotate90(f.pose))

    for q in neigh:
        r_q = rect_of_furniture(f, q, inflate=f.margin)
        J_q, _, _ = compute_J_for_item(fid, r_q, rin, placed_rects | {fid: r_q})
        if J_q + EPS < best_J:
            best_J = J_q
            best_pose = q
            if opts.first_improvement:
                break

    if best_J + EPS < base_J:
        placed[fid].pose = best_pose
        return True

    return False

# -----------------------------
# 顶层：全局 MTV 调度求解（无回溯）
# -----------------------------

def all_clear(placed: Dict[str, Furniture], room: Room) -> tuple[bool, float, float]:
    """所有家具都无重叠且不越界才算通过。"""
    rin = room_inner_rect(room)
    rects = {fid: rect_of_furniture(f, f.pose, inflate=f.margin) for fid, f in placed.items()}
    A_total = 0.0
    B_total = 0.0
    for fid, r in rects.items():
        A_i = overlap_with_others(fid, r, rects)
        B_i = rect_outside_area(r, rin)
        A_total += A_i
        B_total += B_i
        if A_i > EPS or B_i > EPS:
            return False, A_total, B_total
    return True, A_total, B_total

def solve_MVT(room: Room,
              items: List[Furniture],
              opts: Options | None = None) -> Dict:
    if opts is None:
        opts = Options()

    placed: Dict[str, Furniture] = {f.id: f for f in items}

    for step in range(opts.max_steps):
        # 1) 全体校验：只有全部无违约才退出
        clear, A_tot, B_tot = all_clear(placed, room)
        if clear:
            return {
                "ok": True,
                "reason": "no-overlap-and-inside",
                "steps": step,
                "placements": {k: (v.pose.x, v.pose.y, v.pose.theta) for k, v in placed.items()},
            }

        # 2) 选择违约度最大的那件
        fid, J_star, A_i, B_i, rect_i, placed_rects = pick_item_to_move(placed, room)

        # 3) 单步改进：MTV 连续推进 + 小邻域
        moved = step_move_one(fid, placed, room, placed_rects, rect_i, A_i, B_i, opts)
        if not moved:
            # 4) 兜底：纯旋转尝试一次
            p_rot = rotate90(placed[fid].pose)
            r_rot = rect_of_furniture(placed[fid], p_rot, inflate=placed[fid].margin)
            rin = room_inner_rect(room)
            J_rot, _, _ = compute_J_for_item(fid, r_rot, rin, placed_rects | {fid: r_rot})
            if J_rot + EPS < J_star:
                placed[fid].pose = p_rot
            else:
                return {
                    "ok": False,
                    "reason": f"stalled at step {step} on {fid}",
                    "steps": step,
                    "placements": {k: (v.pose.x, v.pose.y, v.pose.theta) for k, v in placed.items()},
                }

    return {
        "ok": False,
        "reason": "max_steps_reached",
        "steps": opts.max_steps,
        "placements": {k: (v.pose.x, v.pose.y, v.pose.theta) for k, v in placed.items()},
    }

# -----------------------------
# 简单自测（可删除）
# -----------------------------
if __name__ == "__main__":
    room = Room(width=4.0, height=3.0, wall_clearance=0.05)

    bed   = Furniture(id="bed",  w=2.0, h=1.6, margin=0.06, pose=Pose(0.4, 0.4, 0))
    desk  = Furniture(id="desk", w=1.2, h=0.6, margin=0.04, pose=Pose(1.1, 0.7, 0))
    sofa  = Furniture(id="sofa", w=1.6, h=0.8, margin=0.05, pose=Pose(1.0, 1.0, 0))

    res = solve_MVT(room, [bed, desk, sofa], Options(step=0.03, mtv_scale=1.0, first_improvement=False))
    print(res["ok"], res["reason"], "steps:", res["steps"])
    for k, p in res["placements"].items():
        print(k, p)
