"""Pydantic models exposed through the HTTP/WebSocket API."""

from pydantic import BaseModel


class LayoutRequest(BaseModel):
    maxNumberOfInteration: int
    methond: str
