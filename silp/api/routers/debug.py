# silp/api/routers/debug_home.py

from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from silp.config_debug import DEBUG_ROOT  # ✅ 全项目统一用这一份 ROOT

# ========== 基础配置 ==========

# __file__ = silp/api/routers/debug_home.py
BASE_DIR = Path(__file__).resolve().parents[1]   # -> silp/api
TEMPLATES_DIR = BASE_DIR / "templates"          # -> silp/api/templates

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


router = APIRouter(prefix="/debug", tags=["debug"])

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
PER_PAGE = 20


# ========== 首页：列出所有 work_id（支持搜索 + 分页） ==========

@router.get("", response_class=HTMLResponse, name="debug_home")
async def debug_home(
    request: Request,
    q: str | None = None,
    page: int = 1,
):
    """
    /debug 首页：
    - 按 mtime 排序显示所有 work_id
    - 支持 q 搜索 work_id 子串
    - 支持分页，每页 PER_PAGE 条
    """
    debug_root = DEBUG_ROOT

    if not debug_root.exists():
        # 如果根目录不存在，就直接渲染空页面提示
        return templates.TemplateResponse(
            "debug_home.html",
            {
                "request": request,
                "worked_items": [],
                "readme_contents": {},
                "debug_text": f"Debug directory not found: {debug_root}",
                "total": 0,
                "page": page,
                "per_page": PER_PAGE,
                "start_index": 0,
                "end_index": 0,
                "q": q,
            },
        )

    # 1. 获取所有 work 目录并按 mtime（新→旧）排序
    all_dirs = sorted(
        [p for p in debug_root.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    # 2. 映射成简单对象列表
    all_items = [{"work_id": p.name, "path": p} for p in all_dirs]

    # 3. 搜索：按 work_id 子串过滤
    if q:
        all_items = [item for item in all_items if q in item["work_id"]]

    total = len(all_items)
    page = max(page, 1)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    page_items = all_items[start:end]

    # 4. 读取当前页每个 work 的 README（可选）
    readme_contents: dict[str, str] = {}
    for item in page_items:
        readme_path = item["path"] / "README.txt"
        if readme_path.exists():
            readme_contents[item["work_id"]] = readme_path.read_text(encoding="utf-8")
        else:
            readme_contents[item["work_id"]] = "(no README.txt)"

    return templates.TemplateResponse(
        "debug_home.html",
        {
            "request": request,
            "worked_items": page_items,
            "readme_contents": readme_contents,
            "debug_text": "",
            "total": total,
            "page": page,
            "per_page": PER_PAGE,
            "start_index": start,
            "end_index": min(end, total),
            "q": q,
        },
    )


# ========== 详情页：显示某个 work_id 的 README + 图片 + 其它文件 ==========

@router.get("/work/{work_id}", response_class=HTMLResponse, name="debug_work_detail")
async def debug_work_detail(
    request: Request,
    work_id: str,
):
    work_dir = (DEBUG_ROOT / work_id)
    work_dir_resolved = work_dir.resolve()

    # 防止路径穿越
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
            "images": images,  # 模板里显示所有图片
            "files": others,   # 模板里显示其它文件（文本/json等）
        },
    )


# ========== 公用：从 work_id 里取某个文件 ==========

def _get_debug_file(work_id: str, name: str) -> Path:
    path = (DEBUG_ROOT / str(work_id) / name).resolve()

    # 防止路径穿越：必须在 DEBUG_ROOT 下
    if DEBUG_ROOT not in path.parents:
        raise FileNotFoundError(f"Invalid debug file path: {path}")

    if not path.exists():
        raise FileNotFoundError(f"Debug file not found: {path}")

    return path


# ========== 已有接口：navfield 专用的两张图 ==========

@router.get("/navfield/{work_id}/obstacle")
def get_obstacle_image(work_id: str):
    file_path = _get_debug_file(work_id, "obstacle.png")
    return FileResponse(file_path)


@router.get("/navfield/{work_id}/edt")
def get_edt_image(work_id: str):
    file_path = _get_debug_file(work_id, "edt.png")
    return FileResponse(file_path)


# ========== 新增：泛用文件读取接口（详情页 <img> 用的） ==========

@router.get("/work/{work_id}/file/{filename}", name="debug_work_file")
def get_work_file(work_id: str, filename: str):
    file_path = _get_debug_file(work_id, filename)
    return FileResponse(file_path)
