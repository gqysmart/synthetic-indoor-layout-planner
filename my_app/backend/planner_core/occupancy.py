import numpy as np

class BitsetOccupancy:
    def __init__(self, H:int, W:int):
        # 0=free, 1=blocked
        self.map = np.zeros((H, W), np.uint8)
        self._last_changed_bbox = None

    def aabb_for(self, x:int, y:int, w:int, h:int, theta:int):
        # 仅 0/90°；返回像素坐标 AABB
        if theta % 180 == 0:
            return (y, y+h, x, x+w)
        else:
            return (y, y+w, x, x+h)

    def collide(self, mask:np.ndarray, top:int, left:int) -> bool:
        h, w = mask.shape
        sub = self.map[top:top+h, left:left+w]
        if sub.shape != mask.shape:  # 出界
            return True
        return np.any(sub & mask)

    def insert(self, mask:np.ndarray, top:int, left:int):
        h, w = mask.shape
        self.map[top:top+h, left:left+w] |= mask
        self._last_changed_bbox = (top, left, top+h, left+w)

    def remove(self, mask:np.ndarray, top:int, left:int):
        h, w = mask.shape
        self.map[top:top+h, left:left+w] &= (~mask)
        self._last_changed_bbox = (top, left, top+h, left+w)

    def last_changed_bbox(self):
        return self._last_changed_bbox
