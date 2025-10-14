from __future__ import annotations
from dataclasses import dataclass
from src.math import Vertex, Vector
from src.material import Material
from src.geometry.ray import Ray
from src.geometry.hit_point import HitPoint
from src.geometry.hittable import Hittable

@dataclass
class Plane(Hittable):
    """
    Plane in 3D space defined by a point, normal, and color.
    """
    point: Vertex # a point on the plane
    normal: Vector      # normal vector of the plane (should be normalized)
    material: Material # material properties

    def __post_init__(self):
        self.normal = self.normal.normalize()

    def intersect(self, ray: Ray, t_min=0.001, t_max=float('inf')) -> HitPoint | None:
        """
        Calculate intersection of ray with plane.
        :param ray: Ray to test intersection with
        :param t_min: minimum valid distance for intersection
        :param t_max: maximum valid distance for intersection
        :return: Hit record if intersection occurs, else None
        """
        denom = ray.direction.dot(self.normal)
        if abs(denom) < 1e-6:
            return None # Ray is parallel to the plane

        t = (self.point - ray.origin).dot(self.normal) / denom
        if t < t_min or t > t_max:
            return None # Intersection is out of bounds

        hit_point = ray.point_at(t)
        normal = self.normal
        if ray.direction.dot(normal) > 0.0:
            normal = -normal

        return HitPoint(dist=t, point=hit_point, normal=normal, material=self.material, ray_dir=ray.direction)