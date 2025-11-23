"""
geom_core.py — Abstract Geometric Primitives

Core goals:
- Single source of truth for coordinates via a discrete grid (fixed-point integers).
- Global PointRegistry: deduplicated, reference-counted discrete points, addressed by stable IDs.
- Abstract geometry built on top of PointID references (no free-floating floats).
- Clean, extensible API (no third-party deps).

Units & precision:
- Base unit = micrometers (µm) as integers to avoid floating-point drift.
- GRID_STEP defines the snapping grid in µm (e.g., 1_000 = 1 mm).

This file defines:
- Config / units utilities
- PointRegistry (PointKey, PointRec)
- Basic references: LevelRef, AxisRef (optional orientation meta)
- Primitives: PointID, Segment (LineSegment, ArcSegment), Polyline
- Validation helpers
- Simple length/area where applicable (2D on XY plane)

Note: Z is discrete as well; for 2D profiles use z = level.elevation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional, Iterable
import math
import uuid

# =========================
# Configuration / Units
# =========================

# 1 m = 1_000_000 µm
UNIT_PER_M = 1_000_000
# Snap step in µm (e.g., 1_000 µm = 1 mm)
GRID_STEP = 1_000
# Tolerance used for snapping decision
TOL = GRID_STEP // 2

# =========================
# Fixed-point helpers
# =========================

def m_to_um(x_m: float) -> int:
    """Meters -> integer micrometers."""
    return round(x_m * UNIT_PER_M)


def um_to_m(x_um: int) -> float:
    """Micrometers int -> meters float (for display/export only)."""
    return x_um / UNIT_PER_M


def snap_um(v: int) -> int:
    """Snap an integer micrometer value to nearest GRID_STEP multiple."""
    r = v % GRID_STEP
    if r >= TOL:
        return v + (GRID_STEP - r)
    return v - r


# =========================
# Registry core
# =========================

@dataclass(frozen=True)
class PointKey:
    ix: int  # index along X grid (unit: GRID_STEP)
    iy: int  # index along Y grid (unit: GRID_STEP)
    iz: int  # index along Z grid (unit: GRID_STEP)

    @property
    def as_um(self) -> Tuple[int, int, int]:
        return (self.ix * GRID_STEP, self.iy * GRID_STEP, self.iz * GRID_STEP)


@dataclass
class PointRecord:
    id: str
    key: PointKey
    refcount: int = 0


class PointRegistry:
    """Global registry for discrete points.

    - Deduplicates by (ix, iy, iz)
    - Returns stable PointIDs
    - Tracks reference counts
    """

    def __init__(self) -> None:
        self._key2id: Dict[PointKey, str] = {}
        self._id2rec: Dict[str, PointRecord] = {}

    # ---- acquisition ----
    def _key_from_um(self, x_um: int, y_um: int, z_um: int) -> PointKey:
        return PointKey(
            ix=snap_um(x_um) // GRID_STEP,
            iy=snap_um(y_um) // GRID_STEP,
            iz=snap_um(z_um) // GRID_STEP,
        )

    def acquire_um(self, x_um: int, y_um: int, z_um: int) -> "PointID":
        """Acquire by integer micrometers (will still be snapped)."""
        key = self._key_from_um(x_um, y_um, z_um)
        pid = self._key2id.get(key)
        if pid is None:
            pid = str(uuid.uuid4())
            rec = PointRecord(id=pid, key=key, refcount=1)
            self._key2id[key] = pid
            self._id2rec[pid] = rec
        else:
            self._id2rec[pid].refcount += 1
        return PointID(pid)

    def acquire_m(self, x_m: float, y_m: float, z_m: float) -> "PointID":
        return self.acquire_um(m_to_um(x_m), m_to_um(y_m), m_to_um(z_m))

    def acquire_tuple_m(self, xyz_m: Tuple[float, float, float]) -> "PointID":
        x, y, z = xyz_m
        return self.acquire_m(x, y, z)

    # ---- release ----
    def release(self, pid: "PointID") -> None:
        rec = self._id2rec.get(pid.id)
        if not rec:
            return
        rec.refcount -= 1
        if rec.refcount <= 0:
            del self._id2rec[pid.id]
            del self._key2id[rec.key]

    # ---- getters ----
    def get_key(self, pid: "PointID") -> PointKey:
        rec = self._id2rec[pid.id]
        return rec.key

    def get_um(self, pid: "PointID") -> Tuple[int, int, int]:
        return self.get_key(pid).as_um

    def get_m(self, pid: "PointID") -> Tuple[float, float, float]:
        x, y, z = self.get_um(pid)
        return (um_to_m(x), um_to_m(y), um_to_m(z))


# =========================
# References (Levels / Axes)
# =========================

@dataclass
class LevelRef:
    name: str
    elevation_um: int  # discrete Z in µm

    @classmethod
    def from_m(cls, name: str, elevation_m: float) -> "LevelRef":
        return cls(name=name, elevation_um=snap_um(m_to_um(elevation_m)))


@dataclass
class AxisRef:
    """Optional orientation meta for axes.

    direction: unit vector in XY plane (float for direction only);
    this does not affect discrete storage but is useful for alignment/snap rules.
    """
    name: str
    dx: float  # unit dir X
    dy: float  # unit dir Y

    def normalized(self) -> "AxisRef":
        l = math.hypot(self.dx, self.dy)
        if l == 0:
            return AxisRef(self.name, 1.0, 0.0)
        return AxisRef(self.name, self.dx / l, self.dy / l)


# =========================
# Geometry primitives
# =========================

@dataclass(frozen=True)
class PointID:
    id: str


@dataclass
class Segment:
    """Abstract base for segments."""
    def length_um(self, reg: PointRegistry) -> int:
        raise NotImplementedError


@dataclass
class LineSegment(Segment):
    p0: PointID
    p1: PointID

    def length_um(self, reg: PointRegistry) -> int:
        x0, y0, _ = reg.get_um(self.p0)
        x1, y1, _ = reg.get_um(self.p1)
        dx = x1 - x0
        dy = y1 - y0
        return int(round(math.hypot(dx, dy)))


@dataclass
class ArcSegment(Segment):
    """Circular arc defined by 3 points or by (center,radius) + sweep.

    Here we store by 3 control points (p0, pm, p1) for simplicity,
    which uniquely defines a circle (except degenerate cases).
    Length uses planar arc length formula.
    """
    p0: PointID
    pm: PointID
    p1: PointID

    def _circle_params(self, reg: PointRegistry) -> Tuple[Tuple[float, float], float, float]:
        # returns (center(x,y), radius, sweep_angle in radians, signed)
        (x0, y0, _), (xm, ym, _), (x1, y1, _) = reg.get_um(self.p0), reg.get_um(self.pm), reg.get_um(self.p1)
        # Convert to float in µm for calculations
        x0, y0, xm, ym, x1, y1 = map(float, (x0, y0, xm, ym, x1, y1))
        # Compute circumcenter using perpendicular bisectors
        def det(ax, ay, bx, by):
            return ax * by - ay * bx
        d = 2 * det((xm - x0), (ym - y0), (x1 - x0), (y1 - y0))
        if abs(d) < 1e-9:
            # Degenerate (collinear); treat as line
            cx = cy = float('nan')
            r = float('inf')
            sweep = 0.0
            return (cx, cy), r, sweep
        ux = (
            ((xm - x0) * (xm + x0) + (ym - y0) * (ym + y0)) / 2
            )
        vx = (
            ((x1 - x0) * (x1 + x0) + (y1 - y0) * (y1 + y0)) / 2
            )
        cx = det(ux, (ym - y0), vx, (y1 - y0)) / d
        cy = det((xm - x0), ux, (x1 - x0), vx) / d
        r = math.hypot(x0 - cx, y0 - cy)
        # angles
        a0 = math.atan2(y0 - cy, x0 - cx)
        am = math.atan2(ym - cy, xm - cx)
        a1 = math.atan2(y1 - cy, x1 - cx)
        # choose sweep direction (through pm)
        def ang_diff(a, b):
            t = (b - a) % (2 * math.pi)
            if t > math.pi:
                t -= 2 * math.pi
            return t
        sweep0_1 = ang_diff(a0, a1)
        sweep0_m = ang_diff(a0, am)
        # if am lies between a0->a1 along sweep0_1, keep; else flip
        if abs(sweep0_1) < 1e-9:
            sweep = 0.0
        else:
            cond = (sweep0_1 > 0 and 0 < sweep0_m < sweep0_1) or (sweep0_1 < 0 and 0 > sweep0_m > sweep0_1)
            sweep = sweep0_1 if cond else (-math.copysign(1.0, sweep0_1) * (2 * math.pi - abs(sweep0_1)))
        return (cx, cy), r, sweep

    def length_um(self, reg: PointRegistry) -> int:
        (_, _), r, sweep = self._circle_params(reg)
        if not math.isfinite(r) or abs(sweep) < 1e-12:
            # fallback to chord length
            return LineSegment(self.p0, self.p1).length_um(reg)
        return int(round(abs(r * sweep)))


@dataclass
class Polyline:
    segments: List[Segment] = field(default_factory=list)
    closed: bool = False

    @classmethod
    def from_points(cls, pts: List[PointID], closed: bool = False) -> "Polyline":
        if len(pts) < 2:
            raise ValueError("Polyline requires at least 2 points")
        segs: List[Segment] = []
        for i in range(len(pts) - 1):
            segs.append(LineSegment(pts[i], pts[i + 1]))
        if closed:
            segs.append(LineSegment(pts[-1], pts[0]))
        return cls(segs, closed)

    def is_valid(self, reg: PointRegistry) -> bool:
        # Basic checks: non-zero segments, no exact duplicate consecutive points
        for s in self.segments:
            if isinstance(s, LineSegment):
                if reg.get_key(s.p0) == reg.get_key(s.p1):
                    return False
        return True

    def length_um(self, reg: PointRegistry) -> int:
        return sum(s.length_um(reg) for s in self.segments)

    def vertices(self) -> Iterable[PointID]:
        if not self.segments:
            return []
        yielded: List[str] = []
        for i, s in enumerate(self.segments):
            if isinstance(s, LineSegment):
                if i == 0:
                    yielded.append(s.p0.id)
                    yield s.p0
                yielded.append(s.p1.id)
                yield s.p1
            else:
                # For arc, yield endpoints (pm is internal, not a corner in a polyline sense)
                if i == 0:
                    yielded.append(s.p0.id)
                    yield s.p0
                if s.p1.id not in yielded:
                    yielded.append(s.p1.id)
                    yield s.p1

    # TODO: add plan_area for closed, non-self-intersecting polylines (shoelace on sampled segments)


# =========================
# Validation utilities (2D plan)
# =========================

def polyline_self_intersects(poly: Polyline, reg: PointRegistry) -> bool:
    """Check naive self-intersection for line-only polylines (O(n^2)).
    Arcs are not handled here (extend later as needed).
    """
    lines: List[LineSegment] = [s for s in poly.segments if isinstance(s, LineSegment)]
    def seg_points(ls: LineSegment) -> Tuple[Tuple[int,int], Tuple[int,int]]:
        x0, y0, _ = reg.get_um(ls.p0)
        x1, y1, _ = reg.get_um(ls.p1)
        return (x0, y0), (x1, y1)

    def ccw(a,b,c):
        return (c[1]-a[1])*(b[0]-a[0]) > (b[1]-a[1])*(c[0]-a[0])

    def intersect(a,b,c,d):
        return ccw(a,c,d) != ccw(b,c,d) and ccw(a,b,c) != ccw(a,b,d)

    n = len(lines)
    for i in range(n):
        for j in range(i+1, n):
            # skip neighboring segments sharing a vertex
            if i+1 == j:
                continue
            if poly.closed and i == 0 and j == n-1:
                continue
            a0,a1 = seg_points(lines[i])
            b0,b1 = seg_points(lines[j])
            if intersect(a0,a1,b0,b1):
                return True
    return False


# =========================
# Example usage (manual test)
# =========================
if __name__ == "__main__":
    reg = PointRegistry()
    # Create a rectangle 3m x 2m at z=0
    p0 = reg.acquire_m(0.0, 0.0, 0.0)
    p1 = reg.acquire_m(3.0, 0.0, 0.0)
    p2 = reg.acquire_m(3.0, 2.0, 0.0)
    p3 = reg.acquire_m(0.0, 2.0, 0.0)

    poly = Polyline.from_points([p0, p1, p2, p3], closed=True)
    assert poly.is_valid(reg)
    assert not polyline_self_intersects(poly, reg)

    length_um = poly.length_um(reg)
    print("Perimeter (m):", um_to_m(length_um))

    # Level & Axis examples
    L0 = LevelRef.from_m("Level 0", 0.0)
    X = AxisRef("X", 1.0, 0.0).normalized()
    Y = AxisRef("Y", 0.0, 1.0).normalized()

    print("Level 0 elevation (m):", um_to_m(L0.elevation_um))
    print("Axis X:", X.dx, X.dy)
