from __future__ import annotations

from abc import ABC
from src.math import Vertex, Vector
from src.geometry.hittable import Hittable
from src.geometry.ray import Ray
from src.geometry.geometry_hit import GeometryHit
from src.material import Material
from .triangle import Triangle
import random


class Square(Hittable):
    """
    Square in 3D space defined by four vertices and material.
    The square is composed of two triangles for intersection calculations.
    """
    v0: Vertex
    v1: Vertex
    v2: Vertex
    v3: Vertex
    material: Material

    tri1: Triangle = None
    tri2: Triangle = None

    def __init__(self, vertex: Vertex, diagonal_vertex: Vertex, material: Material):
        self.v0 = vertex
        self.v2 = diagonal_vertex
        self.v1 = Vertex(diagonal_vertex.x, vertex.y, vertex.z)
        self.v3 = Vertex(vertex.x, diagonal_vertex.y, diagonal_vertex.z)
        self.material = material
        self.__post_init__()

    def __post_init__(self):
        # Create two triangles from the square's vertices
        self.tri1 = Triangle(self.v0, self.v1, self.v2, self.material)
        self.tri2 = Triangle(self.v0, self.v2, self.v3, self.material)

    def intersect(self, ray: Ray, t_min=0.001, t_max=float('inf')) -> GeometryHit | None:
        """
        Check intersection with both triangles composing the square.
        :param ray: Ray to test intersection with
        :param t_min: minimum valid distance for intersection
        :param t_max: maximum valid distance for intersection
        :return: Hit record if intersection occurs, else None
        """
        hit1 = self.tri1.intersect(ray, t_min, t_max)
        hit2 = self.tri2.intersect(ray, t_min, t_max)

        if hit1 and hit2:
            return hit1 if hit1.dist < hit2.dist else hit2
        return hit1 or hit2

    def compute_uv(self, point: Vertex) -> tuple[float, float]:
        """
        Compute UV coordinates for the given point on the square.
        :param point: Point on the square
        :return: Tuple of (u, v) coordinates
        """
        # Assuming the square is axis-aligned, compute UV based on vertex positions
        u = (point.x - self.v0.x) / (self.v2.x - self.v0.x)
        v = (point.y - self.v0.y) / (self.v2.y - self.v0.y)
        return u, v

    def compute_derivatives(self, point: Vertex) -> tuple[Vector, Vector]:
        """
        Compute the partial derivatives dpdu and dpdv at the given point on the square.
        :param point: Point on the square
        :return: Tuple of (dpdu, dpdv) vectors
        """
        # Assuming the square is axis-aligned, compute derivatives based on vertex positions
        dpdu = Vector(self.v1.x - self.v0.x, self.v1.y - self.v0.y, self.v1.z - self.v0.z)
        dpdv = Vector(self.v3.x - self.v0.x, self.v3.y - self.v0.y, self.v3.z - self.v0.z)
        return dpdu, dpdv


    def random_point(self) -> Vertex:
        u = random.uniform(0, 1)
        v = random.uniform(0, 1)
        if u + v > 1:
            u = 1 - u
            v = 1 - v
        point = self.v0 + (self.v1 - self.v0) * u + (self.v3 - self.v0) * v
        return point

    def normal_at(self, point: Vertex) -> Vector:
        # Normal is the same for both triangles
        return self.tri1.normal_at(point)
