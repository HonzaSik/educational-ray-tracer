from __future__ import annotations
from abc import ABC, abstractmethod
from src.geometry.hit_point import HitPoint
from src.geometry.ray import Ray
from src.math import Vertex

class Hittable(ABC):
    """Anything that can be intersected by a ray."""
    @abstractmethod
    def intersect(self, ray: Ray, t_min: float = 1e-3, t_max: float = float('inf')) -> HitPoint | None:
        """Calculate intersection of ray with the object.
        :param ray: Ray to test intersection with
        :param t_min: minimum valid distance for intersection
        :param t_max: maximum valid distance for intersection
        :return: Hit record if intersection occurs, else None
        """
        pass

    @abstractmethod
    def random_point(self) -> Vertex:
        """Generate a random point on the surface of the object."""
        pass