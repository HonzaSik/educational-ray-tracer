from .shading_model import ShadingModel, apply_noise_normal_perturbation
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.light import Light
from src.material.color import Color
from src.math import Vector
from dataclasses import dataclass

from src.scene.scene import Scene


@dataclass
class NormalShader(ShadingModel):
    """
    Simple object shader for previewing normals.
    """

    def shade(self, hit: SurfaceInteraction, light: Light | None, view_dir: Vector,
              scene: Scene | None = None) -> Color:
        """
        Shade based on the normal vector at the hit point.
        """
        material = hit.material
        n = hit.normal.normalize()

        noise = getattr(material, "normal_noise", None)
        norm = apply_noise_normal_perturbation(hit, noise, n)

        red = int((norm.x + 1) * 0.5 * 255)
        green = int((norm.y + 1) * 0.5 * 255)
        blue = int((norm.z + 1) * 0.5 * 255)

        return Color.custom_rgb(red, green, blue)

    def shade_multiple_lights(self, hit: SurfaceInteraction, lights: list[Light], view_dir: Vector,
                              scene: Scene | None = None) -> Color:
        """
        Shade ignoring multiple lights; normals are independent of lighting.
        """
        return self.shade(hit=hit, light=None, view_dir=view_dir)
