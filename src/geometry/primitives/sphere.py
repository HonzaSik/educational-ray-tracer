from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt
from src.math import Vertex
from src.geometry.primitive import Primitive
from src.geometry.ray import Ray
from src.geometry.geometry_hit import GeometryHit
from src.math import Vector


@dataclass
class Sphere(Primitive):
    """
    Sphere in 3D space defined by center, radius, and color. Centered at the origin by default with radius 0.5.
    """
    center: Vertex = field(default_factory=lambda: Vertex(0, 0, 0))
    radius: float = field(default=1)

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
        c = oc.dot(oc) - self.radius * self.radius  # Sphere quadratic coefficient c

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

    def normal_at(self, point: Vertex) -> Vector:
        """
        Get the normal vector at a given point on the sphere's surface.
        :param point: Point on the sphere
        :return: Normal vector at that point
        """
        normal = (point - self.center) / self.radius
        return normal
