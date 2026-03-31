from __future__ import annotations
from dataclasses import dataclass
from src.math import Vertex, Vector


@dataclass
class GeometryHit:
    """
    Record of a ray-object intersection.
    Contains basic information about the hit, such as the distance from the ray origin to the hit point, the hit point itself, the surface normal at the hit point, and whether the ray hit the front face of the surface.
    Optionally includes a geometry_id to identify which object was hit.
    """
    dist: float
    point: Vertex
    normal: Vector
    front_face: bool
    geometry_id: int | None = None # not used for now but can be helpful for debugging or future features like material properties and speed optimizations

    def __post_init__(self):
        self.normal = self.normal.normalize()
        if self.geometry_id is None:
            self.geometry_id = id(self)
