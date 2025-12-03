"""API routes for submitting planner jobs and streaming their progress."""

from __future__ import annotations

import asyncio
import json
from unittest import case
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from silp.core.geometry.shape import Rectangle
from silp.domain.furniture import Furniture
from silp.lib.connection_manager import ConnectionManager
from silp.api.schemas.api import LayoutRequest
from silp.lib.debug.debug import Debug_based_work_id, Debug
from silp.services.planner.path_find_Astar import astar_shortest_path
from silp.services.planner.path_find_bfs_op import bfs_shortest_path
from silp.services.planner.room_path_find import room_path_find

from silp.domain.layout import layout_example_a,layout_example_b


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
    print(f"WebSocket connection requested for job {job_id}.")
    await manager.connect(job_id, websocket)
    try:
        await manager.broadcast(job_id, {"type": "status", "payload":{"message": f"Connected to job {job_id}."}})
        while True:
            raw_message = await websocket.receive_text()
            try:
                message = json.loads(raw_message)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "payload":{"message": "Invalid JSON payload."}})
                continue

            if message.get("type") == "command" :
                payload = message.get("payload", {})
                command = payload.get("command") 
                print("Command received:", command)
                await manager.broadcast(job_id, {"type": "status", "payload":{"message": f"Received command '{command}'  for job {job_id}."}})

                match command:
                    case "start_path_finding":
                        # room = payload.get("room", None)
                        # furniture_list = payload.get("furnitures", None)
                        # method = payload.get("algorithm","Astar")
                        # agent = payload.get("agent", None)
                        print("Starting path finding...")
                        print("the chosen layout index:", payload.get("parameters", {}).get("selected", 0))
                        
                        if payload.get("parameters", {}).get("selected", 0) == 0:
                            room = layout_example_a.room
                            furniture_list = layout_example_a.furnitures
                        else:
                            room = layout_example_b.room
                            furniture_list = layout_example_b.furnitures
                        method = "Astar"
                        agent = None
                        path = await  asyncio.to_thread(room_path_find, room, furniture_list, method, agent=agent, debug=debug)
                        path = _serialize_path(path)
                        await manager.broadcast(job_id, {"type": "path_response", "payload":{"command":"start_path_finding", "path": path}})
                        if len(path) == 0:
                            print("No path found.")
                        else:   
                            print("Path finding completed.")

                    case "get_example_layout":
                        print("Getting example room layouts...")
                        data_layout = _get_example_room_layout()
                       
                        await manager.broadcast(job_id, {"type": "layout_response", "payload":{"command":"get_example_layout", "layout": data_layout}})
                        print("Example layout sent.")
                    case _:
                        pass

            elif message.get("type") == "subscribe" :
                await manager.broadcast(job_id, {"type": "status", "payload":{"message": f"Subscribed to job {job_id}."}})
                continue
            elif message.get("type") == "status":
                print("Status command received:", message.get("payload"))
                await manager.broadcast(job_id, {"type": "status", "payload":{"message": f"Status command received for job {job_id}."}})
                continue
    except WebSocketDisconnect:
        await manager.broadcast(job_id, {"type": "status", "payload":{"message": f"Disconnected from job {job_id}."} })
        manager.disconnect(job_id, websocket)


def _serialize_path(path):
    # path 是 [(r,c), (r,c) ...] 或 [(x,y) ...]
    return [list(p) for p in path]

def _get_example_room_layout()->list:

    import silp.domain.layout as layout
    data_layout_a = layout.data_room_layout_example_a
    data_layout_b = layout.data_room_layout_example_b
    return [data_layout_a, data_layout_b]
    