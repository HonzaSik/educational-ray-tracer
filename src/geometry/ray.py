from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from src.math import Vertex, Vector, Vec3

def transform_point(matrix, point):
    """
    Transform a point using a 4x4 affine transformation matrix.
    :param matrix: 4x4 transformation matrix
    :param point: point to transform
    :return: transformed point
    """
    v = np.array([point.x, point.y, point.z, 1.0])
    r = matrix @ v
    return Vertex(float(r[0]), float(r[1]), float(r[2]))

def transform_vector(matrix, v):
    """
    Transform a vector using a 4x4 affine transformation matrix.
    :param matrix: 4x4 transformation matrix
    :param v: vector to transform
    :return: transformed vector
    """
    a = np.array([v.x, v.y, v.z, 0.0])
    r = matrix @ a
    return Vector(float(r[0]), float(r[1]), float(r[2]))

@dataclass
class Ray:
    """
    Ray in 3D space defined by an origin and a direction.
    Normalized direction vector ensures consistent behavior in intersection calculations.
    """
    origin: Vertex  # starting point of the ray
    direction: Vector | Vec3  # normalized direction vector

    def __post_init__(self):
        """
        Normalize the direction vector to ensure consistent behavior in intersection calculations.
        """
        self.direction = self.direction.normalize()

    def point_at(self, dist: float) -> Vertex:
        """
        Calculate point along the ray at distance dist from the origin.
        :param dist: distance from the ray origin
        :return: point at that distance
        """
        return self.origin + self.direction * dist

    def transformed(self, matrix: np.ndarray) -> Ray:
        """
        Transform the ray by applying the given affine transformation matrix to both the origin and direction.
        :param matrix: 4x4 transformation matrix
        :return: new Ray instance with transformed origin and direction
        """
        new_origin = transform_point(matrix, self.origin)
        new_dir = transform_vector(matrix, self.direction)

        return Ray(new_origin, new_dir)