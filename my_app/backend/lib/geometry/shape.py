from __future__ import annotations
from dataclasses import dataclass
from abc import ABC
from dataclasses import field
import math 


# ==========================================================
# 1. 抽象 Shape 基类
# ==========================================================
@dataclass
class Shape(ABC):
    """纯几何形状（无位置信息）"""
    pass


# ==========================================================
# 2. 具体 Shape：Rectangle
# ==========================================================
@dataclass
class Rectangle(Shape):
    width: float
    height: float


# ==========================================================
# 3. PlacedShape —— 给任意 Shape 添加位置 + 旋转 + 缩放
# ==========================================================

@dataclass
class Transform:
    x: float = 0.0    # center x
    y: float = 0.0    # center y
    r: float = 0.0    # rotation degree
    sx: float = 1.0   # scale x
    sy: float = 1.0   # scale y
    
    def local_to_world(self, lx: float, ly: float) -> tuple[float, float]:
        """
        把局部坐标 (lx, ly) 转换为父坐标 / 世界坐标
        """
        # 1. scale
        lx *= self.sx
        ly *= self.sy

        # 2. rotate
        theta = math.radians(self.r)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        rx = lx * cos_t - ly * sin_t
        ry = lx * sin_t + ly * cos_t

        # 3. translate
        wx = rx + self.x
        wy = ry + self.y

        return wx, wy

@dataclass
class PlacedShape:
    shape: Shape      # 组合，而不是继承
    transform: Transform = field(default_factory=Transform)


# ==========================================================
# 4. PlacedRectangle —— 特化版：shape 一定是 Rectangle
# ==========================================================
@dataclass
class PlacedRectangle(PlacedShape):
    shape: Rectangle  # 在子类限制类型（是合法的）

    @staticmethod
    def from_center(
        cx: float,
        cy: float,
        width: float,
        height: float,
        rotation: float = 0.0
    ) -> "PlacedRectangle":
        """构造一个放置好的 Rectangle（以中心为基准）"""
        return PlacedRectangle(
            shape=Rectangle(width=width, height=height),
            x=cx,
            y=cy,
            r=rotation,
            sx=1.0,
            sy=1.0,
        )
