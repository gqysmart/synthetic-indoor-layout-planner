import math
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterable, List, Optional, Sequence, Tuple, Union

if TYPE_CHECKING:
    import numpy as np

from .furnishings import Furnish

class Segment:
    def __init__(self):
        pass

    def get_start(self, points):
        raise NotImplementedError

    def get_end(self, points):
        raise NotImplementedError

class Line(Segment):
    def __init__(self, start_idx, end_idx):
        self.start_idx = start_idx
        self.end_idx = end_idx

    def get_start(self, points):
        return points[self.start_idx]

    def get_end(self, points):
        return points[self.end_idx]

class Arc(Segment):
    def __init__(self, start_idx, end_idx, center_idx, radius, start_angle, end_angle):
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.center_idx = center_idx
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def get_start(self, points):
        center = points[self.center_idx]
        return [
            center[0] + self.radius * math.cos(self.start_angle),
            center[1] + self.radius * math.sin(self.start_angle)
        ]

    def get_end(self, points):
        center = points[self.center_idx]
        return [
            center[0] + self.radius * math.cos(self.end_angle),
            center[1] + self.radius * math.sin(self.end_angle)
        ]

class Room:
    def __init__(self, points, outline, furnitures: Optional[Iterable[Furnish]] = None):
        """
        Initialize Room with a list of points and outline as list of Line and Arc segments.
        Segments reference points by indices and must be linked head to tail to form a closed room.

        Args:
        points (list): List of [x, y] coordinates.
        outline (list): List of Line or Arc instances.
        furnitures (Iterable[Furnish], optional): Furnishings that belong to the room.
        """
        self.points = points
        if not outline:
            raise ValueError("Outline cannot be empty")
        if not points:
            raise ValueError("Points cannot be empty")
        for seg in outline:
            if isinstance(seg, Line):
                if seg.start_idx >= len(points) or seg.end_idx >= len(points):
                    raise ValueError("Invalid point index in Line")
            elif isinstance(seg, Arc):
                if seg.start_idx >= len(points) or seg.end_idx >= len(points) or seg.center_idx >= len(points):
                    raise ValueError("Invalid point index in Arc")
            else:
                raise ValueError("Invalid segment type")
        for i in range(len(outline) - 1):
            if not self._almost_equal(outline[i].get_end(points), outline[i+1].get_start(points)):
                raise ValueError(f"Segments {i} and {i+1} are not connected")
        if not self._almost_equal(outline[-1].get_end(points), outline[0].get_start(points)):
            raise ValueError("Outline is not closed")
        self.outline = outline
        self.furnitures: List[Furnish] = list(furnitures) if furnitures is not None else []

    def add_furniture(self, furniture: Furnish) -> None:
        """Append a single piece of furniture to the room."""
        self.furnitures.append(furniture)

    def extend_furnitures(self, furnitures: Iterable[Furnish]) -> None:
        """Append multiple furnishings to the room."""
        self.furnitures.extend(furnitures)

    def _almost_equal(self, p1, p2, tol=1e-6):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1]) < tol

    def describe(self) -> str:
        """Return a human-readable description of the room and its furnitures."""
        lines: List[str] = []
        lines.append("Room Points:")
        for idx, point in enumerate(self.points):
            lines.append(f"  P{idx}: ({point[0]:.2f}, {point[1]:.2f})")

        lines.append("Room Outline Segments:")
        for idx, segment in enumerate(self.outline):
            start = segment.get_start(self.points)
            end = segment.get_end(self.points)
            if isinstance(segment, Line):
                lines.append(f"  {idx}: Line from ({start[0]:.2f}, {start[1]:.2f}) to ({end[0]:.2f}, {end[1]:.2f})")
            elif isinstance(segment, Arc):
                center = self.points[segment.center_idx]
                lines.append(
                    f"  {idx}: Arc center=({center[0]:.2f}, {center[1]:.2f}) radius={segment.radius:.2f} "
                    f"start=({start[0]:.2f}, {start[1]:.2f}) end=({end[0]:.2f}, {end[1]:.2f})"
                )

        lines.append("Furnitures:")
        if not self.furnitures:
            lines.append("  (none)")
            return "\n".join(lines)

        for furn in self.furnitures:
            lines.append(
                "  {name} [{ftype}] size=({w:.2f} x {l:.2f} x {h:.2f}) "
                "position=({x:.2f}, {y:.2f}) rotation={rot:.1f}° anchor={anchor}".format(
                    name=furn.name,
                    ftype=furn.type,
                    w=furn.width,
                    l=furn.length,
                    h=furn.height,
                    x=furn.x,
                    y=furn.y,
                    rot=furn.rotation,
                    anchor=furn.anchor,
                )
            )

        return "\n".join(lines)

    def print_room_and_furnitures(self) -> None:
        """Print room geometry and furnishings using the describe output."""
        print(self.describe())


