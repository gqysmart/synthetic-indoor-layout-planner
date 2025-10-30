from dataclasses import dataclass, field
from typing import Optional

try:
    from typing import Literal  # type: ignore
except ImportError:  # pragma: no cover - fallback for older Python versions
    from typing_extensions import Literal  # type: ignore
import random
import string

def random_suffix(length=4):
    """生成随机后缀"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@dataclass
class Furnish:
    name: str
    type: str
    width: float
    length: float
    height: float
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0  # 朝向（度）
    anchor: Literal["center", "bottom-left", "top-left"] = "center"

    def get_corners(self):
        """根据 anchor 和旋转计算四个角坐标"""
        import math
        w, l = self.width, self.length
        cx, cy = self.x, self.y

        # 以中心为 anchor
        if self.anchor == "center":
            half_w, half_l = w / 2, l / 2
            corners = [
                (cx - half_w, cy - half_l),
                (cx + half_w, cy - half_l),
                (cx + half_w, cy + half_l),
                (cx - half_w, cy + half_l)
            ]
        elif self.anchor == "bottom-left":
            corners = [
                (cx, cy),
                (cx + w, cy),
                (cx + w, cy + l),
                (cx, cy + l)
            ]
        else:
            raise ValueError(f"Unknown anchor type: {self.anchor}")

        # 旋转
        theta = math.radians(self.rotation)
        rotated = [
            (
                cx + (x - cx) * math.cos(theta) - (y - cy) * math.sin(theta),
                cy + (x - cx) * math.sin(theta) + (y - cy) * math.cos(theta)
            )
            for x, y in corners
        ]
        return rotated

    def __post_init__(self) -> None:
        for attr in ("width", "length", "height"):
            value = getattr(self, attr)
            if value <= 0:
                raise ValueError(f"{attr} must be positive, got {value}")

    def footprint(self) -> float:
        """Return the amount of floor space occupied by the furniture."""
        return self.width * self.length

    def volume(self) -> float:
        """Return the volumetric space used by the furniture."""
        return self.width * self.length * self.height


    @classmethod
    def bed(cls,name: Optional[str] = None):
        return cls(
            name=name or f"Bed-{random_suffix()}",
            type="bed",
            width=1.6,
            length=2.2,
            height=0.6
        )

    @classmethod
    def wardrobe(cls,name: Optional[str] = None):
        return cls(
            name=name or f"Wardrobe-{random_suffix()}",
            type="wardrobe",
            width=1.8,
            length=0.6,
            height=2.0
        )

    @classmethod
    def sofa(cls,name: Optional[str] = None):
        return cls(
            name=name or f"Sofa-{random_suffix()}",
            type="sofa",
            width=2.0,
            length=0.9,
            height=0.8

        )

