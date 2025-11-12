# src/shading/curvature_shader.py
from dataclasses import dataclass

from contourpy.types import offset_dtype

from .shader_model import ShadingModel
from src.geometry.hit_point import HitPoint
from src.geometry.world import World
from src.material.color import Color
from src.math import Vector
from ..scene import Light


@dataclass
class CurvatureShader(ShadingModel):
    """
    Simple object shader for visualizing curvature by approximating it using finite differences of normals.
    Lighter areas indicate higher curvature, while darker areas indicate flat regions.
    """
    _bias: float = 0.005

    def shade(self, hit: HitPoint, world: World, light: Light| None, view_dir: Vector) -> Color:
        """
        Shade based on the curvature approximated by finite differences of normals.
        """
        offset = self._bias
        norm = hit.normal.normalize()

        # Sample normals at small offsets in x and z directions normalized
        offset_norm_x = world.normal_at(hit.point + Vector(offset,0,0)).normalize()
        offset_norm_z = world.normal_at(hit.point + Vector(0,0,offset)).normalize()

        # Approximate curvature using the change in normals in x and z directions
        curvature = 1.0 - 0.5 * (norm.dot(offset_norm_x) + norm.dot(offset_norm_z))
        color = Color(curvature, curvature, curvature)
        return color.clamp01()

    def shade_multiple_lights(self, hit, world, lights, view_dir):
        """
        Shade ignoring multiple lights. Curvature is independent of lighting.
        """
        return self.shade(hit, world, None, view_dir)
