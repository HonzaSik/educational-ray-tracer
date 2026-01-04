from __future__ import annotations
from abc import ABC, abstractmethod
from src.material.color import Color
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.light import Light
from src.math import Vector

class ShadingModel(ABC):
    @abstractmethod
    def shade(self, hit: SurfaceInteraction, light: Light, view_dir: Vector) -> Color:
        ...

    @abstractmethod
    def shade_multiple_lights(self, hit: SurfaceInteraction, lights: list[Light], view_dir: Vector) -> Color:
        ...