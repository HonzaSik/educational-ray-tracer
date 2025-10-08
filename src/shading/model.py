from __future__ import annotations
from abc import ABC, abstractmethod
from src.material.color import Color
from src.geometry.hit_point import HitPoint
from src.geometry.world import World
from src.scene.light import Light
from src.math import Vector

class ShadingModel(ABC):
    @abstractmethod
    def shade(self, hit: HitPoint, world: World, light: Light, view_dir: Vector) -> Color:
        ...

    @abstractmethod
    def shade_multiple_lights(self, hit: HitPoint, world: World, lights: list[Light], view_dir: Vector) -> Color:
        ...