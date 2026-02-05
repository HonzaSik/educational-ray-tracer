from __future__ import annotations
from dataclasses import dataclass
from src.math import Vertex, Vector


@dataclass
class GeometryHit:
    """
    Record of a ray-object intersection.
    """
    dist: float
    point: Vertex
    normal: Vector
    front_face: bool
    geometry_id: int | None = None

    def __post_init__(self):
        self.normal = self.normal.normalize()
        if self.geometry_id is None:
            self.geometry_id = id(self)
