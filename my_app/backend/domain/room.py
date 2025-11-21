from dataclasses import dataclass,field
from my_app.backend.lib.geometry.shape import Rectangle, Transform
from enum import Enum
from typing import List, Tuple

import cv2
import numpy as np

from my_app.backend.domain.door import Door
from my_app.backend.domain.furniture import Furniture, FurnitureLibrary, FurnitureSpec, FurnitureType, furniture_lib
from my_app.backend.lib.geometry.shape import PlacedRectangle, Rectangle


@dataclass
class Room:
    shape: Rectangle
    name: str
    doors: list[Door]=None
    transform: Transform = field(default_factory=Transform)
    def world_corners(self) -> list[tuple[float, float]]:
        """
        返回房间旋转后的四个世界坐标角点（顺序适用于 cv.fillPoly）：
        顺序：左上 → 右上 → 右下 → 左下（逆时针）
        """

        rw = self.shape.width
        rd = self.shape.height   # 或 height，看你的字段名

        # 房间本地坐标下的四个角
        # （⚠️ y 轴向下为正，与 OpenCV 坐标系一致）
        local_corners = [
            (-rw / 2.0, -rd / 2.0),   # 左上
            ( rw / 2.0, -rd / 2.0),   # 右上
            ( rw / 2.0,  rd / 2.0),   # 右下
            (-rw / 2.0,  rd / 2.0),   # 左下
        ]

        # 转换到世界坐标
        return [
            self.transform.local_to_world(x, y)
            for (x, y) in local_corners
        ]


def create_room(
    name: str,
    room_width: float,
    room_depth: float,
    doors: List[Door] | None = None,
) -> Room:
    """
    furniture_items 示例:
    [
        {"id": "bed_01", "type": "bed_double",},
        {"id": "desk_01", "type": "desk_std" },
    ]
    """

   
    room_shape = Rectangle(
        width=room_width,
        height=room_depth,
       
    )


    if doors is None:
        doors = []

    return Room(
        shape=room_shape,
        name=name,
        doors=doors,
    )


room_example_a = create_room(
    "Room A",
    5.0,
    4.0,
)

room_example_b = create_room(
    "Room B",
    6.0,
    5.0,
)



def show_rooms(room_a: Room, room_b: Room):
    img_a = draw_room(room_a, pixels_per_meter=100)
    img_b = draw_room(room_b, pixels_per_meter=100)

    cv2.imshow("Room A", img_a)
    cv2.imshow("Room B", img_b)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    show_rooms(room_example_a, room_example_b)
