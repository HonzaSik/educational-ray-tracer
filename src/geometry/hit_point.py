from __future__ import annotations
from dataclasses import dataclass
from src.math import Vertex, Vector
from src.material import Material

@dataclass
class HitPoint:

    """
    Record of a ray-object intersection.
    Stores intersection distance, point, normal, and color at thepoint.
    """
    dist: float # distance from ray origin to intersection
    point: Vertex # intersection point
    normal: Vector # normal at intersection point
    ray_dir: Vector # direction of the incoming ray
    material: Material # material properties