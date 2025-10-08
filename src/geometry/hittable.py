from __future__ import annotations
from abc import ABC, abstractmethod
from src.geometry.hit_point import HitPoint
from src.geometry.ray import Ray

class Hittable(ABC):
    """Anything that can be intersected by a ray."""
    @abstractmethod
    def intersect(self, ray: Ray, t_min: float = 1e-3, t_max: float = float('inf')) -> HitPoint | None:
        ...