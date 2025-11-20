"""Utility to manage WebSocket connections grouped by job id."""

from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, List, Set

from fastapi import WebSocket


class ConnectionManager:
    """Tracks subscribers and broadcasts JSON payloads to each job id."""

    def __init__(self) -> None:
        self.connections: DefaultDict[str, Set[WebSocket]] = defaultdict(set)
        self.backlog: DefaultDict[str, List[dict]] = defaultdict(list)

    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[job_id].add(websocket)
        if self.backlog.get(job_id):
            for message in list(self.backlog[job_id]):
                try:
                    await websocket.send_json(message)
                except Exception:
                    break
            self.backlog.pop(job_id, None)

    def disconnect(self, job_id: str, websocket: WebSocket) -> None:
        group = self.connections.get(job_id)
        if not group:
            return
        group.discard(websocket)
        if not group:
            self.connections.pop(job_id, None)

    async def broadcast(self, job_id: str, message: dict) -> None:
        """Send JSON payloads to every listener on the given job id."""
        targets = list(self.connections.get(job_id, []))
        if not targets:
            self.backlog[job_id].append(message)
            return
        for websocket in targets:
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(job_id, websocket)

    async def close_job(self, job_id: str) -> None:
        """Close all sockets and drop cached messages for the given job."""
        sockets = list(self.connections.pop(job_id, []))
        for websocket in sockets:
            try:
                await websocket.close()
            except Exception:
                pass
