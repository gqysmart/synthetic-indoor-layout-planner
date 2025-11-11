"""Render Room objects to PNG data URLs for WebSocket delivery."""

from __future__ import annotations

import base64

from ..models.room import CVRender, Room


def room_image_data_url(room: Room) -> str:
    """
    Render the provided room and return a data URL (PNG).

    Raises RuntimeError if OpenCV cannot encode the image.
    """
    renderer = CVRender(pixels_per_m=120.0, margin=40)
    canvas = renderer.render(room)
    cv2, _ = renderer._ensure_cv()
    ok, buffer = cv2.imencode(".png", canvas)
    if not ok:
        raise RuntimeError("Failed to encode room canvas to PNG.")
    encoded = base64.b64encode(buffer.tobytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
