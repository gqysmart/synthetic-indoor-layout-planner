from dataclasses import dataclass
from typing import Tuple

WallID = int 
@dataclass
class Door:
    """
    Simple doorway description placed on a room boundary.
    position: world-space center of the doorway.
    width: opening width measured along the wall.
    """
    offset: float = 0.0
    wallID: WallID = 0
    width: float = 0.9
    name: str | None = None
