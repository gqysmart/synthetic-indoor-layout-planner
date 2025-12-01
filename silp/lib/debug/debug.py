import cv2 as cv
import numpy as np
from abc import ABC, abstractmethod
from pathlib import Path


class Debug(ABC):
    def __init__(self, save_dir: str, enable: bool = True):
        self.save_dir = save_dir
        self.enable = enable

    @abstractmethod
    def save_mask(self, mask: np.ndarray, file_name: str):
        ...

    @abstractmethod
    def save_image(self, image: np.ndarray, filename: str):
        ...

    def to_uint8_image(self, img: np.ndarray) -> np.ndarray:
        """
        Normalize and convert any image to uint8.
        - (H, W) single channel -> global normalization
        - (H, W, C) multi-channel -> per-channel normalization
        """

        if img is None:
            return None

        # already uint8 → no change
        if img.dtype == np.uint8:
            return img

        # Single channel
        if img.ndim == 2:
            arr = img.astype(np.float32)
            arr -= arr.min()
            maxv = arr.max()
            if maxv > 0:
                arr /= maxv
            arr = (arr * 255).astype(np.uint8)
            return arr

        # Multi-channel (3 or 4)
        if img.ndim == 3 and img.shape[2] in (3, 4):
            arr = img.astype(np.float32)

            # per-channel normalization
            arr -= arr.min(axis=(0, 1), keepdims=True)

            maxv = arr.max(axis=(0, 1), keepdims=True)
            maxv[maxv == 0] = 1.0  # avoid division by zero

            arr /= maxv
            arr = (arr * 255).astype(np.uint8)
            return arr

        raise ValueError(f"Unsupported image shape: {img.shape}, dtype: {img.dtype}")


class Debug_based_work_id(Debug):
    def __init__(self, save_dir: str, work_id: str = "01", enable: bool = True):
        super().__init__(save_dir, enable)
        self.work_id = work_id
        self._ensure_dir()

    def _ensure_dir(self):
        """确保 debug/{work_id}/ 目录存在。"""
        Path(self.save_dir, self.work_id).mkdir(parents=True, exist_ok=True)

    def set_work_id(self, work_id: str):
        self.work_id = work_id
        self._ensure_dir()

    def save_mask(self, mask: np.ndarray, file_name: str):
        if not self.enable:
            return
        print(f"Debug: saving mask to {file_name}.png")
        self._ensure_dir()

        filepath = Path(self.save_dir, self.work_id, f"{file_name}.png")

        # 根据类型安全地转换
        if mask.dtype == np.bool_:
            mask_u8 = mask.astype(np.uint8) * 255
        elif mask.dtype == np.uint8:
            mask_u8 = mask
        else:
            # 比如 float 0/1，或者其他类型，直接用归一化逻辑
            mask_u8 = self.to_uint8_image(mask)

        cv.imwrite(str(filepath), mask_u8)

    def save_image(self, image: np.ndarray, filename: str):
        if not self.enable:
            return
        print(f"Debug: saving image to {filename}.png")

        self._ensure_dir()

        filepath = Path(self.save_dir, self.work_id, f"{filename}.png")

        img_uint8 = self.to_uint8_image(image)
        cv.imwrite(str(filepath), img_uint8)
