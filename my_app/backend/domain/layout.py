from dataclasses import dataclass
from enum import Enum

import numpy as np
import cv2 as cv

from my_app.core.geometry.pixelCoorinateSystem import PixelCoordinateSystem
from my_app.backend.lib.view.cv_canvas import CVViewport as CVCanvas
from my_app.backend.domain.room import Room, room_example_a, room_example_b
from my_app.backend.domain.furniture import (
    FurnitureType,
    FurnitureSpec,
    Furniture,
    furniture_example_bed,
    furniture_example_table,
    furniture_example_wardrobe,
    furniture_example_desk_round,
    furniture_lib,
)
from my_app.core.geometry.shape import  Rectangle
from my_app.core.geometry.coorinateSystem import Transform
# from my_app.backend.planner_core_simplified.model_simplified import Layout  # 暂时不用就先注释掉，免得 lint 报 unused


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
    layout_method: LayoutMethod


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
            return RoomLayout(room=room, furnitures=furnitures, layout_method=method)

        case LayoutMethod.RANDOM:
            # TODO: 在这里实现随机布局逻辑
            return RoomLayout(room=room, furnitures=furnitures, layout_method=method)

        case LayoutMethod.CSP:
            # TODO: 在这里调用 CSP solver 生成新的家具 transform
            return RoomLayout(room=room, furnitures=furnitures, layout_method=method)

        case _:
            # unknown method，先退回 MANUAL
            return RoomLayout(room=room, furnitures=furnitures, layout_method=LayoutMethod.MANUAL)


# 如你以后真的需要基于 Layout(求解结果) 的二次封装，可以在这两个函数里实现：
def create_room_layout_MANUAL(room: Room, layout_model) -> RoomLayout:
    raise NotImplementedError("MANUAL 布局基于 layout_model 的版本还没实现")


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
   
    corner_world_room = room.world_corners()
    img = canvas.draw_polygon(corner_world_room, color=(200, 200, 200))
    img = canvas.draw_text(
        f"Room: {room.name}",
        position_world=(room_left + 0.2, room_top + 0.2),
      )
       

    # 家具
    for furn in layout.furnitures:
        # 这里假设：Furniture.spec.type 对应的 spec.size 是 Rectangle 
        corner_world = furn.world_corners()   

        color = (0, 0, 255)  # 红色
        if( furn.spec.type == FurnitureType.BED_DOUBLE ):
            color = (255, 0, 0)  # 蓝色
        if( furn.spec.type == FurnitureType.WARDROBE_2D ):
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


    layout = create_room_layout(
        room,
        furniture_list,
        method=LayoutMethod.MANUAL,
    )

    img = draw_layout(layout, canvas)
   
