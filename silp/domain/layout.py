from dataclasses import dataclass
from enum import Enum

import numpy as np
import cv2 as cv

from silp.core.geometry.coorinate_system import PixelCoordinateSystem,Transform
from silp.core.geometry.shape import Rectangle
from silp.lib.view.cv_canvas import CVViewport as CVCanvas
from silp.domain.room import Room, room_example_a, room_example_b
from silp.domain.furniture import (
    FurnitureType,
    FurnitureSpec,
    Furniture,
    furniture_example_bed,
    furniture_example_table,
    furniture_example_wardrobe,
    furniture_example_desk_round,
    furniture_lib,
)

# from silp.services.planner_core_simplified.model_simplified import Layout  # 暂时不用就先注释掉，免得 lint 报 unused


# -----------------------
# 数据结构
# -----------------------

class LayoutMethod(Enum):
    RANDOM = "RANDOM"
    CSP = "CSP"
    MANUAL = "MANUAL"


@dataclass
class RoomLayout:
    room: Room
    furnitures: list[Furniture]


# -----------------------
# 创建布局
# -----------------------

def create_room_layout(
    room: Room,
    furnitures: list[Furniture],
    method: LayoutMethod = LayoutMethod.MANUAL,
) -> RoomLayout:
    """
    现在先做一个最简单版本：
    - MANUAL: 直接使用传入的 furnitures（里面已经有 transform）
    - 其他方法以后再实现
    """
    match method:
        case LayoutMethod.MANUAL:
            # 手动：直接用现成的家具
            return RoomLayout(room=room, furnitures=furnitures)

        case LayoutMethod.RANDOM:
            # TODO: 在这里实现随机布局逻辑
            return RoomLayout(room=room, furnitures=furnitures)

        case LayoutMethod.CSP:
            # TODO: 在这里调用 CSP solver 生成新的家具 transform
            return RoomLayout(room=room, furnitures=furnitures)

        case _:
            # unknown method，先退回 MANUAL
            return RoomLayout(room=room, furnitures=furnitures)


# 如你以后真的需要基于 Layout(求解结果) 的二次封装，可以在这两个函数里实现：
def create_room_layout_MANUAL(room: Room, furnitures: list[Furniture]) -> RoomLayout:
    return RoomLayout(room=room, furnitures=furnitures)
    


def create_room_layout_RANDOM(room: Room, layout_model) -> RoomLayout:
    raise NotImplementedError("RANDOM 布局基于 layout_model 的版本还没实现")


# -----------------------
# 绘制布局
# -----------------------
def _draw_room(room: Room, canvas: CVCanvas) -> np.ndarray:
    """
    把一个 Room 画成一张 OpenCV 图像（BGR）
    假定房间是 axis-aligned 的矩形（暂时忽略旋转 r）
    """

    room_vects = room.shape.get_polygon_points()      # 假设 Room.shape 是 Rectangle(width, height)

  
   

    # 使用 room 本地坐标系，原点在房间中心
    corner_world_room = room.world_corners()
    img = canvas.draw_polygon(corner_world_room, color=(200, 200, 200))
    img = canvas.draw_text(
        f"Room: {room.name}",
        position_world=(room_left + 0.2, room_top + 0.2),
      )
    return img


