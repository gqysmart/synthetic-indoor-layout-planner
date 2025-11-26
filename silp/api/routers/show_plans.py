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
from silp.domain.room import Room
from silp.services.job_runner import run_planner_job


router = APIRouter()
manager = ConnectionManager()

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "index.html"
HTML_PAGE = TEMPLATE_PATH.read_text(encoding="utf-8")

pending_jobs: dict[str, tuple[LayoutRequest, Room | None]] = {}
pending_jobs_lock = asyncio.Lock()


async def _start_pending_job(job_id: str) -> bool:
    """Pop a pending job and launch the planner if available."""
    async with pending_jobs_lock:
        job_payload = pending_jobs.pop(job_id, None)
    if not job_payload:
        return False
    request, room = job_payload
    asyncio.create_task(run_planner_job(job_id, request, manager, room))
    return True


@router.get("/", response_class=HTMLResponse, tags=["ui"])
async def home() -> HTMLResponse:
    """Serve the demo form that kicks off planner jobs."""
    return HTMLResponse(HTML_PAGE)


@router.post("/jobs", tags=["jobs"])
async def create_job(
    maxNumberOfInteration: int = Form(...),
    methond: str = Form(...),
    roomFile: UploadFile | None = File(None),
) -> dict:
    """Accept planner parameters (plus optional room JSON) and launch the worker."""
    job_id = uuid.uuid4().hex[:8]
    request = LayoutRequest(
        maxNumberOfInteration=maxNumberOfInteration,
        methond=methond,
    )
    # room = await room_from_upload(roomFile)

    # async with pending_jobs_lock:
    #     pending_jobs[job_id] = (request, room)

    return {"job_id": job_id}


@router.websocket("/ws/jobs/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str) -> None:
    """Relay planner progress via WebSocket."""
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

            if message.get("type") == "command" and message.get("command") == "start_planning":
                started = await _start_pending_job(job_id)
                if started:
                    await manager.broadcast(job_id, {"type": "status", "message": "Planner run requested."})
                else:
                    await manager.broadcast(
                        job_id,
                        {"type": "warning", "message": "No pending job found or planner already running."},
                    )
                continue

            await manager.broadcast(
                job_id,
                {"type": "warning", "message": f"Unhandled message for {job_id}: {message!r}"},
            )

    except WebSocketDisconnect:
        await manager.broadcast(job_id, {"type": "status", "message": f"Disconnected from job {job_id}."})
        manager.disconnect(job_id, websocket)
