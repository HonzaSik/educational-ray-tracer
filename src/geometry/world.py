from __future__ import annotations
from abc import ABC
from typing import  Iterable
from src.geometry.hittable import Hittable
from .ray import Ray
from .hit_point import HitPoint
from src.math import Vertex
from src.math.vector import Vector


class World(Hittable):
    """
    Container for all objects in the scene. Supports ray intersection with all objects.
    objects: list of Sphere, Plane, Mesh
    """
    def __init__(self, objects: Iterable[Hittable] = ()):
        self.objects: list[Hittable] = list(objects)

    def add(self, *objs: Hittable) -> None:
        """Add an object or more objects to the world."""
        self.objects.extend(objs)

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

    def emitters(self) -> Iterable[Hittable]:
        for obj in self.objects:
            material = getattr(obj, "material", None)
            if material and getattr(material, "emission", None):
                yield obj

    def random_point(self) -> Vertex:
        import random
        obj = random.choice(self.objects)
        return obj.random_point()


    def normal_at(self, point: Vertex, debug: bool = False) -> Vector:
        """
        Approximate the normal of the object nearest to a given world-space point.
        Used for educational shaders (curvature, flow fields, etc.).
        """
        closest_dist = float("inf")
        closest_normal = Vector(0, 1, 0)

        for obj in self.objects:
            if not hasattr(obj, "normal_at"):
                continue

            try:
                n = obj.normal_at(point)
            except (AttributeError, TypeError) as e:
                if debug:
                    print(f"[World.normal_at] Skipping {obj}: {e}")
                continue


            dist = 0.0
            if hasattr(obj, "center"):
                dist = (point - obj.center).norm()
            elif hasattr(obj, "position"):
                dist = (point - obj.position).norm()

            if dist < closest_dist and n is not None:
                closest_dist = dist
                closest_normal = n

        return closest_normal.normalize()
