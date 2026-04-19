from src.material.color import Color
from src.math import Vector
from src.scene.scene import Scene
from src.scene import SurfaceInteraction, Light
from src.shading import LocalShading


class ColorShader(LocalShading):
    """
    A simple shader that returns the base color of the material without any lighting calculations. This can be useful for debugging or for rendering objects with a flat color.
    """
    def shade(self, hit: SurfaceInteraction, light: Light, view_dir: Vector, scene: Scene | None = None) -> Color:
        return hit.material.get_color()

    def shade_multiple_lights(self, hit: SurfaceInteraction, lights: list[Light], view_dir: Vector, scene: Scene | None = None) -> Color:
        return hit.material.get_color()