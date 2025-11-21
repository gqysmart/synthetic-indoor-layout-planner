from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

from my_app.backend.lib.geometry.shape import PlacedRectangle,Rectangle
from my_app.backend.lib.geometry.shape import Transform


class FurnitureType(Enum):
    BED_DOUBLE = "bed_double"
    DESK_STD = "desk_std"
    WARDROBE_2D = "wardrobe_2d"
    SOFA_3SEAT = "sofa_3seat"
    TABLE_4P = "table_4p"


@dataclass
class FurnitureSpec:
    type: FurnitureType
    shape: Rectangle  # (width, depth) in meters
    reach_offsets: List[Tuple[float, float]]


@dataclass
class Furniture:
    id: str
    spec: FurnitureSpec
    transform: Transform
    def world_corners(self) -> list[tuple[float, float]]:
        """
        返回家具旋转后的四个世界坐标角点（顺序适用于 cv.fillPoly）：
        顺序：左上 → 右上 → 右下 → 左下（逆时针）
        """

        fw = self.spec.shape.width
        fh = self.spec.shape.height   # 或 height，看你的字段名

        # 家具本地坐标下的四个角
        # （⚠️ y 轴向下为正，与 OpenCV 坐标系一致）
        local_corners = [
            (-fw / 2.0, -fh / 2.0),   # 左上
            ( fw / 2.0, -fh / 2.0),   # 右上
            ( fw / 2.0,  fh / 2.0),   # 右下
            (-fw / 2.0,  fh / 2.0),   # 左下
        ]

        # 转换到世界坐标
        return [
            self.transform.local_to_world(x, y)
            for (x, y) in local_corners
        ]



RAW_FURNITURE_DATA = [
    {
        "code": FurnitureType.BED_DOUBLE,
        "size": (2.0, 1.5),        # 双人床 2.0m x 1.5m
        "reach_mode": "front_sides",
        "margin": 0.6,
    },
    {
        "code": FurnitureType.DESK_STD,
        "size": (1.2, 0.6),
        "reach_mode": "front",     # 只需要前面可达
        "margin": 0.7,
    },
    {
        "code": FurnitureType.WARDROBE_2D,
        "size": (1.8, 0.6),
        "reach_mode": "front",     # 衣柜前面可达
        "margin": 0.8,
    },
    {
        "code": FurnitureType.SOFA_3SEAT,
        "size": (2.0, 0.8),
        "reach_mode": "front",
        "margin": 0.6,
    },
    {
        "code": FurnitureType.TABLE_4P,
        "size": (1.2, 0.8),
        "reach_mode": "all",       # 四面都可达
        "margin": 0.6,
    },
]


def compute_reach_offsets(width: float, depth: float, mode: str, margin: float) -> List[Tuple[float, float]]:
    """
    Compute clearance offsets (relative to furniture center) to keep walkable space.
    """
    hw = width / 2
    hd = depth / 2
    offsets: List[Tuple[float, float]] = []

    if mode in ("front", "front_sides", "all"):
        offsets.append((0.0, -(hd + margin)))
    if mode in ("front_sides", "all"):
        offsets.append((-(hw + margin), 0.0))
        offsets.append(((hw + margin), 0.0))
    if mode == "all":
        offsets.append((0.0, hd + margin))

    return offsets


class FurnitureLibrary:
    def __init__(self, specs: Dict[FurnitureType, FurnitureSpec]):
        self._specs = dict(specs)

    @classmethod
    def from_default_data(cls) -> "FurnitureLibrary":
        specs: Dict[FurnitureType, FurnitureSpec] = {}

        for item in RAW_FURNITURE_DATA:
            f_type: FurnitureType = item["code"]
            width, depth = item["size"]
            mode: str = item["reach_mode"]
            margin: float = item["margin"]

            offsets = compute_reach_offsets(width, depth, mode, margin)

            specs[f_type] = FurnitureSpec(
                type=f_type,
                shape=Rectangle(width=width, height=depth),
                reach_offsets=offsets,
            )

        return cls(specs)

    @classmethod
    def from_dicts(cls, rows: List[dict]) -> "FurnitureLibrary":
        specs: Dict[FurnitureType, FurnitureSpec] = {}
        for item in rows:
            f_type = item["code"]
            if isinstance(f_type, str):
                f_type = FurnitureType(f_type)  # 支持字符串
            width, depth = item["size"]
            mode: str = item.get("reach_mode", "front")
            margin: float = item.get("margin", 0.6)
            offsets = compute_reach_offsets(width, depth, mode, margin)
            specs[f_type] = FurnitureSpec(
                type=f_type,
                shape=Rectangle(width=width, height=depth),
                reach_offsets=offsets,
            )
        return cls(specs)

    def get_spec(self, f_type: FurnitureType) -> FurnitureSpec:
        return self._specs[f_type]

    def all_specs(self) -> List[FurnitureSpec]:
        return list(self._specs.values())

    def __contains__(self, f_type: FurnitureType) -> bool:
        return f_type in self._specs

    def __len__(self) -> int:
        return len(self._specs)


furniture_lib = FurnitureLibrary.from_default_data()

furniture_example_table = Furniture(
    id="table_01",
    spec=furniture_lib.get_spec(FurnitureType.TABLE_4P),
    transform=Transform(x=0, y=0, r=30),
)

furniture_example_bed = Furniture(
    id="bed_01",
    spec=furniture_lib.get_spec(FurnitureType.BED_DOUBLE),
    transform=Transform(x=0, y=0, r=45),
)
furniture_example_wardrobe = Furniture(
    id="wardrobe_01",
    spec=furniture_lib.get_spec(FurnitureType.WARDROBE_2D),
    transform=Transform(x=0, y=0, r=90),
)   
