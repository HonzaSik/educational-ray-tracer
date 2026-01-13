from __future__ import annotations
from abc import ABC, abstractmethod
from src.geometry.geometry_hit import GeometryHit
from src.geometry.ray import Ray
from src.math import Vertex


class ObjectGeometry(ABC):
    """Geometric object interface for ray tracing intersections"""

    @abstractmethod
    def intersect(self, ray: Ray, t_min: float = 1e-3, t_max: float = float('inf')) -> GeometryHit | None:
        """Calculate intersection of ray with the object.
        :param ray: Ray to test intersection with
        :param t_min: minimum valid distance for intersection
        :param t_max: maximum valid distance for intersection
        :return: Hit record if intersection occurs, else None
        """
        pass

    @abstractmethod
    def normal_at(self, point: Vertex) -> Vertex:
        """Get the normal vector at a given point on the object's surface."""
        pass
