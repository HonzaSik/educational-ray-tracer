# src/shading/normal_shader.py
from __future__ import annotations
from typing import Literal
from .shading_model import ShadingModel
from src.geometry.hit_point import HitPoint
from src.geometry.world import World
from src.scene.light import Light
from src.material.color import Color
from src.math import Vector
from dataclasses import dataclass

@dataclass
class DepthShader(ShadingModel):
    """
    Simple object shader for visualizing depth from the camera.
    """

    def shade(self, hit: HitPoint, world: World, light: Light| None, view_dir: Vector) -> Color:
        """
        Shade based on the depth from the camera.
        Maps depth to a grayscale value, with closer points being lighter.
        """

        max_depth = 10.0  # Maximum depth to map to white
        depth = min(hit.dist, max_depth)
        intensity = 1.0 - (depth / max_depth)
        gray_value = int(intensity * 255)
        return Color.custom_rgb(gray_value, gray_value, gray_value)

    def shade_multiple_lights(self, hit: HitPoint, world: World, lights: list[Light], view_dir: Vector) -> Color:
        """
        Shade ignoring multiple lights; depth is independent of lighting.
        """
        return self.shade(hit=hit, world=world, light=None, view_dir=view_dir)