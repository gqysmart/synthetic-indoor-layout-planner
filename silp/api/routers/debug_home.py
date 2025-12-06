from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="silp/api/templates")
from silp.config_debug import DEBUG_ROOT 

router = APIRouter()

PER_PAGE = 20

@router.get("/debug", response_class=HTMLResponse)
async def debug_home(
    request: Request,
    q: str | None = None,       # 搜索关键词（work_id 子串）
    page: int = 1,              # 当前页（从 1 开始）
):
    debug_root = DEBUG_ROOT  # Path("debug")

    # 1. 获取所有 work_id 目录，并按“修改时间”从新到旧排序
    all_dirs = sorted(
        [p for p in debug_root.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    # 2. 映射成简单对象（这里用 dict，你也可以用 Pydantic / dataclass）
    all_items = [{"work_id": p.name, "path": p} for p in all_dirs]

    # 3. 搜索：如果传了 q，就只保留包含 q 的 work_id
    if q:
        all_items = [item for item in all_items if q in item["work_id"]]

    total = len(all_items)

    # 4. 分页，只显示 1–20、21–40 这样
    page = max(page, 1)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    page_items = all_items[start:end]

    # 5. 读取 README（假设每个 work 目录下有 README.txt，你按需改）
    readme_contents: dict[str, str] = {}
    for item in page_items:
        readme_path = item["path"] / "README.txt"
        if readme_path.exists():
            readme_contents[item["work_id"]] = readme_path.read_text(encoding="utf-8")
        else:
            readme_contents[item["work_id"]] = "(no README.txt)"

    # 6. 传到模板的上下文
    context = {
        "request": request,
        "worked_items": page_items,      # 只包含当前页 1–20 条
        "readme_contents": readme_contents,
        "debug_text": "",
        "total": total,
        "page": page,
        "per_page": PER_PAGE,
        "start_index": start,           # 0-based
        "end_index": min(end, total),   # 1-based 显示用
        "q": q,
    }

    return templates.TemplateResponse("debug_home.html", context)
