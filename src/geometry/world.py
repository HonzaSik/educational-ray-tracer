from __future__ import annotations
from abc import ABC
from typing import  Iterable
from src.geometry.hittable import Hittable
from .ray import Ray
from .hit_point import HitPoint


class World(Hittable, ABC):
    """
    Container for all objects in the scene. Supports ray intersection with all objects.
    objects: list of Sphere, Plane, Mesh
    """
    def __init__(self, objects: Iterable[Hittable] = ()):
        self.objects: list[Hittable] = list(objects)

    def add(self, obj: Hittable) -> None:
        self.objects.append(obj)

    def remove(self, obj: Hittable) -> None:
        self.objects.remove(obj)

    def intersect(self, ray: Ray, t_min: float = 1e-3, t_max: float = float('inf')) -> HitPoint | None:
        closest = t_max
        hit_best: HitPoint | None = None
        for obj in self.objects:
            h = obj.intersect(ray, t_min, closest)
            if h is None:
                continue
            if h and h.dist < closest:
                closest = h.dist
                hit_best = h
        return hit_best

    def hit(self, ray: Ray, t_min: float = 1e-3, t_max: float = float('inf')) -> HitPoint | None:
        return self.intersect(ray, t_min, t_max)
