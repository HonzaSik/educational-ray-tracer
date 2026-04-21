from __future__ import annotations
from .local_shading import LocalShading
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.light import Light
from src.material.color import Color
from src.math import Vector
from dataclasses import dataclass
from src.scene.scene import Scene


@dataclass
class DepthShader(LocalShading):
    """
    Simple object shader for visualizing depth from the camera.
    """
    max_depth: float = 10.0

    def shade(self, hit: SurfaceInteraction, light: Light | None, view_dir: Vector, scene: Scene | None = None) -> Color:
        """
        Shade based on the depth of the hit point from the camera. Closer objects will be brighter, while farther objects will be darker.
        """
        depth = min(hit.geom.dist, self.max_depth)
        intensity = 1.0 - (depth / self.max_depth)
        gray_value = int(intensity * 255)
        return Color.custom_rgb(gray_value, gray_value, gray_value)

    def shade_multiple_lights(self, hit, lights, view_dir, scene: Scene | None = None) -> Color:
        """
        Shade ignoring multiple lights; depth is independent of lighting.
        """
        return self.shade(hit=hit, light=None, view_dir=view_dir)
