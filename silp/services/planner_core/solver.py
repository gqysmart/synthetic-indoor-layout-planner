import numpy as np
from .occupancy import BitsetOccupancy
from .distance_field import edt_from_obstacles, edt_update_local
from .widest_path import widest_path_single_source, reachable
from .candidates import local_max_candidates, wall_strip_candidates, rank_by_heuristic
from .corridor import reserve_corridors

def solve(room, furns, opts):
    """
    room: RoomSpec(dict) -> 包含 room_mask(0/1), static_obstacle(0/1), doors_px[], pixel_size_m
    furns: list[ {id,w_px,h_px,margin_px,prefer_wall,bool, approach_edges:[(y,x), ...], orientations:[0,90]} ]
    opts:  {main_corridor_m:0.8, aux_corridor_m:0.6, step_px:1, max_local_iters:50}
    """
    H, W = room["room_mask"].shape
    static = room["static_obstacle"].copy().astype(np.uint8)  # 墙、柱、门扇、窗保留等
    pixel_size_m = room["pixel_size_m"]
    # 预留通道（可关闭：传 None）
    if opts.get("main_corridor_m"):
        D0 = edt_from_obstacles(static, pixel_size_m)
        keep_main, keep_aux = reserve_corridors(D0, room["doors_px"],
                                                opts["main_corridor_m"], opts["aux_corridor_m"], pixel_size_m)
        static |= (keep_main | keep_aux)

    # 初始距离场 + 单源最大瓶颈
    D = edt_from_obstacles(static, pixel_size_m)
    src = tuple(room["doors_px"][0])  # 主入口
    dist_all = widest_path_single_source(D, src)
    occ = BitsetOccupancy(H, W)

    # 1) 构造解：大件优先
    furns_sorted = sorted(furns, key=lambda f: f["w_px"]*f["h_px"], reverse=True)
    placements = {}
    for f in furns_sorted:
        placed = False
        cands = local_max_candidates(D) + wall_strip_candidates(room["room_mask"])
        for (y,x) in rank_by_heuristic(cands, D, f.get("prefer_wall", False)):
            for theta in f["orientations"]:
                mask = furniture_mask_px(f, theta)        # >>> 你已有几何/栅格化就复用
                top, left = y - mask.shape[0]//2, x - mask.shape[1]//2
                # 1-2 硬约束
                if top < 0 or left < 0: continue
                if occ.collide(mask, top, left): continue
                # 3 可达：接近点像素坐标（随 theta 旋转）
                ap = approach_points_px(f, (top,left), theta)
                if not reachable(dist_all, ap, thr_m=0.60): continue
                # 放下
                occ.insert(mask, top, left)
                D = edt_update_local(D, static | occ.map, occ.last_changed_bbox(), pixel_size_m)
                dist_all = widest_path_single_source(D, src)  # 简洁起见全域重算；工程上可做局部松弛
                placements[f["id"]] = {"y":int(y), "x":int(x), "theta":theta, "top":int(top), "left":int(left)}
                placed = True
                break
            if placed: break
        if not placed:
            return {"ok": False, "reason": f"cannot place {f['id']}"}

    # 2) 局部解拥（只接受改善“最小瓶颈”或“拥挤面积”）
    for _ in range(opts.get("max_local_iters", 50)):
        improved = local_decongest_step(placements, occ, D, dist_all, static, src, pixel_size_m)
        if not improved: break

    return {"ok": True, "placements": placements}
