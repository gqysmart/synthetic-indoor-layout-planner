from dataclasses import dataclass
from typing import List


# ---------- 基础几何 ----------

@dataclass
class Rectangle:
    x: float
    y: float
    w: float
    h: float
    rotation: float = 0.0  # 先不考虑，统一当 0 用


# ---------- 领域对象 ----------

@dataclass
class Room:
    id: str
    name: str
    rect: Rectangle   # 房间轮廓矩形


@dataclass
class FurnitureType:
    id: str           # 如 "bed_queen"
    name: str         # "Queen Bed"
    category: str     # "bed", "sofa", ...
    size_w: float     # 默认宽度
    size_h: float     # 默认高度
    min_clearance: float = 0.0   # 预留空隙（暂时不用）


@dataclass
class FurnitureInstance:
    id: str           # 如 "bed_1"
    type_id: str      # 对应 FurnitureType.id
    can_rotate: bool = True


@dataclass
class Placement:
    furniture_id: str
    rect: Rectangle   # 家具在房间中的位置
    rotation: float = 0.0


@dataclass
class Layout:
    room_id: str
    placements: List[Placement]
    score: float = 0.0           # 布局评分（暂时可以不管）
