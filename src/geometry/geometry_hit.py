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
    geometry_id: int | None = None

    def __post_init__(self):
        self.normal = self.normal.normalize()
        if self.geometry_id is None:
            self.geometry_id = id(self)
