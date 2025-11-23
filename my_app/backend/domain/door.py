from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple

from my_app.backend.core.geometry.shape import Line

WallID = int 
@dataclass
class Door:
    """
    Simple doorway description placed on a room boundary.
    position: world-space center of the doorway.
    width: opening width measured along the wall.
    """
    offset: float = 0.0
    wallID: WallID = 2
    width: float = 0.9
    name: str | None = None
    shape:Line = field(init=False)

    