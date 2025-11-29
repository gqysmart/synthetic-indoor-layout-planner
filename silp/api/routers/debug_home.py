from fastapi import APIRouter, Request
from pathlib import Path

from silp.lib.debug.debug import Debug_based_work_id

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/debug", tags=["debug_home"])

THIS_DIR = Path (__file__).resolve()
TEMPLATE_DIR = THIS_DIR.parent.parent / "templates"
DEBUG_ROOT = Path("debug")
debug = Debug_based_work_id(save_dir=str(DEBUG_ROOT))

template = Jinja2Templates(directory=str(TEMPLATE_DIR))

@router.get("/", response_class= HTMLResponse)
async def debug_home(request:Request):
    """Render the debug home page."""
    worked_items :list[dict] = []
    readme_contents: dict = {}

    if DEBUG_ROOT.exists() and DEBUG_ROOT.is_dir():
        for item in DEBUG_ROOT.iterdir():
            if not item.is_dir():
                continue

            worked_items.append({
                "work_id": item.name,
                "path": f"/debug/{item.name}"
            })
            readme_path = item / "README.md"
            if readme_path.exists() and readme_path.is_file():
                try:
                    content = readme_path.read_text(encoding="utf-8")
                except Exception:
                    continue
                readme_contents[item.name] =  content
               

    context = {
        "request": request,
        "worked_items": worked_items,
        "readme_contents": readme_contents,
        "debug_text":worked_items[0]
    }

    return template.TemplateResponse("debug_home.html", context)