import sys
from pathlib import Path
import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = ROOT / "my-app" / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from lib.geometry.geomCore import PointRegistry, Polyline
from models.visualize import plot_polylines


class PlotPolylinesTest(unittest.TestCase):
    def test_draws_each_polyline_with_expected_color(self) -> None:
        registry = PointRegistry()

        p0 = registry.acquire_m(0.0, 0.0, 0.0)
        p1 = registry.acquire_m(1.0, 0.0, 0.0)
        p2 = registry.acquire_m(0.0, 2.0, 0.0)

        poly_horizontal = Polyline.from_points([p0, p1])
        poly_vertical = Polyline.from_points([p0, p2])

        fig, ax = plt.subplots()
        try:
            colors = ["red", "blue"]
            plot_polylines([poly_horizontal, poly_vertical], registry, ax=ax, colors=colors)

            self.assertEqual(2, len(ax.lines))

            x0, y0 = ax.lines[0].get_data()
            self.assertEqual([0.0, 1.0], list(x0))
            self.assertEqual([0.0, 0.0], list(y0))
            self.assertEqual("red", ax.lines[0].get_color())

            x1, y1 = ax.lines[1].get_data()
            self.assertEqual([0.0, 0.0], list(x1))
            self.assertEqual([0.0, 2.0], list(y1))
            self.assertEqual("blue", ax.lines[1].get_color())
        finally:
            plt.close(fig)


if __name__ == "__main__":
    unittest.main()
