"""Utility builders for default Room instances used when no upload is provided."""

from __future__ import annotations

import math
import random
from typing import Callable, List

import silp
from silp.domain.furniture import Furniture
from silp.domain.room import Room
from silp.core.geometry.shape import Arc, Line



# def _sample_room_with_arc() -> Room:
#     points = [
#         [0.0, 0.0],
#         [4.0, 0.0],
#         [6.0, 2.0],
#         [6.0, 5.0],
#         [0.0, 5.0],
#         [4.0, 2.0],
#     ]
#     outline = [
#         Line(0, 1),
#         Arc( radius=2.0, start_angle=-math.pi / 2, end_angle=0.0),
#         Line(2, 3),
#         Line(3, 4),
#         Line(4, 0),
#     ]
#     room = Room(points, outline)
#     room.extend_furnitures(_show_room_furniture())
#     return room


# def _show_room_furniture() -> List[Furniture]:
#     bed = Furniture.bed("Bed")
#     bed.x = 1.6
#     bed.y = 3.6

#     wardrobe = Furniture.wardrobe("Wardrobe")
#     wardrobe.anchor = "bottom-left"
#     wardrobe.x = 0.3
#     wardrobe.y = 4.2

#     sofa = Furniture.sofa("Sofa")
#     sofa.x = 4.6
#     sofa.y = 1.6
#     sofa.rotation = -90.0

#     coffee_table = Furniture(
#         name="CoffeeTable",
#         type="table",
#         width=1.0,
#         length=0.6,
#         height=0.45,
#         x=3.9,
#         y=2.2,
#         rotation=0.0,
#     )

#     return [bed, wardrobe, sofa, coffee_table]


# def _sample_rect_room() -> Room:
#     points = [
#         [0.0, 0.0],
#         [5.0, 0.0],
#         [5.0, 4.0],
#         [0.0, 4.0],
#     ]
#     outline = [
#         Line(0, 1),
#         Line(1, 2),
#         Line(2, 3),
#         Line(3, 0),
#     ]
#     room = Room(points, outline)

#     desk = Furniture(
#         name="Desk",
#         type="desk",
#         width=1.4,
#         length=0.7,
#         height=0.75,
#         x=1.0,
#         y=1.0,
#     )
#     chair = Furniture(
#         name="Chair",
#         type="chair",
#         width=0.6,
#         length=0.6,
#         height=1.0,
#         x=1.0,
#         y=0.2,
#     )
#     shelf = Furniture(
#         name="Shelf",
#         type="shelf",
#         width=0.4,
#         length=2.0,
#         height=2.0,
#         x=4.5,
#         y=1.0,
#         rotation=90.0,
#         anchor="bottom-left",
#     )
#     room.extend_furnitures([desk, chair, shelf])
#     return room


DEFAULT_ROOM_BUILDERS: List[Callable[[], Room]] = [
 
]


def random_room() -> Room:
    """Return a freshly constructed default room."""
    builder = random.choice(DEFAULT_ROOM_BUILDERS)
    return builder()


DEFAULT_ROOMS = [builder() for builder in DEFAULT_ROOM_BUILDERS]

