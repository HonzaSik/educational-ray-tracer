from __future__ import annotations
from dataclasses import dataclass
from src.math import Vertex, Vector
from src.geometry.primitive import Primitive
from src.geometry.ray import Ray
from src.geometry.geometry_hit import GeometryHit

EPS = 1e-6

@dataclass
class Box(Primitive):
    corner1: Vertex
    corner2: Vertex

    @property
    def x0(self):
        return min(self.corner1.x, self.corner2.x)

    @property
    def x1(self):
        return max(self.corner1.x, self.corner2.x)

    @property
    def y0(self):
        return min(self.corner1.y, self.corner2.y)

    @property
    def y1(self):
        return max(self.corner1.y, self.corner2.y)

    @property
    def z0(self):
        return min(self.corner1.z, self.corner2.z)

    @property
    def z1(self):
        return max(self.corner1.z, self.corner2.z)

    def normal_at(self, point: Vertex) -> Vector:
        if abs(point.x - self.x0) < EPS:
            return Vector(-1, 0, 0)  # left
        if abs(point.x - self.x1) < EPS:
            return Vector(1, 0, 0)  # right
        if abs(point.y - self.y0) < EPS:
            return Vector(0, -1, 0)  # bottom
        if abs(point.y - self.y1) < EPS:
            return Vector(0, 1, 0)  # top
        if abs(point.z - self.z0) < EPS:
            return Vector(0, 0, -1)  # back
        if abs(point.z - self.z1) < EPS:
            return Vector(0, 0, 1)  # front
        raise ValueError("Point is not on the surface of the box.")

    def intersect(self, ray: Ray, t_min=0.001, t_max=float('inf')) -> GeometryHit | None:
        if abs(ray.direction.x) < EPS:
            if ray.origin.x < self.x0 or ray.origin.x > self.x1:
                return None
        if abs(ray.direction.y) < EPS:
            if ray.origin.y < self.y0 or ray.origin.y > self.y1:
                return None
        if abs(ray.direction.z) < EPS:
            if ray.origin.z < self.z0 or ray.origin.z > self.z1:
                return None

        tx0 = (self.x0 - ray.origin.x) / ray.direction.x
        tx1 = (self.x1 - ray.origin.x) / ray.direction.x
        tmin = min(tx0, tx1)
        tmax = max(tx0, tx1)

        ty0 = (self.y0 - ray.origin.y) / ray.direction.y
        ty1 = (self.y1 - ray.origin.y) / ray.direction.y
        tmin = max(tmin, min(ty0, ty1))
        tmax = min(tmax, max(ty0, ty1))

        tz0 = (self.z0 - ray.origin.z) / ray.direction.z
        tz1 = (self.z1 - ray.origin.z) / ray.direction.z
        tmin = max(tmin, min(tz0, tz1))
        tmax = min(tmax, max(tz0, tz1))

        if tmax < max(tmin, t_min) or tmin > t_max:
            return None

        t_hit = tmin if tmin >= t_min else tmax
        hit_point = ray.point_at(t_hit)

        # Face normal
        normal = self.normal_at(hit_point)

        # Flip to face the ray
        if ray.direction.dot(normal) > 0.0:
            normal = -normal
            front_face = False
        else:
            front_face = True

        return GeometryHit(
            dist=t_hit,
            point=hit_point,
            normal=normal,
            front_face=front_face,
        )

    def random_point(self) -> Vertex:
        raise NotImplementedError("Random point generation not implemented for Box.")
