from fastapi import APIRouter
from pathlib import Path

from fastapi.responses import FileResponse

from silp.lib.debug.debug import Debug_based_work_id

router = APIRouter(
    prefix="/debug", tags=["debug"])

DEBUG_ROOT = Path("debug")

def _get_debug_file(work_id:int,name:str)->Path:
    path = DEBUG_ROOT / str(work_id) / name
    if not path.exists():
        raise FileNotFoundError(f"Debug file not found: {path}")
    return path

@router.get("/navfield/{work_id}/obstacle")
def get_obstacle_image(work_id: int):
    file_path  = _get_debug_file(work_id, "obstacle.png")
    return  FileResponse(file_path)

@router.get("/navfield/{work_id}/edt")
def get_edt_image(work_id: int):
    file_path  = _get_debug_file(work_id, "edt.png")
    return  FileResponse(file_path)



