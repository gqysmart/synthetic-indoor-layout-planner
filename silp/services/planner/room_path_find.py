from typing import List, Optional
from pathlib import Path
from collections import deque
import numpy as np
from silp.core.geometry.coorinate_system import PixelCoordinateSystem
from silp.core.geometry.shape import Rectangle
from silp.lib.debug.debug import Debug, Debug_based_work_id
from silp.services.planner.navigation_field import PixelNavigationField, SimpleAgent,Agent
from silp.domain.layout import room_example_a
from silp.domain.furniture import (
    Furniture,
    furniture_example_table,
    furniture_example_desk_round,
    furniture_example_bed,
    furniture_example_wardrobe,
)
from silp.services.planner.path_find_bfs_op import bfs_shortest_path
from silp.services.planner_core_simplified.model_simplified import Room   

def room_path_find(room: Optional[Room]=None, furniture_list:Optional[List[Furniture]]=None, method:str|None=None, agent:Optional[Agent]=None, debug:Debug=None) -> list[float,float]:
    """BFS 寻路示例。"""
    # 构建导航场
    if room is None:    
        room = room_example_a
    if furniture_list is None:
        furniture_list = [
            # furniture_example_table,
            # furniture_example_desk_round,
            furniture_example_bed,
        # furniture_example_wardrobe,
    ]
    if agent is None:
        agent = SimpleAgent(radius_m=0.0)

    rect: Rectangle = room.shape      # 假设 Room.shape 是 Rectangle(width, height)
    room_w = rect.width
    room_h = rect.height

    pixels_per_meter = 100
    pcs = PixelCoordinateSystem(
        pixels_per_meter=pixels_per_meter,
        canvas_size=(
            int(np.ceil(room_w * pixels_per_meter)) + 40,
            int(np.ceil(room_h * pixels_per_meter)) + 40,
        ),
        center_world=(0.0, 0.0),
    )

    

    nav = PixelNavigationField(pcs).from_room_and_furniture_with_simple_agent(
        room=room,
        furniture_list=furniture_list,
        agent=agent,
        debug=debug,
    )

    start = (300, 320)
    goal = (250, 300)   # 随便先放一个不等于 start 的点
    method = method if method is not None else "BFS"
    path = []
    if method=="Astar":
        from silp.services.planner.path_find_Astar import astar_shortest_path
        path = astar_shortest_path(start, goal, nav,debug=debug) 

    elif method=="BFS":
        path = bfs_shortest_path(start, goal, nav,debug=debug)

    if path is not None:
       if debug is not None:
            walkable_img = nav.walkable_image
            walkable_img[[row for row,col in path],[col for row,col in path]]=0
            debug.save_image(
                walkable_img, "path")
            
       return pcs.pixels_to_worlds(path)
    return []

if __name__ == "__main__":
    DEBUG_ROOT = Path("debug")
    debug = Debug_based_work_id(save_dir=str(DEBUG_ROOT))
    
    path = room_path_find(debug=debug)
    print("path:", path)