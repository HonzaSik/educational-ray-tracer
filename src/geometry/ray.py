from __future__ import annotations
from dataclasses import dataclass
from src.math import Vertex, Vector, Vec3


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
