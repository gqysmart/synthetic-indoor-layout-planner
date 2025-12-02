from dataclasses import dataclass
import math

from dataclasses import dataclass
from typing import Tuple, List
import numpy as np
import cv2 as cv


# ==========================================================
# 6. Transform
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

    def clone(self) -> 'Transform':
        return Transform(
            x=self.x,
            y=self.y,
            r=self.r,
            sx=self.sx,
            sy=self.sy,
        )
    
# ==========================================================
    


@dataclass
class PixelCoordinateSystem:
    """
    负责 World <-> Pixel 的坐标转换 + 多边形栅格化。
    - 世界坐标单位：米 (m)
    - 像素坐标单位：pixel (col=x, row=y)
    """
    pixels_per_meter: float                   # 每米多少像素
    canvas_size: Tuple[int, int]             # (width_px, height_px)
    center_world: Tuple[float, float] = (0.0, 0.0)  # 画布中心在 world 里的位置 (cx, cy)

    def __post_init__(self):
        self.width_px, self.height_px = self.canvas_size
        self._update_origin_world()

    # ------------------------------------------------------------------
    # 内部：根据 center_world & 分辨率，计算 world 左上角坐标
    # ------------------------------------------------------------------
    def _update_origin_world(self):
        cx, cy = self.center_world
        half_w_m = (self.width_px  / 2.0) / self.pixels_per_meter
        half_h_m = (self.height_px / 2.0) / self.pixels_per_meter

        # 世界坐标中，对应画布左上角的 (wx0, wy0)
        # 注意：这里假设 world 和 pixel 的 y 方向都是“向下为正”
        self.world_left_top = (cx - half_w_m, cy - half_h_m)

    @property
    def pixel_size_in_world(self) -> float:
        """每个像素在 world 里的实际尺寸（米）。"""
        return 1.0 / self.pixels_per_meter
    # ------------------------------------------------------------------
    # 配置接口：缩放 / 平移
    # ------------------------------------------------------------------
    def set_zoom(self, pixels_per_meter: float):
        """修改缩放比例（同时更新世界原点）。"""
        self.pixels_per_meter = pixels_per_meter
        self._update_origin_world()

    def set_center(self, center_world: Tuple[float, float]):
        """修改以哪个 world 点作为画布中心。"""
        self.center_world = center_world
        self._update_origin_world()

    # ------------------------------------------------------------------
    # 坐标转换：World <-> Pixel
    # ------------------------------------------------------------------
    def world_to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        """
        世界坐标 (x, y in meters) -> 像素坐标 (col, row)
        col 对应图像的 x（宽方向），row 对应图像的 y（高方向）
        """
        wx0, wy0 = self.world_left_top
        col = int(round((x - wx0) * self.pixels_per_meter))
        row = int(round((y - wy0) * self.pixels_per_meter))
        return  col,row
    
    def worlds_to_pixels(self, world_pts: List[Tuple[float, float]]) -> List[Tuple[int, int]]:
        """
        世界坐标列表 (x, y in meters) -> 像素坐标列表 (col, row)
        col 对应图像的 x（宽方向），row 对应图像的 y（高方向）
        """
        return [self.world_to_pixel(x, y) for (x, y) in world_pts]
    
    def pixels_to_worlds(self, pixel_pts: List[Tuple[int, int]]) -> List[Tuple[float, float]]:
        """
        像素坐标列表 (col, row) -> 世界坐标列表 (x, y in meters)
        """
        return [self.pixel_to_world(col, row) for (row, col) in pixel_pts]

    def pixel_to_world(self, col: int, row: int) -> Tuple[float, float]:
        """
        像素坐标 (col, row) -> 世界坐标 (x, y in meters)
        """
        wx0, wy0 = self.world_left_top
        x = wx0 + col / self.pixels_per_meter
        y = wy0 + row / self.pixels_per_meter
        return x, y

    # ------------------------------------------------------------------
    # 多边形相关：World 多边形 -> Pixel 点集 / mask
    # ------------------------------------------------------------------
    def world_poly_to_pixel_pts(
        self,
        world_points: List[Tuple[float, float]]
    ) -> np.ndarray:
        """
        把 world 坐标的多边形顶点列表，转换为 OpenCV 需要的像素顶点数组：
        返回形状为 (N, 1, 2) 的 np.int32 数组。
        """
        pts = np.array(
            [self.world_to_pixel(x, y) for (x, y) in world_points],
            dtype=np.int32
        ).reshape((-1, 1, 2))
        return pts

    def polygon_to_mask(
        self,
        world_points: List[Tuple[float, float]],
        value: int = 1
    ) -> np.ndarray:
        """
        把 world 坐标的多边形栅格化成一张 0/1 mask（height_px x width_px）。
        value: 填充值，默认 1。
        """
        mask = np.zeros((self.height_px, self.width_px), dtype=np.uint8)
        pts = self.world_poly_to_pixel_pts(world_points)
        cv.fillPoly(mask, [pts], value)
        return mask

    def empty_mask(self, value: int = 0) -> np.ndarray:
        """生成一张空的 mask。"""
        return np.full((self.height_px, self.width_px), value, dtype=np.uint8)
