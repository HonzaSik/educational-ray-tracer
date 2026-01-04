# src/shading/dot_product_shader.py
from dataclasses import dataclass
from .shading_model import ShadingModel
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.light import Light
from src.material.color import Color
from src.math import Vector
import math

@dataclass
class DotProductShader(ShadingModel):
    """
    Object shader that colors based on the dot product between the normal and either the light direction or view direction.
    param use_light: If True, uses the light direction; otherwise uses the view direction.
    param frequency: Frequency of the sine wave applied to the dot product value for color variation.
    """
    use_light: bool = False
    frequency: float = 8.0

    def shade(self, hit: SurfaceInteraction, light: Light | None, view_dir: Vector) -> Color:
        """
        Shade based on the dot product between the normal and light/view direction.
        """
        norm = hit.geom.normal.normalize()
        if self.use_light and light:
            light = (light.position - hit.geom.point).normalize()
            # measures how much the normal faces the light
            view = max(norm.dot(light), -1.0)
        else:
            view = (-view_dir).normalize()
            # measures how much the normal faces the view direction
            view = max(norm.dot(view), -1.0)

        # map from [-1, 1] to [0, 1]
        t = 0.5 * (view + 1.0)

        # apply sine wave for color variation for better visualization of angles
        color = Color(math.sin(t * self.frequency) * 0.5 + 0.5, t, 1.0 - t)
        return color.clamp_01()

    def shade_multiple_lights(self, hit : SurfaceInteraction, lights, view_dir):
        """
        Shade using the first light in the list if use_light is True; otherwise, ignore lights.
        """
        return self.shade(hit, lights[0] if lights else None, view_dir)
