"""Quick demo for plotting polylines using visualize helpers."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import cv2

ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = ROOT / "my-app" / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from lib.geometry import PointRegistry, Polyline, plot_polylines, plot_polyline_cv


def main() -> None:
    registry = PointRegistry()

    p0 = registry.acquire_m(0.0, 0.0, 0.0)
    p1 = registry.acquire_m(4.0, 0.0, 0.0)
    p2 = registry.acquire_m(4.0, 3.0, 0.0)
    p3 = registry.acquire_m(0.0, 3.0, 0.0)
    rectangle = Polyline.from_points([p0, p1, p2, p3], closed=True)

    p4 = registry.acquire_m(1.0, 1.0, 0.0)
    p5 = registry.acquire_m(3.0, 2.0, 0.0)
    diagonal = Polyline.from_points([p4, p5])

    fig, ax = plt.subplots(figsize=(6, 4))
    plot_polylines([rectangle, diagonal], registry, ax=ax, colors=["tab:blue", "tab:orange"])
    ax.set_title("Sample Floor Outline")
    ax.grid(True, linestyle="--", linewidth=0.5)

    output_dir = ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    mpl_output = output_dir / "sample_polyline.png"
    fig.savefig(mpl_output, dpi=200)
    print(f"Saved Matplotlib figure to {mpl_output}")
    plt.show()

    canvas = plot_polyline_cv(
        rectangle,
        registry,
        pixels_per_m=120.0,
        margin=40,
        color=(20, 120, 240),
        thickness=3,
        show=False,
    )
    cv_output = output_dir / "sample_polyline_cv.png"
    cv2.imwrite(str(cv_output), canvas)
    print(f"Saved OpenCV render to {cv_output}")


if __name__ == "__main__":
    main()
