from dataclasses import dataclass,field
from enum import Enum
from typing import Dict, List, Tuple

from silp.core.geometry.shape import Rectangle, Arc, Shape
from silp.core.geometry.coorinate_system import Transform

from silp.core.geometry.placed_entity import PlacedEntity


class FurnitureType(Enum):
    BED_DOUBLE = "bed_double"
    DESK_STD = "desk_std"
    WARDROBE_2D = "wardrobe_2d"
    SOFA_3SEAT = "sofa_3seat"
    TABLE_4P = "table_4p"
    DESK_ROUND = "desk_round"


@dataclass
class FurnitureSpec:
    type: FurnitureType
    shape: Shape
    reach_offsets: List[Tuple[float, float]]



@dataclass
class Furniture(PlacedEntity):
    name:str
    type: FurnitureType 
    
    @classmethod
    def from_type(
        cls,
        id: str,
        name:str,
        type: FurnitureType,
        furniture_lib: "FurnitureLibrary",
        transform: Transform = Transform()) -> "Furniture":

        return cls(
            name=name,
            type=type,
            shape_ref = furniture_lib.get_spec(type).shape,
            transform=transform)
    
    def clone_to(self, new_name:str, transform: Transform) -> "Furniture":
        return Furniture(
            name=new_name,
            type=self.type,
            shape_ref=self.shape_ref,
            transform=transform,
        )


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
        "code": FurnitureType.DESK_ROUND,
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

            shape = Rectangle(width=width, height=depth)
            if f_type == FurnitureType.DESK_ROUND:
                shape = Arc(radius=width/2, start_angle=0, end_angle=360)


            specs[f_type] = FurnitureSpec(
                type=f_type,
                shape=shape,
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

furniture_example_table = Furniture.from_type(
    id="table_01",
    name="Dining Table",
    type=FurnitureType.TABLE_4P,
    furniture_lib=furniture_lib,
    transform=Transform(x=1.4, y=-1.05, r=90),
)

furniture_example_bed = Furniture.from_type (
    id="bed_01",
    name="Double Bed",
    type=FurnitureType.BED_DOUBLE,
    furniture_lib=furniture_lib,
    transform=Transform(x=-0.8, y=-0.9, r=0),
)
furniture_example_wardrobe = Furniture.from_type(
    id="wardrobe_01",
    name="Wardrobe",
    type=FurnitureType.WARDROBE_2D,
    furniture_lib=furniture_lib,
    transform=Transform(x=0, y=1.35, r=0),
)   

furniture_example_desk_round = Furniture.from_type(
    id="desk_round_01",
    name="Round Desk",
    type=FurnitureType.DESK_ROUND,
    furniture_lib=furniture_lib,
    transform=Transform(x=0, y=0, r=90),
)
