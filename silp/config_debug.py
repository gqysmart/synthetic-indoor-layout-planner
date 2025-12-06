# silp/config_debug.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # 指到 silp/ 这一层
DEBUG_ROOT = (BASE_DIR / "debug").resolve()
