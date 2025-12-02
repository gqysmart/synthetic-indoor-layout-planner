from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Union
import math
from silp.core.geometry.coorinate_system import Transform

Point = tuple[float, float]

# ==========================================================
# 1. Abstract Shape base class
# ==========================================================
@dataclass
class Shape(ABC):
    _vertices_buffer: list[Point] = field(default= None, init=False)
    # tuple example: (x, y, "L") , (x,y,"A") , L for line, A for arc
    # If we later want to store L/A types, create a structure; for now vertices are plain points.

    def is_refined(self) -> bool:
        return self._vertices_buffer is not None and len(self._vertices_buffer) > 0

    @abstractmethod
    def refine(self) -> None:
        pass

    def get_polygon_points(self) -> list[Point]:
        """
        Return the polygon vertex list, suitable for cv.fillPoly and similar.
        Refine first if the Shape is not yet refined.
        """
        if not self.is_refined():
            self.refine()
        return self._vertices_buffer


   

# ==========================================================
# 3. Concrete Shape: Line
# ==========================================================
@dataclass
class Line(Shape):
    start: Point
    end: Point

    def __post_init__(self):
        self.refine()

    def refine(self) -> None:
        """
        Refine the line into a segment sequence (two endpoints).
        """
        self._vertices_buffer = [self.start, self.end]

    def point_at_distance(self, distance: float) -> Point:
        """
        Return the point located at the given distance from the start.
        """
        x0, y0 = self.start
        x1, y1 = self.end
        line_length = math.hypot(x1 - x0, y1 - y0)
        if line_length == 0:
            return self.start  # Start and end coincide

        ratio = distance / line_length
        ratio = max(0.0, min(1.0, ratio))  # Clamp to [0, 1]

        x = x0 + ratio * (x1 - x0)
        y = y0 + ratio * (y1 - y0)
        return (x, y)


# ==========================================================
# 4. Concrete Shape: Arc (centered at origin)
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
        Refine the arc into a sequence of line segments.
        Center is at (0, 0) and angles are in degrees.
        """
        self._vertices_buffer = []

        start_rad = math.radians(self.start_angle)
        end_rad   = math.radians(self.end_angle)
        total_angle = end_rad - start_rad

        n = max(1, self.num_segments)
        angle_step = total_angle / n

        for i in range(n + 1):
            angle = start_rad + i * angle_step
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            self._vertices_buffer.append((x, y))

    def point_at_distance(self, distance: float) -> Point:
        """
        Return the point located at the given distance along the arc from the start angle.
        """
        arc_length = abs(math.radians(self.end_angle - self.start_angle)) * self.radius
        if arc_length == 0:
            angle = math.radians(self.start_angle)
        else:
            ratio = distance / arc_length
            ratio = max(0.0, min(1.0, ratio))  # Clamp to [0, 1]
            angle = math.radians(self.start_angle) + ratio * (math.radians(self.end_angle) - math.radians(self.start_angle))

        x = self.radius * math.cos(angle)
        y = self.radius * math.sin(angle)
        return (x, y)


BasicShape = Union[Line, Arc]


# ==========================================================
# 5. Composite Shape: Curve
# ==========================================================

def _points_equal(a: Point, b: Point, eps: float = 1e-9) -> bool:
    return math.isclose(a[0], b[0], abs_tol=eps) and math.isclose(a[1], b[1], abs_tol=eps)

@dataclass(kw_only=True)
class Curve(Shape):
    shapes: list[BasicShape] = field(default_factory=list)

    def refine(self) -> None:
        """
        Refine a polyline/curve into a vertex sequence by concatenating
        vertices from each shape in order, while:
        - avoiding duplicate joints between consecutive segments
        - avoiding an explicit closing vertex equal to the first one
          (fillPoly / polygon logic会自动闭合)
        """
        self._vertices_buffer = []

        for i, shape in enumerate(self.shapes):
            if not shape.is_refined():
                shape.refine()

            verts = shape._vertices_buffer
            if not verts:
                continue

            if i == 0:
                # 第一段：全部顶点都保留
                self._vertices_buffer.extend(verts)
            else:
                # 后续段：如果本段首点 == 当前末点，就跳过首点
                start_idx = 0
                if self._vertices_buffer and _points_equal(verts[0], self._vertices_buffer[-1]):
                    start_idx = 1
                self._vertices_buffer.extend(verts[start_idx:])

        # 如果最后一个点和第一个点相同，就删除最后一个，避免显式闭环点
        if len(self._vertices_buffer) > 1 and _points_equal(self._vertices_buffer[0], self._vertices_buffer[-1]):
            self._vertices_buffer.pop()

    def get_edge(self, index: int) -> BasicShape:
        return self.shapes[index]


# ==========================================================
# 2. Concrete Shape: Rectangle
# ==========================================================
@dataclass
class Rectangle(Curve):
    width: float
    height: float

    EDGE_TOP    = 0
    EDGE_RIGHT  = 1
    EDGE_BOTTOM = 2
    EDGE_LEFT   = 3

    def __post_init__(self):
        """
        Local coordinate system uses the rectangle center as the origin.
        Edge order:
          0: top
          1: right
          2: bottom
          3: left
        Future doors can bind to an edge using this index.
        """
        hw = self.width / 2.0
        hh = self.height / 2.0

        self.shapes = [
            # Top: top-left → top-right
            Line(start=(-hw, -hh), end=( hw, -hh)),
            # Right: top-right → bottom-right
            Line(start=( hw, -hh), end=( hw,  hh)),
            # Bottom: bottom-right → bottom-left
            Line(start=( hw,  hh), end=(-hw,  hh)),
            # Left: bottom-left → top-left
            Line(start=(-hw,  hh), end=(-hw, -hh)),
        ]
