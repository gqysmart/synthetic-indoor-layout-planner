"""Utilities to parse uploaded room JSON files into Room objects."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List

from fastapi import HTTPException, UploadFile, status

from ..models.furnishings import Furnish
from ..models.room import Arc, Line, Room


def _parse_points(data: Any) -> List[List[float]]:
    if not isinstance(data, list) or not data:
        raise ValueError("`points` must be a non-empty list.")
    points: List[List[float]] = []
    for idx, coord in enumerate(data):
        if (
            not isinstance(coord, (list, tuple))
            or len(coord) != 2
            or not all(isinstance(value, (int, float)) for value in coord)
        ):
            raise ValueError(f"`points[{idx}]` must be [x, y].")
        points.append([float(coord[0]), float(coord[1])])
    return points


def _parse_outline(data: Any) -> List[Line | Arc]:
    if not isinstance(data, list) or not data:
        raise ValueError("`outline` must be a non-empty list.")

    outline: List[Line | Arc] = []
    for idx, segment in enumerate(data):
        if not isinstance(segment, dict) or "type" not in segment:
            raise ValueError(f"`outline[{idx}]` missing `type`.")
        seg_type = segment["type"].lower()
        if seg_type == "line":
            outline.append(Line(segment["start"], segment["end"]))
        elif seg_type == "arc":
            outline.append(
                Arc(
                    start_idx=segment["start"],
                    end_idx=segment["end"],
                    center_idx=segment["center"],
                    radius=float(segment["radius"]),
                    start_angle=float(segment["start_angle"]),
                    end_angle=float(segment["end_angle"]),
                )
            )
        else:
            raise ValueError(f"Unsupported segment type `{seg_type}`.")
    return outline


def _parse_furnitures(data: Any) -> Iterable[Furnish]:
    if not data:
        return []
    if not isinstance(data, list):
        raise ValueError("`furnitures` must be a list.")
    furnitures: List[Furnish] = []
    for idx, furn in enumerate(data):
        try:
            furnitures.append(
                Furnish(
                    name=furn.get("name", f"FURN-{idx}"),
                    type=furn["type"],
                    width=float(furn["width"]),
                    length=float(furn["length"]),
                    height=float(furn["height"]),
                    x=float(furn.get("x", 0.0)),
                    y=float(furn.get("y", 0.0)),
                    rotation=float(furn.get("rotation", 0.0)),
                    anchor=furn.get("anchor", "center"),
                )
            )
        except KeyError as exc:
            raise ValueError(f"Furniture entry {idx} missing {exc.args[0]!r}.") from exc
    return furnitures


async def room_from_upload(upload: UploadFile | None) -> Room | None:
    """Read + validate an uploaded JSON file and convert it to a Room."""
    if upload is None:
        return None
    try:
        raw = (await upload.read()).decode("utf-8")
    except Exception as exc:  # pragma: no cover - depends on Starlette internals
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unable to read uploaded file.") from exc

    try:
        payload: Dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid JSON: {exc.msg}") from exc

    try:
        points = _parse_points(payload["points"])
        outline = _parse_outline(payload["outline"])
        furnitures = _parse_furnitures(payload.get("furnitures"))
    except KeyError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Missing field: {exc.args[0]}") from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    return Room(points=points, outline=outline, furnitures=furnitures)
