from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import cv2 as cv

from my_app.backend.core.geometry.coorinate_system import PixelCoordinateSystem


@dataclass
class CVViewport:
    """
    CVViewport = 负责在 pixel layer 进行绘制的“渲染层”
    - 不负责 world/pixel 坐标转换
    - 不负责 local/world transform
    - 只负责调用 PixelCoordinateSystem，把 pixel 点渲染出来
    """
    pcs: PixelCoordinateSystem                      # world <-> pixel 的坐标系统
    background_color: Tuple[int, int, int] = (255, 255, 255)

    def __post_init__(self):
        self.width_px, self.height_px = self.pcs.canvas_size
        self._init_canvas()

    # -----------------------------------------------------------
    # 初始化画布
    # -----------------------------------------------------------
    def _init_canvas(self):
        self.image = np.ones((self.height_px, self.width_px, 3), dtype=np.uint8)
        self.image[:] = self.background_color

    # -----------------------------------------------------------
    # basic draw functions
    # -----------------------------------------------------------
    def draw_polygon(
        self,
        world_points: List[Tuple[float, float]],
        color: Tuple[int, int, int] = (0, 255, 0),
        stroke: bool = True
    ):
        """
        world_points: [(x,y), (x,y), ...]
        """
        pts = self.pcs.world_poly_to_pixel_pts(world_points)  # 委托 pcs
        cv.fillPoly(self.image, [pts], color)

        if stroke:
            cv.polylines(self.image, [pts], True, (0, 0, 0), thickness=2)

    def draw_text(
        self,
        text: str,
        position_world: Tuple[float, float],
        color: Tuple[int, int, int] = (0, 0, 0),
        scale: float = 0.6,
        thickness: int = 1
    ):
        col, row = self.pcs.world_to_pixel(*position_world)
        cv.putText(
            self.image,
            text,
            (col, row),
            cv.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            thickness,
        )

    # -----------------------------------------------------------
    # show / clear
    # -----------------------------------------------------------
    def show(self, winname="CVViewport"):
        cv.imshow(winname, self.image)
        cv.waitKey(0)
        cv.destroyAllWindows()

    def clear(self):
        self._init_canvas()


    # -----------------------------------------------------------
    # 提供一个辅助：world poly -> mask（调用 pcs）
    # -----------------------------------------------------------
    def polygon_to_mask(self, world_points, value=1) -> np.ndarray:
        """
        只是代理给 PixelCoordinateSystem，使得 viewport 在算法层也能方便使用。
        """
        return self.pcs.polygon_to_mask(world_points, value)
