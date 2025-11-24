import heapq
import numpy as np

def widest_path_single_source(D: np.ndarray, src: tuple[int,int]) -> np.ndarray:
    H, W = D.shape
    dist = np.zeros_like(D, dtype=np.float32)
    pq = [(-D[src], src)]  # max-heap via negative
    dist[src] = D[src]
    nbr = [(1,0),(-1,0),(0,1),(0,-1)]
    while pq:
        negw, (y,x) = heapq.heappop(pq)
        w = -negw
        if w < dist[y,x]:  # 过期
            continue
        for dy,dx in nbr:
            ny, nx = y+dy, x+dx
            if 0 <= ny < H and 0 <= nx < W and D[ny,nx] > 0:
                cand = min(w, D[ny,nx])
                if cand > dist[ny,nx]:
                    dist[ny,nx] = cand
                    heapq.heappush(pq, (-cand, (ny,nx)))
    return dist

def reachable(dist_all: np.ndarray, points: list[tuple[int,int]], thr_m: float) -> bool:
    return any(dist_all[py, px] >= thr_m for (py,px) in points)