def draw_layout(layout: RoomLayout, canvas: CVCanvas) -> np.ndarray:
    """
    把一个 RoomLayout 画成一张 OpenCV 图像（BGR）
    假定房间和家具都是 axis-aligned 的矩形（暂时忽略旋转 r）
    """

    room = layout.room
   

    # 使用 room 本地坐标系，原点在房间中心
   
    corner_world_room = room.world_polygon()
    img = canvas.draw_polygon(corner_world_room, color=(200, 200, 200))
    img = canvas.draw_text(
        f"Room: {room.name}",
        position_world=(room_left + 0.2, room_top + 0.2),
      )
       

    # 家具
    for furn in layout.furnitures:
        # 这里假设：Furniture.spec.type 对应的 spec.size 是 Rectangle 
        corner_world = furn.world_polygon()   

        color = (0, 0, 255)  # 红色
        if( furn.type == FurnitureType.BED_DOUBLE ):
            color = (255, 0, 0)  # 蓝色
        if( furn.type == FurnitureType.WARDROBE_2D ):
            color = (0, 255, 0)  # 绿色 

        #cv.rectangle(img, tl_f, br_f, color, thickness=-1)  # 实心红色
        img =canvas.draw_polygon(corner_world, color=color)
        # 标注家具 ID
        #     img,
        #     furn.id,
        #     label_pos,
        #     cv.FONT_HERSHEY_SIMPLEX,
        #     0.4,
        #     (255, 255, 255),
        #     1,
        #     cv.LINE_AA,
        # )

    # 门口
    # for door in room.doors:
    #     dx, dy = door.position
    #     door_w = door.width

    #     dist_left = abs(dx - room_left)
    #     dist_right = abs(dx - room_right)
    #     dist_top = abs(dy - room_top)
    #     dist_bottom = abs(dy - room_bottom)

    #     nearest = min(
    #         [("left", dist_left), ("right", dist_right), ("top", dist_top), ("bottom", dist_bottom)],
    #         key=lambda item: item[1],
    #     )[0]

    #     half_w = door_w / 2.0
    #     if nearest in ("left", "right"):
    #         wall_x = room_left if nearest == "left" else room_right
    #         p1 = world_to_pixel(wall_x, dy - half_w)
    #         p2 = world_to_pixel(wall_x, dy + half_w)
    #     else:
    #         wall_y = room_top if nearest == "top" else room_bottom
    #         p1 = world_to_pixel(dx - half_w, wall_y)
    #         p2 = world_to_pixel(dx + half_w, wall_y)

    #     cv.line(img, p1, p2, (0, 128, 0), thickness=4)
    canvas.show("Debug Canvas")
    return img


room_a = room_example_a
furniture_list_1 = [
    furniture_example_bed.clone_to("bed_01_room_a", Transform(x=-0.8, y=-0.9, r=0)),
    furniture_example_table.clone_to("table_01_room_a", Transform(x=1.4, y=-1.05, r=90)),
    furniture_example_wardrobe.clone_to("wardrobe_01_room_a", Transform(x=-0.9, y=1.35, r=0)),
    furniture_example_desk_round.clone_to("desk_round_01_room_a", Transform(x=0, y=0, r=90)),
]

layout_example_a = create_room_layout_MANUAL(
    room=room_a,
    furnitures=furniture_list_1,
)


room_b = room_example_b
furniture_list_2 = [
    furniture_example_bed.clone_to("bed_01_room_b", Transform(x=-0.8, y=-0.9, r=0)),
    furniture_example_table.clone_to("table_01_room_b", Transform(x=1.4, y=-1.05, r=90)),
    furniture_example_wardrobe.clone_to("wardrobe_01_room_b", Transform(x=-0.9, y=1.35, r=0)),
    furniture_example_desk_round.clone_to("desk_round_01_room_b", Transform(x=0, y=0, r=90)),
]

layout_example_b = create_room_layout_MANUAL(
    room=room_a,
    furnitures=furniture_list_1,
)

# -----------------------
# main：测试绘制 Room A 的手动布局
# -----------------------

if __name__ == "__main__":
    room = room_example_a
    furniture_list = [
        furniture_example_bed,
        furniture_example_table,
        furniture_example_wardrobe,
        furniture_example_desk_round,
    ]

    rect: Rectangle = room.shape      # 假设 Room.shape 是 Rectangle(width, height)
    room_w = rect.width
    room_h = rect.height

    room_left = 0.0 - room_w / 2.0
    room_right = 0.0 + room_w / 2.0
    room_top = 0.0 - room_h / 2.0
    room_bottom = 0.0 + room_h / 2.0

    pixels_per_meter = 100
    pcs = PixelCoordinateSystem(
        pixels_per_meter=pixels_per_meter,
        canvas_size=(int(np.ceil(room_w * pixels_per_meter))+40, int(np.ceil(room_h * pixels_per_meter))+40),
        center_world=(0.0, 0.0),
    )

    canvas = CVCanvas(
        pcs=pcs,
        background_color=(240, 240, 240),
    )

    img = draw_layout(layout_example_a, canvas)
