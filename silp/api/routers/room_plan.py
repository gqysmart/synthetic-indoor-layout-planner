"""API routes for submitting planner jobs and streaming their progress."""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from silp.lib.connection_manager import ConnectionManager
from silp.api.schemas.api import LayoutRequest
from silp.lib.debug.debug import Debug_based_work_id, Debug
from silp.services.planner.path_find_Astar import astar_shortest_path
from silp.services.planner.path_find_bfs_op import bfs_shortest_path
from silp.services.planner.room_path_find import room_path_find


router = APIRouter(prefix="/plan", tags=["planner"])
manager = ConnectionManager()
DEBUG_ROOT = Path("debug")

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "index.html"
HTML_PAGE = TEMPLATE_PATH.read_text(encoding="utf-8")

# async def _start_pending_job(job_id: str) -> bool:
#     """Pop a pending job and launch the planner if available."""
#     async with pending_jobs_lock:
#         job_payload = pending_jobs.pop(job_id, None)
#     if not job_payload:
#         return False
#     request, room = job_payload
#     asyncio.create_task(run_planner_job(job_id, request, manager, room))
#     return True


@router.get("/", response_class=HTMLResponse, tags=["ui"])
async def home() -> HTMLResponse:
    """Serve the demo form that kicks off planner jobs."""
    return HTMLResponse(HTML_PAGE)


@router.post("/jobs", tags=["jobs"])
async def create_job(
  
) -> dict:
    """Accept planner parameters (plus optional room JSON) and launch the worker."""
    job_id = uuid.uuid4().hex[:8]
    
    return {"job_id": job_id}


@router.websocket("/ws/jobs/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str) -> None:
    """Relay planner progress via WebSocket."""
    debug: Debug = Debug_based_work_id(save_dir=str(DEBUG_ROOT), work_id=job_id)
    await manager.connect(job_id, websocket)
    try:
        await manager.broadcast(job_id, {"type": "status", "message": f"Connected to job {job_id}."})
        while True:
            raw_message = await websocket.receive_text()
            try:
                message = json.loads(raw_message)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON payload."})
                continue

            if message.get("type") == "command" and message.get("command") == "room_path_finding":
                # room = message.get("room") 
                # furniture_list = message.get("furniture_list")
                # method = message.get("method","Astar")
                room = None 
                furniture_list = None
                agent = None
                method = message.get("method","Astar")
                
                path = await  asyncio.to_thread(room_path_find, room, furniture_list, method, agent=agent, debug=debug)
                path = _serialize_path(path)
                await manager.broadcast(job_id, {"type": "path", "path": path})

                continue

            elif message.get("type") == "subscribe" :
                await manager.broadcast(job_id, {"type": "status", "message": f"Subscribed to job {job_id}."})
                continue
            
                
           

    except WebSocketDisconnect:
        await manager.broadcast(job_id, {"type": "status", "message": f"Disconnected from job {job_id}."})
        manager.disconnect(job_id, websocket)


def _serialize_path(path):
    # path 是 [(r,c), (r,c) ...] 或 [(x,y) ...]
    return [list(p) for p in path]