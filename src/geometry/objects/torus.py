from __future__ import annotations
from src.math import Vertex, Vector
from src.geometry.object_geometry import ObjectGeometry
from src.geometry.ray import Ray
from src.geometry.geometry_hit import GeometryHit
import random
import numpy as np
from dataclasses import dataclass


@dataclass
class Torus(ObjectGeometry):
    """
    A torus object. Donut shape defined by a major radius (distance from center to tube center) and a minor radius (tube radius). Uses as example of custom Hittable implementation. in jupyter notebook.
    The torus is centered at 'center' vertex and l
    """
    center: Vertex
    radius_major: float  # Major radius (distance from center to tube center)
    radius_tube: float  # Minor radius (tube radius)

    def normal_at(self, point: Vertex) -> Vector:
        local_hit = point - self.center
        nx = 4 * local_hit.x * (
                local_hit.x ** 2 + local_hit.y ** 2 + local_hit.z ** 2 - self.radius_major ** 2 - self.radius_tube ** 2)
        ny = 4 * local_hit.y * (
                local_hit.x ** 2 + local_hit.y ** 2 + local_hit.z ** 2 - self.radius_major ** 2 - self.radius_tube ** 2) + 8 * self.radius_major ** 2 * local_hit.y
        nz = 4 * local_hit.z * (
                local_hit.x ** 2 + local_hit.y ** 2 + local_hit.z ** 2 - self.radius_major ** 2 - self.radius_tube ** 2)
        return Vector(nx, ny, nz).normalize()

    def intersect(self, ray: Ray, t_min=1e-3, t_max=float('inf')) -> GeometryHit | None:
        ray_origin = ray.origin - self.center
        rd = ray.direction

        # coefficients for quartic equation
        ox, oy, oz = ray_origin.x, ray_origin.y, ray_origin.z
        dx, dy, dz = rd.x, rd.y, rd.z

        sum_d_sq = dx * dx + dy * dy + dz * dz
        e = ox * ox + oy * oy + oz * oz - self.radius_major * self.radius_major - self.radius_tube * self.radius_tube
        f = ox * dx + oy * dy + oz * dz
        four_R2 = 4.0 * self.radius_major * self.radius_major

        coeffs = [
            sum_d_sq * sum_d_sq,
            4.0 * sum_d_sq * f,
            2.0 * sum_d_sq * e + 4.0 * f * f + four_R2 * dy * dy,
            4.0 * f * e + 2.0 * four_R2 * oy * dy,
            e * e - four_R2 * (self.radius_tube * self.radius_tube - oy * oy)
        ]

        roots = np.roots(coeffs)
        roots = np.real(roots[np.isreal(roots)])
        roots = [r for r in roots if t_min < r < t_max]

        if not roots:
            return None

        t = min(roots)
        hit_point = ray.point_at(t)

        normal = self.normal_at(hit_point)

        return GeometryHit(
            point=hit_point,
            normal=normal,
            dist=t,
            front_face=ray.direction.dot(normal) < 0.0,
        )

    def random_point(self) -> Vertex:
        u = random.uniform(0, 2 * np.pi)
        v = random.uniform(0, 2 * np.pi)

        x = (self.radius_major + self.radius_tube * np.cos(v)) * np.cos(u)
        y = (self.radius_major + self.radius_tube * np.cos(v)) * np.sin(u)
        z = self.radius_tube * np.sin(v)

        return Vertex(x, y, z) + self.center
