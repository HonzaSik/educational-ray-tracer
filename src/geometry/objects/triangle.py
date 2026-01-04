from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from math import sqrt
from src.math import Vertex, Vector
from src.geometry.hittable import Hittable
from src.geometry.ray import Ray
from src.geometry.geometry_hit import GeometryHit
from src.material import Material
import random

@dataclass
class Triangle(Hittable, ABC):
    """
    Triangle in 3D space defined by three vertices and material.
    """
    v0: Vertex
    v1: Vertex
    v2: Vertex
    material: Material

    edge_1: Vector = None
    edge_2: Vector = None

    # Precompute edges for intersection calculations to optimize performance
    def __post_init__(self):
        self.edge_1 = self.v1 - self.v0
        self.edge_2 = self.v2 - self.v0


    def intersect(self, ray: Ray, t_min=0.001, t_max=float('inf')) -> GeometryHit | None:
        """
        Möller–Trumbore ray-triangle intersection algorithm implementation.
        :param ray: Ray to test intersection with
        :param t_min: minimum valid distance for intersection
        :param t_max: maximum valid distance for intersection
        :return: Hit record if intersection occurs, else None
        """

        # Calculate determinant and check if ray is parallel to triangle
        plane_vector = ray.direction.cross(self.edge_2)
        determinant = self.edge_1.dot(plane_vector)

        # If determinant is near zero, ray lies in plane of triangle or is parallel to it
        if abs(determinant) < 1e-8:
            return None

        inv_det = 1.0 / determinant

        # Calculate distance from v0 to ray origin
        vertex_to_origin = ray.origin - self.v0

        # Calculate u parameter and test bounds u stands u is the barycentric coordinate
        u = vertex_to_origin.dot(plane_vector) * inv_det

        if u < 0.0 or u > 1.0:
            return None

        # Prepare to test v parameter
        q_vector = vertex_to_origin.cross(self.edge_1)

        # Calculate v parameter and test bounds
        v = ray.direction.dot(q_vector) * inv_det
        if v < 0.0 or u + v > 1.0:
            return None

        # Calculate t to find intersection point along the ray
        t = self.edge_2.dot(q_vector) * inv_det
        if t < t_min or t > t_max:
            return None

        # Calculate intersection point in 3D space
        hit_point = ray.point_at(t)
        # Calculate normal using cross product of edges
        normal = self.edge_1.cross(self.edge_2).normalize_ip()
        if ray.direction.dot(normal) > 0.0:
            normal = -normal

        return GeometryHit(
            dist=t,
            point=hit_point,
            normal=normal,
            front_face=ray.direction.dot(normal) < 0.0,
        )


    def translate(self, offset: Vector) -> None:
        """
        Move triangle by offset vector.
        """
        self.v0 += offset
        self.v1 += offset
        self.v2 += offset
        self.__post_init__()


    def random_point(self) -> Vertex:
        u = random.uniform(0, 1)
        v = random.uniform(0, 1)
        if u + v > 1:
            u = 1 - u
            v = 1 - v
        point = self.v0 + (self.v1 - self.v0) * u + (self.v2 - self.v0) * v
        return point

    def normal_at(self, point: Vertex) -> Vector:
        """
        Get the normal vector at a given point on the triangle's surface.
        :param point: Point on the triangle
        :return: Normal vector at that point
        """
        normal = self.edge_1.cross(self.edge_2).normalize_ip()
        return normal