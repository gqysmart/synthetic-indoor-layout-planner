from dataclasses import dataclass
from my_app.backend.lib.geometry.shape import Transform
import numpy as np  
import cv2 as cv

@dataclass
class CVViewport:
    pixels_per_meter: float
    canvas_size: tuple[int, int]          # (width_px, height_px)
    center_world: tuple[float, float] = (0.0, 0.0)
   

    def __post_init__(self):
        self.width_px, self.height_px = self.canvas_size
        self._update_origin_world()

        # 初始化画布
        self.image = np.ones((self.height_px, self.width_px, 3), dtype=np.uint8) * 255

    def _update_origin_world(self):
        cx, cy = self.center_world
        w_half_m = (self.width_px  / 2 ) / self.pixels_per_meter
        h_half_m = (self.height_px / 2 ) / self.pixels_per_meter

        # 这里就是自动算出来的 world_left_top
        self.world_left_top = (cx - w_half_m, cy - h_half_m)

    def set_zoom(self, pixels_per_meter: float):
        self.pixels_per_meter = pixels_per_meter
        self._update_origin_world()

    def set_center(self, center_world: tuple[float, float]):
        self.center_world = center_world
        self._update_origin_world()

    def world_to_pixel(self, x: float, y: float) -> tuple[int, int]:
        wx0, wy0 = self.world_left_top
        col = int((x - wx0) * self.pixels_per_meter) 
        row = int((y - wy0) * self.pixels_per_meter)
        return col, row

    def display_poly(self,corner_points:list,color: tuple[int, int, int] = (0, 255, 0), with_stroke: bool = True):
        pts = np.array(
            [self.world_to_pixel(x, y) for (x, y) in corner_points],
            np.int32
        ).reshape((-1, 1, 2))
        cv.fillPoly(self.image, [pts], color)   
        if with_stroke:
            cv.polylines(self.image, [pts], isClosed=True, color=(0,0,0), thickness=2)
        return self.image
    
    def display_text(self,text:str, poistion_world: tuple[float, float], font_scale: float = 0.7, color: tuple[int, int, int] = (0, 0, 0)):
        position_px = self.world_to_pixel(poistion_world[0], poistion_world[1])
        cv.putText(self.image, text, position_px, cv.FONT_HERSHEY_SIMPLEX, font_scale, color, 2)
        return self.image
       
    # def fill_polygon(self, corner_points: list[tuple[float, float]],
    #                  color: tuple[int, int, int] = (0, 255, 0)):
    #     pts = np.array(
    #         [self.world_to_pixel(x, y) for (x, y) in corner_points],
    #         np.int32
    #     ).reshape((-1, 1, 2))
    #     cv.fillPoly(self.image, [pts], color)
    #     return self.image

    def show(self, winname="CVViewport"):
        cv.imshow(winname, self.image)
        cv.waitKey(0)
        cv.destroyAllWindows()


def test_viewport():
    # 家具大小
    fw = 2.0
    fh = 1.0

    # 家具 transform：中心在(1,1), 旋转30°
    T = Transform(x=1.0, y=1.0, r=30)

    # 家具 local 四个角点
    local_corners = [
        (-fw/2, -fh/2),
        ( fw/2, -fh/2),
        ( fw/2,  fh/2),
        (-fw/2,  fh/2),
    ]

    # 转成 world 坐标
    world_corners = [T.local_to_world(x,y) for (x,y) in local_corners]

    print("World corners:")
    for p in world_corners:
        print("   ", p)

    # 创建 Viewport
    viewport = CVViewport(
        pixels_per_meter=100,
        canvas_size=(1000, 800),       # 画布 1000×800 px
        center_world=(0,0),            # 世界中心对齐画布中心
        margin_px=50                   # 留白 50px
    )

    # 绘制家具
    viewport.fill_polygon(world_corners, (0,0,255))

    viewport.show()



if __name__ == "__main__":
    test_viewport()