class CVRender:
    """Utilities for text and OpenCV rendering of a room and its furniture."""

    def __init__(
        self,
        *,
        printer: Callable[[str], None] = print,
        pixels_per_m: float = 120.0,
        margin: int = 40,
        color: Tuple[int, int, int] = (50, 120, 240),
        thickness: int = 3,
        background_color: Tuple[int, int, int] = (255, 255, 255),
        furniture_fill: Tuple[int, int, int] = (200, 220, 200),
        furniture_outline: Tuple[int, int, int] = (60, 120, 80),
        arc_samples_per_circle: int = 64,
    ) -> None:
        self._printer = printer
        self.pixels_per_m = pixels_per_m
        self.margin = margin
        self.color = color
        self.thickness = thickness
        self.background_color = background_color
        self.furniture_fill = furniture_fill
        self.furniture_outline = furniture_outline
        self.arc_samples_per_circle = arc_samples_per_circle

    def print_room(self, room: Room) -> None:
        """Print the room using the configured printer callable."""
        self._printer(room.describe())

    @staticmethod
    def _points_close(a: Tuple[float, float], b: Tuple[float, float], tol: float = 1e-9) -> bool:
        return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol

    def _room_outline_points(self, room: Room, arc_samples_per_circle: int) -> List[Tuple[float, float]]:
        coords: List[Tuple[float, float]] = []
        for segment in room.outline:
            start = tuple(segment.get_start(room.points))
            if not coords or not self._points_close(coords[-1], start):
                coords.append(start)

            if isinstance(segment, Arc):
                sweep = segment.end_angle - segment.start_angle
                if abs(sweep) > 1e-9:
                    steps = max(2, int(math.ceil(abs(sweep) / (2 * math.pi) * arc_samples_per_circle)))
                    center = room.points[segment.center_idx]
                    for idx in range(1, steps):
                        angle = segment.start_angle + sweep * (idx / steps)
                        pt = (
                            center[0] + segment.radius * math.cos(angle),
                            center[1] + segment.radius * math.sin(angle),
                        )
                        coords.append(pt)

            end = tuple(segment.get_end(room.points))
            if not coords or not self._points_close(coords[-1], end):
                coords.append(end)

        if coords and not self._points_close(coords[0], coords[-1]):
            coords.append(coords[0])

        return coords

    @staticmethod
    def _furniture_outline_points(furnish: Furnish) -> List[Tuple[float, float]]:
        corners = list(furnish.get_corners())
        if corners and (
            abs(corners[0][0] - corners[-1][0]) > 1e-9 or abs(corners[0][1] - corners[-1][1]) > 1e-9
        ):
            corners.append(corners[0])
        return [(float(x), float(y)) for x, y in corners]

    @staticmethod
    def _ensure_cv():
        try:
            import cv2
            import numpy as np
        except ImportError as exc:
            raise RuntimeError("OpenCV (cv2) and numpy are required for CV rendering.") from exc
        return cv2, np

    def render(
        self,
        room: Room,
        *,
        furnitures: Optional[Sequence[Furnish]] = None,
        arc_samples_per_circle: Optional[int] = None,
    ) -> "np.ndarray":
        cv2, np = self._ensure_cv()
        sampled_outline = self._room_outline_points(
            room, arc_samples_per_circle if arc_samples_per_circle is not None else self.arc_samples_per_circle
        )
        room_coords = np.array(sampled_outline, dtype=np.float32)
        if room_coords.size == 0:
            return np.full((2 * self.margin, 2 * self.margin, 3), self.background_color, dtype=np.uint8)

        room_coords_px = room_coords * float(self.pixels_per_m)

        furnishings_list: Sequence[Furnish] = furnitures if furnitures is not None else room.furnitures
        furniture_polys_px: List[Tuple[Furnish, "np.ndarray"]] = []
        if furnishings_list:
            for furn in furnishings_list:
                poly = np.array(self._furniture_outline_points(furn), dtype=np.float32)
                if poly.size == 0:
                    continue
                furniture_polys_px.append((furn, poly * float(self.pixels_per_m)))

        all_px_arrays = [room_coords_px] + [poly for _, poly in furniture_polys_px]
        bounds_min = np.vstack([arr.min(axis=0) for arr in all_px_arrays]).min(axis=0)
        bounds_max = np.vstack([arr.max(axis=0) for arr in all_px_arrays]).max(axis=0)

        width = max(1, int(math.ceil(bounds_max[0] - bounds_min[0])) + 2 * self.margin)
        height = max(1, int(math.ceil(bounds_max[1] - bounds_min[1])) + 2 * self.margin)

        def to_canvas(points_px: "np.ndarray") -> "np.ndarray":
            shifted = points_px - bounds_min + self.margin
            shifted[:, 1] = (bounds_max[1] - points_px[:, 1]) + self.margin
            return np.round(shifted).astype(np.int32)

        def to_canvas_point(point_px: "np.ndarray") -> "np.ndarray":
            shifted = point_px - bounds_min + self.margin
            shifted[1] = (bounds_max[1] - point_px[1]) + self.margin
            return np.round(shifted).astype(np.int32)

        canvas = np.full((height, width, 3), self.background_color, dtype=np.uint8)
        room_points_px = to_canvas(room_coords_px).reshape(-1, 1, 2)
        cv2.polylines(
            canvas,
            [room_points_px],
            isClosed=True,
            color=self.color,
            thickness=self.thickness,
            lineType=cv2.LINE_AA,
        )

        for furn, poly_px in furniture_polys_px:
            poly_canvas = to_canvas(poly_px).reshape(-1, 1, 2)
            cv2.fillPoly(canvas, [poly_canvas], color=self.furniture_fill, lineType=cv2.LINE_AA)
            cv2.polylines(
                canvas,
                [poly_canvas],
                isClosed=True,
                color=self.furniture_outline,
                thickness=2,
                lineType=cv2.LINE_AA,
            )
            center_px = np.array([furn.x, furn.y], dtype=np.float32) * float(self.pixels_per_m)
            center_canvas = to_canvas_point(center_px)
            cv2.putText(
                canvas,
                furn.type.capitalize(),
                tuple(center_canvas.astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (40, 40, 40),
                thickness=1,
                lineType=cv2.LINE_AA,
            )

        return canvas

    def save(
        self,
        room: Room,
        output: Union[str, Path],
        *,
        canvas: Optional["np.ndarray"] = None,
        furnitures: Optional[Sequence[Furnish]] = None,
        arc_samples_per_circle: Optional[int] = None,
    ) -> "np.ndarray":
        cv2, _ = self._ensure_cv()
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if canvas is None:
            canvas = self.render(
                room,
                furnitures=furnitures,
                arc_samples_per_circle=arc_samples_per_circle,
            )
        if not cv2.imwrite(str(output_path), canvas):
            raise RuntimeError(f"Failed to write image to {output_path}")
        return canvas

    def show(
        self,
        room: Room,
        *,
        window_name: str = "room",
        wait_ms: int = 0,
        destroy: bool = True,
        canvas: Optional["np.ndarray"] = None,
        furnitures: Optional[Sequence[Furnish]] = None,
        arc_samples_per_circle: Optional[int] = None,
    ) -> "np.ndarray":
        cv2, _ = self._ensure_cv()
        if canvas is None:
            canvas = self.render(
                room,
                furnitures=furnitures,
                arc_samples_per_circle=arc_samples_per_circle,
            )
        cv2.imshow(window_name, canvas)
        cv2.waitKey(wait_ms)
        if destroy:
            cv2.destroyWindow(window_name)
        return canvas

if __name__ == "__main__":
    # Test with a rectangular room
    points = [[0, 0], [4, 0], [4, 3], [0, 3]]
    outlines = [
        Line(0, 1),
        Line(1, 2),
        Line(2, 3),
        Line(3, 0)
    ]
    room = Room(points, outlines)
    print("Room created successfully with rectangular outline.")

    # Test with arc
    points_arc = [[0, 0], [2, 0], [4, 2], [4, 0], [2, 2]]  # 4 is center
    outlines_arc = [
        Line(0, 1),
        Arc(1, 2, 4, 2, -math.pi/2, 0),  # from -pi/2 to 0 around [2,2]
        Line(2, 3),
        Line(3, 0)
    ]
    try:
        room_arc = Room(points_arc, outlines_arc)
        print("Room with arc created successfully.")
    except ValueError as e:
        print(f"Error creating room with arc: {e}")
