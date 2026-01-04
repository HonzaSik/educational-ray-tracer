from __future__ import annotations

from dataclasses import dataclass

from src.math import Vertex, Vector


@dataclass
class GeometryHit:
    """
    Record of a ray-object intersection.
    Stores intersection distance, point, normal, and color at thepoint.
    """
    dist: float  # distance from ray origin to intersection
    point: Vertex  # intersection point
    normal: Vector  # normal at intersection point
    front_face: bool
    uv: tuple[float, float] | None  # texture coordinates at intersection point
    dpdu: Vector | None  # partial derivative of position w.r.t u
    dpdv: Vector | None  # partial derivative of position w.r.t v
    geometry_id: int | None = None