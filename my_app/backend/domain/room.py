from dataclasses import dataclass,field
from my_app.core.geometry.shape import Rectangle
from my_app.core.geometry.coorinateSystem import Transform
from enum import Enum
from typing import List, Tuple

import cv2
import numpy as np

from my_app.backend.domain.door import Door
from my_app.backend.domain.furniture import Furniture, FurnitureLibrary, FurnitureSpec, FurnitureType, furniture_lib


@dataclass
class Room:
    shape: Rectangle
    name: str
    door: Door=field(default_factory=Door)
    transform: Transform = field(default_factory=Transform)
    def world_corners(self) -> list[tuple[float, float]]:
        """
        返回房间旋转后的四个世界坐标角点（顺序适用于 cv.fillPoly）：
        顺序：左上 → 右上 → 右下 → 左下（逆时针）
        """

        vects = self.shape.get_polygon_points()


        # 转换到世界坐标
        return [
            self.transform.local_to_world(x, y)
            for (x, y) in vects
        ]


def create_room(
    name: str,
    room_width: float,
    room_depth: float,
    door: Door | None = None,
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


    if door is None:
        door = Door(
            offset=(0.2),#200mm from left wall
            wallID=0,
            width=0.9)
   
    return Room(
        shape=room_shape,
        name=name,
        door=door,
    )


room_example_a = create_room(
    "Room A",
    3.5,
    3.0,
)

room_example_b = create_room(
    "Room B",
    6.0,
    5.0,
)


