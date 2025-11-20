"""Lightweight Matplotlib helpers for plotting geomCore polylines."""
from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple
import math

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
import cv2

from .geomCore import ArcSegment, LineSegment, PointRegistry, Polyline, um_to_m


def polyline_xy(
    polyline: Polyline,
    registry: PointRegistry,
    *,
    close: Optional[bool] = None,
    arc_resolution: int = 16,
) -> Tuple[Sequence[float], Sequence[float]]:
    """Return x/y coordinate sequences (in metres) for the given polyline.

    Args:
        polyline: Target polyline from ``geomCore``.
        registry: Point registry used to look up coordinates.
        close: Force closure of the point list. Defaults to polyline.closed.
        arc_resolution: Approximate number of samples per full circle for arcs.
    """
    if not polyline.segments:
        return (), ()

    should_close = polyline.closed if close is None else close
    samples_per_circle = max(8, arc_resolution)
    xs: list[float] = []
    ys: list[float] = []

    def append_point(x_um: float, y_um: float) -> None:
        x_m = um_to_m(int(round(x_um)))
        y_m = um_to_m(int(round(y_um)))
        if xs and math.isclose(xs[-1], x_m) and math.isclose(ys[-1], y_m):
            return
        xs.append(x_m)
        ys.append(y_m)

    for segment in polyline.segments:
        x0_um, y0_um, _ = registry.get_um(segment.p0)
        if not xs:
            append_point(x0_um, y0_um)

        if isinstance(segment, LineSegment):
            x1_um, y1_um, _ = registry.get_um(segment.p1)
            append_point(x1_um, y1_um)
            continue

        if isinstance(segment, ArcSegment):
            (cx_um, cy_um), r_um, sweep = segment._circle_params(registry)
            if not math.isfinite(r_um) or abs(sweep) < 1e-9:
                x1_um, y1_um, _ = registry.get_um(segment.p1)
                append_point(x1_um, y1_um)
                continue

            start_angle = math.atan2(y0_um - cy_um, x0_um - cx_um)
            total_steps = max(2, int(math.ceil(samples_per_circle * abs(sweep) / (2 * math.pi))))
            step = sweep / total_steps
            for i in range(1, total_steps + 1):
                angle = start_angle + step * i
                x_um = cx_um + r_um * math.cos(angle)
                y_um = cy_um + r_um * math.sin(angle)
                append_point(x_um, y_um)
            continue

        raise TypeError(f"Unsupported segment type: {type(segment)!r}")

    if should_close and xs and (not math.isclose(xs[0], xs[-1]) or not math.isclose(ys[0], ys[-1])):
        xs.append(xs[0])
        ys.append(ys[0])

    return xs, ys


def plot_polyline(
    polyline: Polyline,
    registry: PointRegistry,
    *,
    ax: Optional[Axes] = None,
    close: Optional[bool] = None,
    arc_resolution: int = 16,
    show: bool = False,
    equal_aspect: bool = True,
    **plot_kwargs: object,
) -> Axes:
    """Plot a single polyline on the provided Matplotlib axes."""
    xs, ys = polyline_xy(polyline, registry, close=close, arc_resolution=arc_resolution)
    if ax is None:
        _, ax = plt.subplots()
    ax.plot(xs, ys, **plot_kwargs)
    if equal_aspect:
        ax.set_aspect("equal", adjustable="box")
    if show:
        plt.show()
    return ax


def plot_polylines(
    polylines: Iterable[Polyline],
    registry: PointRegistry,
    *,
    ax: Optional[Axes] = None,
    close: Optional[bool] = None,
    arc_resolution: int = 16,
    show: bool = False,
    equal_aspect: bool = True,
    colors: Optional[Iterable[str]] = None,
    **plot_kwargs: object,
) -> Axes:
    """Plot multiple polylines with optional color cycling."""
    if ax is None:
        _, ax = plt.subplots()

    color_cycle: Optional[tuple[str, ...]] = None
    if colors is not None:
        color_cycle = tuple(colors)
        if not color_cycle:
            color_cycle = None

    for idx, poly in enumerate(polylines):
        kwargs = dict(plot_kwargs)
        if color_cycle is not None:
            kwargs.setdefault("color", color_cycle[idx % len(color_cycle)])
        xs, ys = polyline_xy(poly, registry, close=close, arc_resolution=arc_resolution)
        ax.plot(xs, ys, **kwargs)

    if equal_aspect:
        ax.set_aspect("equal", adjustable="box")
    if show:
        plt.show()
    return ax


def plot_polyline_cv(
    polyline: Polyline,
    registry: PointRegistry,
    *,
    canvas: Optional[np.ndarray] = None,
    pixels_per_m: float = 100.0,
    margin: int = 20,
    close: Optional[bool] = None,
    arc_resolution: int = 16,
    color: Tuple[int, int, int] = (0, 165, 255),
    thickness: int = 2,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    show: bool = False,
    window_name: str = "polyline",
) -> np.ndarray:
    """Render a polyline onto an OpenCV canvas and return the image.

    Args:
        polyline: Polyline to render.
        registry: Point registry for coordinate lookup.
        canvas: Optional target image (BGR). If omitted a new canvas is created.
        pixels_per_m: Scalar to convert metres to pixels.
        margin: Padding (pixels) around the computed bounding box.
        close: Force closure of the points list, defaults to ``polyline.closed``.
        arc_resolution: Samples used to approximate arcs when flattening.
        color: BGR colour used when drawing the polyline.
        thickness: Line thickness (pixels).
        background_color: Colour used for a generated canvas.
        show: If True, display the image via ``cv2.imshow``.
        window_name: Window title when ``show`` is True.

    Returns:
        The image containing the rendered polyline.
    """
    xs, ys = polyline_xy(polyline, registry, close=close, arc_resolution=arc_resolution)
    if not xs:
        if canvas is None:
            canvas = np.full((2 * margin, 2 * margin, 3), background_color, dtype=np.uint8)
        if show:
            cv2.imshow(window_name, canvas)
            cv2.waitKey(0)
            cv2.destroyWindow(window_name)
        return canvas

    coords = np.column_stack([xs, ys]) * float(pixels_per_m)
    min_vals = coords.min(axis=0)
    max_vals = coords.max(axis=0)
    span = np.maximum(max_vals - min_vals, 1.0)

    width = int(math.ceil(span[0])) + 2 * margin
    height = int(math.ceil(span[1])) + 2 * margin

    shifted = coords - min_vals + margin
    shifted[:, 1] = (max_vals[1] - coords[:, 1]) + margin
    points_px = np.round(shifted).astype(np.int32)

    if canvas is None:
        canvas = np.full((height, width, 3), background_color, dtype=np.uint8)

    cv2.polylines(
        canvas,
        [points_px.reshape(-1, 1, 2)],
        isClosed=bool(polyline.closed if close is None else close),
        color=color,
        thickness=thickness,
        lineType=cv2.LINE_AA,
    )

    if show:
        cv2.imshow(window_name, canvas)
        cv2.waitKey(0)
        cv2.destroyWindow(window_name)
    return canvas
