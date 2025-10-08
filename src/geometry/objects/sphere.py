from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from src.math import Vertex
from src.geometry.hittable import Hittable
from src.geometry.ray import Ray
from src.geometry.hit_point import HitPoint
from src.material import Material


@dataclass
class Sphere(Hittable):
    """
    Sphere in 3D space defined by center, radius, and color.
    """
    center: Vertex # center of the sphere
    radius: float # radius of the sphere
    material: Material # material properties
    # default reflectivity is 0 (matte)

    # Ray-sphere intersection
    def intersect(self, ray: Ray, t_min=0.001, t_max=float('inf')) -> HitPoint | None:
        """
        Calculate intersection of ray with sphere.
        :param ray: Ray to test intersection with
        :param t_min: minimum valid distance for intersection
        :param t_max: maximum valid distance for intersection
        :return: Hit record if intersection occurs, else None
        """
        oc = ray.origin - self.center   # Vector from oray origin to sphere center

        # Quadratic coefficients
        a = ray.direction.dot(ray.direction) # Usually = 1 if ray.direction is normalized
        b = 2.0 * oc.dot(ray.direction) # Projection of oc onto the ray
        c = oc.dot(oc) - self.radius * self.radius # Distance^2 from ray origin to sphere surface

        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None # no intersection - ray misses the sphere

        sqrt_disc = sqrt(discriminant)

        # Find the nearest root that lies in the acceptable range by calculating both roots using quadratic formula
        root = (-b - sqrt_disc) / (2.0 * a)
        if root < t_min or root > t_max:
            root = (-b + sqrt_disc) / (2.0 * a)
            if root < t_min or root > t_max: # Point is out of range so no valid intersection
                return None

        # Calculate intersection in 3d space
        hit_point = ray.point_at(root)

        # Calculate normal at the intersection point for lighting calculations
        normal = (hit_point - self.center) / self.radius
        if ray.direction.dot(normal) > 0.0:
            normal = -normal

        return HitPoint(dist=root, point=hit_point, normal=normal, material=self.material, ray_dir=ray.direction)