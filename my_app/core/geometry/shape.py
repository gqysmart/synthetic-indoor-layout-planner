from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Union
import math

Point = tuple[float, float]

# ==========================================================
# 1. 抽象 Shape 基类
# ==========================================================
@dataclass
class Shape(ABC):
    vertices: list[Point] = field(default_factory=list, init=False)
    # tuple example: (x, y, "L") , (x,y,"A") , L for line, A for arc
    # （如果以后真要存 L/A 类型，可以单独做一个结构；现在 vertices 是纯点）

    def is_refined(self) -> bool:
        return len(self.vertices) > 0

    @abstractmethod
    def refine(self) -> None:
        pass

    def get_polygon_points(self) -> list[Point]:
        """
        返回多边形顶点列表，适用于 cv.fillPoly 等函数。
        如果 Shape 未细化，则先进行细化。
        """
        if not self.is_refined():
            self.refine()
        return self.vertices


# ==========================================================
# 2. 具体 Shape：Rectangle
# ==========================================================
@dataclass
class Rectangle(Shape):
    width: float
    height: float

    def __post_init__(self):
        self.refine()

    def refine(self) -> None:
        """
        细化矩形为四个顶点（顺时针），局部坐标以中心为原点。
        """
        hw = self.width / 2.0
        hh = self.height / 2.0
        self.vertices = [
            (-hw, -hh),  # 左上
            ( hw, -hh),  # 右上
            ( hw,  hh),  # 右下
            (-hw,  hh),  # 左下
        ]


# ==========================================================
# 3. 具体 Shape：Line
# ==========================================================
@dataclass
class Line(Shape):
    start: Point
    end: Point

    def __post_init__(self):
        self.refine()

    def refine(self) -> None:
        """
        细化直线为线段序列（两个端点）。
        """
        self.vertices = [self.start, self.end]


# ==========================================================
# 4. 具体 Shape：Arc（以原点为圆心）
# ==========================================================
@dataclass
class Arc(Shape):
    radius: float
    num_segments: int = 36
    start_angle: float = 0.0  # in degrees
    end_angle: float = 360.0  # in degrees

    def __post_init__(self):
        self.refine()

    def refine(self) -> None:
        """
        细化圆弧为线段序列。
        圆心在 (0, 0)，角度单位为度。
        """
        self.vertices = []

        start_rad = math.radians(self.start_angle)
        end_rad   = math.radians(self.end_angle)
        total_angle = end_rad - start_rad

        n = max(1, self.num_segments)
        angle_step = total_angle / n

        for i in range(n + 1):
            angle = start_rad + i * angle_step
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            self.vertices.append((x, y))


BasicShape = Union[Line, Arc]


# ==========================================================
# 5. 组合 Shape：Curve
# ==========================================================
@dataclass
class Curve(Shape):
    shapes: list[BasicShape] = field(default_factory=list)

    def refine(self) -> None:
        """
        细化折线/曲线为顶点序列：按顺序拼接内部每个 shape 的顶点。
        """
        self.vertices = []
        for shape in self.shapes:
            if not shape.is_refined():
                shape.refine()
            self.vertices.extend(shape.vertices)

