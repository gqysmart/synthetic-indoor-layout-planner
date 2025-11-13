# ---------- 渲染与测试（OpenCV） ----------
import cv2
import numpy as np
from typing import List, Tuple
from  solver_MVT import (
    Room,
    Furniture,
    Pose,
    Options,
    solve_MVT,
    rect_of_furniture,
)

def _m2px(x: float, y: float, scale: int) -> Tuple[int, int]:
    return int(round(x * scale)), int(round(y * scale))

def draw_rect(img, rect: Tuple[float,float,float,float], scale: int, color, thickness=2, filled=False):
    x1,y1,x2,y2 = rect
    p1 = _m2px(x1, y1, scale)
    p2 = _m2px(x2, y2, scale)
    if filled:
        cv2.rectangle(img, p1, p2, color, thickness=cv2.FILLED, lineType=cv2.LINE_AA)
    cv2.rectangle(img, p1, p2, color, thickness=thickness, lineType=cv2.LINE_AA)

def render_scene_png(path: str,
                     room: Room,
                     items: List[Furniture],
                     title: str = "",
                     scale: int = 200,
                     show_margin: bool = True):
    """
    渲染当前房间与家具到 PNG。
    - room: 宽高（米），wall_clearance 作为内缩边界可视化一圈灰线
    - items: 使用每件家具的 pose + margin
    """
    W, H = _m2px(room.width, room.height, scale)
    canvas = np.full((H+100, W+100, 3), 255, np.uint8)  # 留边距
    ox, oy = 50, 50  # 画布内边距像素

    # 背景
    cv2.rectangle(canvas, (ox, oy), (ox+W, oy+H), (230, 230, 230), thickness=cv2.FILLED)

    # 房间外框
    cv2.rectangle(canvas, (ox, oy), (ox+W, oy+H), (0, 0, 0), thickness=2)

    # 内缩墙距（可视化）
    if room.wall_clearance > 1e-9:
        c = room.wall_clearance
        x1,y1 = _m2px(c, c, scale)
        x2,y2 = _m2px(room.width - c, room.height - c, scale)
        cv2.rectangle(canvas, (ox+x1, oy+y1), (ox+x2, oy+y2), (180,180,180), thickness=1, lineType=cv2.LINE_AA)

    # 颜色循环
    palette = [(70,130,180), (60,180,75), (255,140,0), (147,112,219), (220,20,60), (0,191,255), (34,139,34)]

    # 逐件家具
    for idx, f in enumerate(items):
        color = palette[idx % len(palette)]
        # 膨胀（margin）矩形（淡色线显示净距带）
        if show_margin and f.margin > 1e-9:
            r_infl = rect_of_furniture(f, f.pose, inflate=f.margin)
            x1,y1 = _m2px(r_infl[0], r_infl[1], scale)
            x2,y2 = _m2px(r_infl[2], r_infl[3], scale)
            cv2.rectangle(canvas, (ox+x1, oy+y1), (ox+x2, oy+y2), (200,200,200), thickness=1, lineType=cv2.LINE_AA)

        # 实体矩形
        r = rect_of_furniture(f, f.pose, inflate=0.0)
        x1,y1 = _m2px(r[0], r[1], scale)
        x2,y2 = _m2px(r[2], r[3], scale)
        cv2.rectangle(canvas, (ox+x1, oy+y1), (ox+x2, oy+y2), color, thickness=2, lineType=cv2.LINE_AA)
        # 填充一点透明效果（用淡色填充体现可视化）
        cv2.rectangle(canvas, (ox+x1+1, oy+y1+1), (ox+x2-1, oy+y2-1), tuple(int(c*0.6) for c in color), thickness=cv2.FILLED)

        # 标签
        label = f"{f.id} ({f.pose.theta}°)"
        cv2.putText(canvas, label, (ox+x1+4, oy+y1+18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30,30,30), 1, cv2.LINE_AA)

    # 标题
    if title:
        cv2.putText(canvas, title, (ox, oy-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10,10,10), 2, cv2.LINE_AA)
    draw_overlaps_overlay(canvas, items, room, scale, ox, oy)
    cv2.imwrite(path, canvas)

def draw_overlaps_overlay(img, items, room, scale, ox=50, oy=50):
    # 画“膨胀后的矩形”之间的交集（红色半透明），用于真碰撞定位
    rects = {f.id: rect_of_furniture(f, f.pose, inflate=f.margin) for f in items}
    ids = list(rects.keys())
    H, W = img.shape[:2]
    overlay = img.copy()
    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            ri, rj = rects[ids[i]], rects[ids[j]]
            inter = rect_intersection(ri, rj)
            x1,y1,x2,y2 = inter
            if x2 > x1 and y2 > y1:
                p1 = (ox + int(round(x1*scale)), oy + int(round(y1*scale)))
                p2 = (ox + int(round(x2*scale)), oy + int(round(y2*scale)))
                cv2.rectangle(overlay, p1, p2, (0,0,255), thickness=cv2.FILLED)
    # 半透明叠加
    cv2.addWeighted(overlay, 0.35, img, 0.65, 0, img)

from typing import Tuple

# 统一矩形类型 (x_min, y_min, x_max, y_max)
Rect = Tuple[float, float, float, float]
def rect_intersection(a: Rect, b: Rect) -> Rect:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    x1 = max(ax1, bx1)
    y1 = max(ay1, by1)
    x2 = min(ax2, bx2)
    y2 = min(ay2, by2)
    return (x1, y1, x2, y2)


def test_render_init_and_final():
    """
    1) 渲染初始布局到 out_init.png
    2) 运行 solve_MVT（无回溯）直到无越界/无重叠
    3) 渲染最终布局到 out_final.png
    """
    room = Room(width=4.0, height=3.0, wall_clearance=0.05)

    # 初始姿态（可随意制造一些重叠/越界以测试）
    bed   = Furniture(id="bed",   w=2.0, h=1.6, margin=0.06, pose=Pose(0.4, 0.4, 0))
    desk  = Furniture(id="desk",  w=1.2, h=0.6, margin=0.04, pose=Pose(1.1, 0.7, 0))
    sofa  = Furniture(id="sofa",  w=1.6, h=0.8, margin=0.05, pose=Pose(1.0, 1.0, 0))

    items = [bed, desk, sofa]

    # 初始图
    render_scene_png("out_init.png", room, items, title="Initial Layout", scale=220, show_margin=True)

    # 求解（只做不越界/不重叠）
    res = solve_MVT(room, items, Options(step=0.02, max_steps=600))
    print("solver_MVT:", res["ok"], res["reason"], "steps:", res["steps"])

    # 最终图
    render_scene_png("out_final.png", room, items, title="Final (no overlap & inside)", scale=220, show_margin=True)

if __name__ == "__main__":
    test_render_init_and_final()
