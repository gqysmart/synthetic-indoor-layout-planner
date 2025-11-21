from dataclasses import dataclass
from typing import Tuple


@dataclass
class Door:
    """
    Simple doorway description placed on a room boundary.
    position: world-space center of the doorway.
    width: opening width measured along the wall.
    """
    position: Tuple[float, float]
    width: float
    name: str | None = None
