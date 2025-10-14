"""Render a sample room outline to an OpenCV canvas."""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = ROOT / "my-app" / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from models.room import Arc, CVRender, Line, Room  # noqa: E402
from models.furnishings import Furnish  # noqa: E402


def build_sample_room() -> Room:
    """Create a simple room with a rounded corner."""
    points = [
        [0.0, 0.0],
        [4.0, 0.0],
        [6.0, 2.0],
        [6.0, 5.0],
        [0.0, 5.0],
        [4.0, 2.0],  # arc center
    ]
    outline = [
        Line(0, 1),
        Arc(1, 2, 5, radius=2.0, start_angle=-math.pi / 2, end_angle=0.0),
        Line(2, 3),
        Line(3, 4),
        Line(4, 0),
    ]
    return Room(points, outline)


def build_sample_furniture(room: Room) -> list[Furnish]:
    """Populate the sample room with a few furniture footprints."""
    bed = Furnish.bed("Bed")
    bed.x = 1.6
    bed.y = 3.6
    bed.rotation = 0.0

    wardrobe = Furnish.wardrobe("Wardrobe")
    wardrobe.anchor = "bottom-left"
    wardrobe.x = 0.3
    wardrobe.y = 4.2

    sofa = Furnish.sofa("Sofa")
    sofa.x = 4.6
    sofa.y = 1.6
    sofa.rotation = -90.0

    coffee_table = Furnish(
        name="CoffeeTable",
        type="table",
        width=1.0,
        length=0.6,
        height=0.45,
        x=3.9,
        y=2.2,
        rotation=0.0,
    )

    return [bed, wardrobe, sofa, coffee_table]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "sample_room_cv.png",
        help="File path for the generated image.",
    )
    parser.add_argument("--show", action="store_true", help="Display the image in an OpenCV window.")
    parser.add_argument("--pixels-per-m", type=float, default=120.0, help="Pixels per metre when rasterising.")
    parser.add_argument("--margin", type=int, default=40, help="Padding around the rendered geometry.")
    parser.add_argument("--iterations", type=int, default=5, help="Number of frames to render in sequence.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    room = build_sample_room()
    room.extend_furnitures(build_sample_furniture(room))

    renderer = CVRender(
        pixels_per_m=args.pixels_per_m,
        margin=args.margin,
    )

    canvas = None
    total_iterations = max(1, args.iterations)
    for iteration in range(total_iterations):
        print(f"Iteration {iteration + 1}")
        renderer.print_room(room)

        output_path = args.output
        if total_iterations > 1:
            output_path = args.output.with_name(f"{args.output.stem}_{iteration + 1}{args.output.suffix}")

        canvas = renderer.save(room, output_path)
        print(f"Saved OpenCV render to {output_path}")

        for furnish in room.furnitures:
            furnish.x += 0.05
            furnish.y += 0.05

    if args.show:
        renderer.show(room, window_name="room", canvas=canvas, wait_ms=0)


if __name__ == "__main__":
    main()
