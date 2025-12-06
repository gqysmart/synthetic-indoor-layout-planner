# silp/api/routers/debug_work_detail.py

from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from silp.config_debug import DEBUG_ROOT  # ✅ 和 debug_home 用同一个
# from silp.lib.debug.debug import Debug_based_work_id  # 现在没用到，可以先注释

# ===== 模板目录 =====
BASE_DIR = Path(__file__).resolve().parents[2]      # 到项目根 synthetic-indoor-layout-planner
TEMPLATES_DIR = BASE_DIR / "silp" / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# 整个文件只定义一次 router
router = APIRouter(prefix="/debug", tags=["debug"])

# 图片后缀白名单
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


@router.get("/work/{work_id}", response_class=HTMLResponse, name="debug_work_detail")
async def debug_work_detail(
    request: Request,
    work_id: str,
):
    """
    显示某个 work_id 的详情页：README + 所有图片 + 其它文件列表
    """
    # ✅ 统一使用 config 中的 DEBUG_ROOT
    work_dir = (DEBUG_ROOT / work_id)

    # 如果你担心路径穿越，可以加一层 resolve + parents 检查：
    work_dir_resolved = work_dir.resolve()
    if DEBUG_ROOT not in work_dir_resolved.parents and work_dir_resolved != DEBUG_ROOT:
        raise HTTPException(status_code=400, detail="Invalid work_id")

    if not work_dir_resolved.exists() or not work_dir_resolved.is_dir():
        raise HTTPException(status_code=404, detail="work_id not found")

    # README
    readme_path = work_dir_resolved / "README.txt"
    readme = (
        readme_path.read_text(encoding="utf-8")
        if readme_path.exists()
        else "(no README.txt)"
    )

    images: list[str] = []
    others: list[str] = []

    for p in work_dir_resolved.iterdir():
        if p.is_file():
            if p.suffix.lower() in IMAGE_EXTS:
                images.append(p.name)
            else:
                others.append(p.name)

    images.sort()
    others.sort()

    return templates.TemplateResponse(
        "debug_work_detail.html",
        {
            "request": request,
            "work_id": work_id,
            "readme": readme,
            "images": images,   # 模板里用来显示所有图片
            "files": others,    # 模板里显示其它文件名
        },
    )


# ====== 公用文件读取函数 ======

def _get_debug_file(work_id: str, name: str) -> Path:
    """
    给定 work_id 和文件名，返回绝对路径；不存在时抛 FileNotFoundError。
    """
    path = (DEBUG_ROOT / str(work_id) / name).resolve()

    # 防止路径穿越：必须在 DEBUG_ROOT 之内
    if DEBUG_ROOT not in path.parents:
        raise FileNotFoundError(f"Invalid debug file path: {path}")

    if not path.exists():
        raise FileNotFoundError(f"Debug file not found: {path}")

    return path


# ====== 专门给 navfield 用的两个旧接口（保留也可以） ======

@router.get("/navfield/{work_id}/obstacle")
def get_obstacle_image(work_id: str):
    file_path = _get_debug_file(work_id, "obstacle.png")
    return FileResponse(file_path)


@router.get("/navfield/{work_id}/edt")
def get_edt_image(work_id: str):
    file_path = _get_debug_file(work_id, "edt.png")
    return FileResponse(file_path)


# ====== 新增：泛用静态文件接口（供详情页展示所有图片用） ======

@router.get("/work/{work_id}/file/{filename}")
def get_work_file(work_id: str, filename: str):
    """
    任意文件访问接口：/debug/work/{work_id}/file/{文件名}
    详情页里 <img src="..."> 用的就是这个。
    """
    file_path = _get_debug_file(work_id, filename)
    return FileResponse(file_path)
