"""Simulated long-running planner job that streams progress updates."""

from __future__ import annotations

import asyncio
from typing import Protocol
import uuid 

from ..models.api import LayoutRequest
from ..models.room import Room
from .room_factory import random_room
from .room_renderer import room_image_data_url


class SupportsBroadcast(Protocol):
    async def broadcast(self, job_id: str, message: dict) -> None: ...
    async def close_job(self, job_id: str) -> None: ...

async def create_planner_job(request: LayoutRequest) -> str:
    job_id =  uuid.uuid4().hex[:8]
    request = LayoutRequest(
        maxNumberOfInteration= request.maxNumberOfInteration,
        methond=request.methond,
    )
    return job_id

    

async def run_planner_job(
    job_id: str,
    request: LayoutRequest,
    manager: SupportsBroadcast,
    room: Room | None = None,
) -> None:
    """
    Mock planner loop.

    Replace this function with the real search algorithm once it is ready.
    """
    try:
       
        effective_room = room or random_room()
        await manager.broadcast(job_id, {"type": "room", "summary": effective_room.describe()})
        try:
            image_url = room_image_data_url(effective_room)
        except Exception as exc:  # pragma: no cover - depends on cv2
            await manager.broadcast(
                job_id,
                {"type": "warning", "message": f"Failed to render room preview: {exc}"},
            )
        else:
            await manager.broadcast(job_id, {"type": "room_image", "data_url": image_url})

        await manager.broadcast(job_id, {"type": "status", "message": "Planner run started."})
        
    except Exception as exc:  # pragma: no cover - demo logging
        await manager.broadcast(job_id, {"type": "error", "message": str(exc)})
    finally:
        await manager.close_job(job_id)
