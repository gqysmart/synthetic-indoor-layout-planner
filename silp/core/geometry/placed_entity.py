from dataclasses import dataclass, field,replace
from abc import ABC, abstractmethod
from typing import Literal, Union
from silp.core.geometry.coorinate_system import Transform
from silp.core.geometry.shape import Shape


@dataclass(kw_only=True)
class PlacedEntity(ABC):
    shape_ref: Shape 
    transform: Transform = field(default_factory=Transform)

    @property
    def shape(self) -> Shape:
        return self.shape_ref

    def world_polygon(self) -> list[tuple[float, float]]:
        local_corners = self.shape.get_polygon_points()
        # 转换到世界坐标
        return [
            self.transform.local_to_world(x, y)
            for (x, y) in local_corners
        ]
    
    def local_polygon(self) -> list[tuple[float, float]]:
        return self.shape.get_polygon_points()
    
    def clone(self) -> "PlacedEntity":
        """
        Create a copy of this entity.
        """
        
            
        new_transform=Transform(
                x=self.transform.x,
                y=self.transform.y,
                r=self.transform.r,
            ),
        return replace(self, transform=new_transform)
        
    
    def move(self, dx: float, dy: float) -> None:
        """
        Move the entity by (dx, dy) in world coordinates.
        """
        self.transform.move(dx, dy)

    def move_to(self, x: float, y: float) -> None:
        """
        Move the entity to (x, y) in world coordinates.
        """
        self.transform.move_to(x, y)

    def rotate(self, dr: float) -> None:
        """
        Rotate the entity by dr degrees.
        """
        self.transform.r += dr
        self.transform.r = self.transform.r % 360   

    def rotate_to(self, r: float) -> None:
        """
        Rotate the entity to r degrees.
        """
        self.transform.r = r % 360
