from dataclasses import dataclass, field
from typing import Optional, List
import numpy as np
import cv2 as cv

from silp.core.geometry.coorinate_system import PixelCoordinateSystem
from silp.core.geometry.placed_entity import PlacedEntity
from silp.lib.debug.debug import Debug


class MaskValue:
    mask_value_container = 255
    mask_value_obstacle = 100
    mask_value_furniture = 20

@dataclass
class Agent:
    pass

@dataclass
class SimpleAgent(Agent):
    radius_m: float
    extra_clearance_m: float = 0.0

    @property
    def required_clearance_m(self) -> float:
        return self.radius_m + self.extra_clearance_m


@dataclass
class PixelNavigationField:
    pcs: PixelCoordinateSystem

    container_mask: Optional[np.ndarray] = None  # 2D array representing container areas
    obstacle_mask: Optional[np.ndarray] = None   # 2D array representing obstacle areas

    distance_to_obstacles: Optional[np.ndarray] = field(default=None, init=False)  # float32 EDT
    walkable_mask: Optional[np.ndarray] = field(default=None, init=False)         # bool

    mask_value: MaskValue = field(default_factory=MaskValue)


    # ---------- 查询接口 ----------

    def is_obstacle(self, row: int, col: int) -> bool:
        if self.obstacle_mask is None:
            raise ValueError("obstacle_mask is not initialized.")
        h, w = self.obstacle_mask.shape
        if not (0 <= row < h and 0 <= col < w):
            return False
        return self.obstacle_mask[row, col] == self.mask_value.mask_value_obstacle

    def is_walkable(self, row: int, col: int) -> bool:
        if self.walkable_mask is None:
            raise ValueError("walkable_mask is not computed.")
        h, w = self.walkable_mask.shape
        if not (0 <= row < h and 0 <= col < w):
            return False
        return bool(self.walkable_mask[row, col])

    # ---------- 构造 / 预处理 ----------

    def from_room_and_furniture_with_simple_agent(
        self,
        room: PlacedEntity,
        furniture_list: Optional[List[PlacedEntity]] = None,
        agent: Optional[SimpleAgent] = None,
        debug: Optional[Debug] = None,
    ) -> "PixelNavigationField":
        """
        使用房间 + 家具 + SimpleAgent 构造像素导航场：
        - 生成 container_mask / obstacle_mask
        - 如果给了 agent，则直接计算 EDT + walkable_mask
        """

        width_px, height_px = self.pcs.canvas_size
        h, w = height_px, width_px

        # 1) container mask: 房间区域
        container_mask = np.zeros((h, w), dtype=np.uint8)
        room_poly_world = room.world_polygon()
        container_mask = self.pcs.polygon_to_mask(
            room_poly_world,
            value=self.mask_value.mask_value_container,
        )

        # 2) obstacle mask: 家具
        obstacle_mask = np.zeros((h, w), dtype=np.uint8)
        if furniture_list is not None:
            for furn in furniture_list:
                poly_world = furn.world_polygon()
                m = self.pcs.polygon_to_mask(
                    poly_world,
                    value=self.mask_value.mask_value_obstacle,
                )
                obstacle_mask[m == self.mask_value.mask_value_obstacle] = (
                    self.mask_value.mask_value_obstacle
                )

        # 保存到 self
        self.container_mask = container_mask
        self.obstacle_mask = obstacle_mask
        if debug is not None:
            debug.save_image(
                self.obstacle_mask, "obstacle")

        # 3) 如果给了 agent，顺便构建 walkable_mask
        if agent is not None:
            px_req = agent.required_clearance_m * self.pcs.pixels_per_meter
            self._build_dist_and_walkable_with_simple_agent(px_req, debug=debug)

        return self

    def _build_dist_and_walkable_with_simple_agent(self, px_req: float, debug: Optional[Debug] = None) -> None:
        """
        使用 EDT 为“圆形 SimpleAgent”构建
        - distance_to_obstacles
        - walkable_mask
        """

        if self.container_mask is None or self.obstacle_mask is None:
            raise ValueError("container_mask or obstacle_mask is not initialized.")

        # free 区域：在房间内且不是障碍
        free_uint8 = np.where(
            (self.container_mask == self.mask_value.mask_value_container)
            & (self.obstacle_mask != self.mask_value.mask_value_obstacle),
            255,
            0,
        ).astype(np.uint8)

        # L2 distance transform（EDT）
        dist = cv.distanceTransform(
            free_uint8,
            distanceType=cv.DIST_L2,
            maskSize=cv.DIST_MASK_PRECISE,
        )
        self.distance_to_obstacles = dist
        if debug is not None:
            debug.save_image(
                self.distance_to_obstacles, "edt")


        # 在房间内，且距离障碍 ≥ px_req 的位置是 walkable
        walkable = (
            (dist >= px_req)
            & (self.container_mask == self.mask_value.mask_value_container)
        )
        self.walkable_mask = walkable

    # ---------- 调试可视化 ----------

   

    def to_debug_bgr(self) -> np.ndarray:
        if self.container_mask is None or self.obstacle_mask is None:
            raise ValueError("container_mask or obstacle_mask is not initialized.")

        h, w = self.container_mask.shape
        img = np.zeros((h, w, 3), dtype=np.uint8)

        # 房间内：先填白
        img[self.container_mask == self.mask_value.mask_value_container] = (255, 255, 255)

        # 障碍：红
        img[self.obstacle_mask == self.mask_value.mask_value_obstacle] = (0, 0, 255)

        if self.walkable_mask is not None:
            # 可通行区域叠加绿色
            mask = self.walkable_mask
            img[mask] = (0, 255, 0)

        return img
