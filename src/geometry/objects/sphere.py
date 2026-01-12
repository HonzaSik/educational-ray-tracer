from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from src.math import Vertex
from src.geometry.hittable import Hittable
from src.geometry.ray import Ray
from src.geometry.geometry_hit import GeometryHit
from src.math import Vector


@dataclass
class Sphere(Hittable):
    """
    Sphere in 3D space defined by center, radius, and color.
    """
    center: Vertex  # center of the sphere
    radius: float  # radius of the sphere

    # Ray-sphere intersection
    def intersect(self, ray: Ray, t_min=0.001, t_max=float('inf')) -> GeometryHit | None:
        """
        Calculate intersection of ray with sphere.
        :param ray: Ray to test intersection with
        :param t_min: minimum valid distance for intersection
        :param t_max: maximum valid distance for intersection
        :return: Hit record if intersection occurs, else None
        """
        oc = ray.origin - self.center  # Vector from oray origin to sphere center

        # Quadratic coefficients
        a = ray.direction.dot(ray.direction)  # Usually = 1 if ray.direction is normalized
        b = 2.0 * oc.dot(ray.direction)  # Projection of oc onto the ray
        c = oc.dot(oc) - self.radius * self.radius  # Distance^2 from ray origin to sphere surface

        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None  # no intersection - ray misses the sphere

        sqrt_disc = sqrt(discriminant)

        # Find the nearest root that lies in the acceptable range by calculating both roots using quadratic formula
        root = (-b - sqrt_disc) / (2.0 * a)
        if root < t_min or root > t_max:
            root = (-b + sqrt_disc) / (2.0 * a)
            if root < t_min or root > t_max:  # Point is out of range so no valid intersection
                return None

        # Calculate intersection in 3d space
        hit_point = ray.point_at(root)

        # Calculate normal at the intersection point for lighting calculations
        normal = self.normal_at(hit_point)
        if ray.direction.dot(normal) > 0.0:
            normal = -normal

        front_face = ray.direction.dot(normal) < 0.0

        return GeometryHit(
            dist=root,
            point=hit_point,
            normal=normal,
            front_face=front_face
        )

    def random_point(self) -> Vertex:
        """
        Generate a random point on the sphere's surface.
        :return: Vertex on the sphere surface
        """
        import random
        import math

        u = random.uniform(0, 1)
        v = random.uniform(0, 1)

        theta = 2 * math.pi * u  # azimuthal angle
        phi = math.acos(2 * v - 1)  # polar angle

        x = self.radius * math.sin(phi) * math.cos(theta)
        y = self.radius * math.sin(phi) * math.sin(theta)
        z = self.radius * math.cos(phi)

        return Vertex(self.center.x + x, self.center.y + y, self.center.z + z)

    def normal_at(self, point: Vertex) -> Vector:
        """
        Get the normal vector at a given point on the sphere's surface.
        :param point: Point on the sphere
        :return: Normal vector at that point
        """
        normal = (point - self.center) / self.radius
        return normal
