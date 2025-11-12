from .shader_model import ShadingModel
from src.geometry.hit_point import HitPoint
from src.geometry.world import World
from src.scene.light import Light
from src.material.color import Color
from src.math import Vector
from dataclasses import dataclass

@dataclass
class NormalShader(ShadingModel):
    """
    Simple object shader for previewing normals.
    """

    def shade(self, hit: HitPoint, world: World, light: Light| None, view_dir: Vector) -> Color:
        """
        Shade based on the normal vector at the hit point.
        """

        norm = hit.normal.normalize_ip()
        red = int((norm.x + 1) * 0.5 * 255)
        green = int((norm.y + 1) * 0.5 * 255)
        blue = int((norm.z + 1) * 0.5 * 255)

        return Color.custom_rgb(red, green, blue)


    def shade_multiple_lights(self, hit: HitPoint, world: World, lights: list[Light], view_dir: Vector) -> Color:
        """
        Shade ignoring multiple lights; normals are independent of lighting.
        """
        return self.shade(hit=hit, world=world, light=None, view_dir=view_dir)
