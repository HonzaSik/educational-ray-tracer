from __future__ import annotations
from dataclasses import dataclass
from math import sqrt

from numpy import atan2, pi

from src.math import Vertex
from src.geometry.hittable import Hittable
from src.geometry.ray import Ray
from src.geometry.geometry_hit import GeometryHit
from src.material import Material
from src.math import Vector
from numba import njit

@dataclass
class Cylinder(Hittable):
    base_point: Vertex  # Center of the cylinder base
    cap_point: Vertex  # Center of the cylinder cap
    radius: float  # Radius of the cylinder
    material: Material  # Material properties

    def normal_at(self, point: Vertex) -> Vector:
        # Vector along the cylinder axis
        axis = self.cap_point - self.base_point
        axis_length_squared = axis.dot(axis)
        axis_normalized = axis / sqrt(axis_length_squared)

        # Vector from base point to the given point
        delta_p = point - self.base_point

        # Project delta_p onto the cylinder axis to find the closest point on the axis
        projection_length = delta_p.dot(axis_normalized)
        closest_point_on_axis = self.base_point + projection_length * axis_normalized

        # Normal is the vector from the closest point on the axis to the point, normalized
        normal = (point - closest_point_on_axis).normalize()
        return normal

    def _compute_uv(self, point: Vertex) -> tuple[float, float]:
        # axis and its length
        axis = self.cap_point - self.base_point
        axis_length = sqrt(axis.dot(axis))
        axis_normalized = axis / axis_length

        # vector from base to point
        rel = point - self.base_point

        # height along axis (0..axis_length)
        h = rel.dot(axis_normalized)

        # closest point on axis, radial direction
        closest_point_on_axis = self.base_point + h * axis_normalized
        radial = (point - closest_point_on_axis).normalize()

        # build an orthonormal basis around the axis
        # pick any reference not parallel to axis
        if abs(axis_normalized.x) > 0.9:
            ref = Vector(0, 1, 0)
        else:
            ref = Vector(1, 0, 0)

        tangent0 = axis_normalized.cross(ref).normalize()
        tangent1 = axis_normalized.cross(tangent0).normalize()

        # coordinates of radial in this basis
        x = radial.dot(tangent0)
        y = radial.dot(tangent1)

        # angle in [-pi, pi]
        theta = atan2(y, x)

        # wrap to [0,1]
        u = (theta / (2.0 * pi)) % 1.0

        # v = 0 at base, 1 at cap
        v = h / axis_length

        return u, v

    def intersect(self, ray: Ray, t_min=0.001, t_max=float('inf')) -> GeometryHit | None:
        # Vector along the cylinder axis
        axis = self.cap_point - self.base_point
        axis_length_squared = axis.dot(axis)
        axis_normalized = axis / sqrt(axis_length_squared)

        # Vector from base point to ray origin
        delta_p = ray.origin - self.base_point

        # Components for the quadratic equation
        d = ray.direction - (ray.direction.dot(axis_normalized)) * axis_normalized
        dp = delta_p - (delta_p.dot(axis_normalized)) * axis_normalized

        a = d.dot(d)
        b = 2 * d.dot(dp)
        c = dp.dot(dp) - self.radius * self.radius

        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None  # No intersection

        sqrt_disc = sqrt(discriminant)

        # Find the nearest root that lies in the acceptable range
        root = (-b - sqrt_disc) / (2.0 * a)
        if root < t_min or root > t_max:
            root = (-b + sqrt_disc) / (2.0 * a)
            if root < t_min or root > t_max:
                return None

        # Calculate intersection point
        hit_point = ray.point_at(root)

        # Check caps
        projection_length = (hit_point - self.base_point).dot(axis_normalized)
        if projection_length < 0 or projection_length > sqrt(axis_length_squared):
            return None

        # Normal
        normal = self.normal_at(hit_point)
        if ray.direction.dot(normal) > 0.0:
            normal = -normal

        # UV
        u, v = self._compute_uv(hit_point)

        return GeometryHit(
            dist=root,
            point=hit_point,
            normal=normal,
            uv=(u, v),
            ray_dir=ray.direction,
        )


    def random_point(self) -> Vertex:
        raise NotImplementedError("Random point generation not implemented for Cylinder.")