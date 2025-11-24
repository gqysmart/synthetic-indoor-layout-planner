from dataclasses import dataclass,field
from silp.core.geometry.shape import Line, Rectangle,Shape
from silp.core.geometry.coorinate_system import Transform
from enum import Enum
from typing import List, Tuple
from silp.core.geometry.placed_entity import PlacedEntity

import cv2
import numpy as np

from silp.domain.door import Door
from silp.domain.furniture import Furniture, FurnitureLibrary, FurnitureSpec, FurnitureType, furniture_lib


@dataclass
class Room(PlacedEntity):
    name: str
    door: Door=field(default_factory=Door)
    
    @property
    def door_shape(self) -> Shape:
        edge = self.shape.get_edge(self.door.wallID)
        start_pt = edge.point_at_distance(self.door.offset)
        end_pt = edge.point_at_distance(self.door.offset + self.door.width)
        return Line(start=start_pt, end=end_pt)
       
    @classmethod
    def create_rec_room(
        cls,
        name: str,
        room_width: float,
        room_depth: float,
        door: Door | None = None,
    ) -> "Room":
   
        room_shape = Rectangle(
            width=room_width,
            height=room_depth,
        
        )

        if door is None:
            door = Door(
                
                offset=(0.2),#200mm from left wall
                wallID=0,
                width=0.9)
    
        return cls(
            shape_ref = room_shape,
            name=name,
            door=door,
        )

    
room_example_a = Room.create_rec_room(
    "Room A",
    3.6,
    3.3,
)

room_example_b = Room.create_rec_room(
    "Room B",
    6.0,
    5.0,
)

