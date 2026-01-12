from __future__ import annotations
from dataclasses import dataclass
from src.math import Vertex, Vector
from src.geometry.ray import Ray
from src.geometry.geometry_hit import GeometryHit
from src.geometry.hittable import Hittable


@dataclass
class Plane(Hittable):
    """
    Plane in 3D space defined by a point, normal, and color.
    """
    point: Vertex  # a point on the plane
    normal: Vector  # normal vector of the plane (should be normalized)

    def __post_init__(self):
        self.normal = self.normal.normalize_ip()

    def intersect(self, ray: Ray, t_min=0.001, t_max=float('inf')) -> GeometryHit | None:
        """
        Calculate intersection of ray with plane.
        :param ray: Ray to test intersection with
        :param t_min: minimum valid distance for intersection
        :param t_max: maximum valid distance for intersection
        :return: Hit record if intersection occurs, else None
        """
        denom = ray.direction.dot(self.normal)
        if abs(denom) < 1e-6:
            return None  # Ray is parallel to the plane

        t = (self.point - ray.origin).dot(self.normal) / denom
        if t < t_min or t > t_max:
            return None  # Intersection is out of bounds

        hit_point = ray.point_at(t)
        normal = self.normal
        if ray.direction.dot(normal) > 0.0:
            normal = -normal

        return GeometryHit(
            dist=t,
            point=hit_point,
            normal=normal,
            front_face=ray.direction.dot(normal) < 0.0,
        )

    def random_point(self) -> Vertex:
        import random
        d = random.uniform(-10, 10)
        u = Vector(1, 0, 0) if abs(self.normal.x) < 0.9 else Vector(0, 1, 0)
        v = self.normal.cross(u).normalize_ip()
        u = v.cross(self.normal).normalize_ip()
        return self.point + u * d + v * d

    def normal_at(self, point: Vertex) -> Vector:
        """
        Get the normal vector at a given point on the plane's surface.
        :param point: Point on the plane
        :return: Normal vector at that point
        """
        return self.normal
