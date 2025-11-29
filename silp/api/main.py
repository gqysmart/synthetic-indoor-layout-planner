"""FastAPI application factory that wires routers and shared settings."""

from fastapi import FastAPI
from pathlib import Path

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from silp.api.routers import debug
from silp.api.routers import debug_home
from silp.api.routers import room_plan


PUBLIC_DIR = Path(__file__).parent / "public"
web_title = "Synthetic indoor layout planner"

app = FastAPI(title=web_title)
app.include_router(debug.router)
app.include_router(debug_home.router)
app.include_router(room_plan.router)

app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")  

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
      <body>
        <h1>SILP Server</h1>
        <p><a href='/debug'>enter debug home</a></p>
      </body>
    </html>
    """