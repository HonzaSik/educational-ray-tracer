from __future__ import annotations
from abc import ABC
from .shading_model import ShadingModel
from src.scene.surface_interaction import SurfaceInteraction
from src.material.color import Color, clamp_color255
from src.material.material.material import Material
from src.scene.light import Light, AmbientLight
from src.math import Vector
from src.math import fresnel_schlick, dielectric_f0
from .helpers import shadow_trace, light_dir_dist
from src.scene.scene import Scene


class BlinnPhongShader(ShadingModel, ABC):
    """
    Blinn–Phong shader with optional Fresnel for dielectrics. Supports multiple lights, ambient, and emission.
    """

    def __init__(
            self,
            use_fresnel: bool = True,
    ) -> None:
        self.use_fresnel = use_fresnel

    def shade(self, hit: SurfaceInteraction, light: Light, view_dir: Vector, scene: Scene | None = None) -> Color:
        if scene is None:
            raise ValueError("Scene must be provided for shading.")

        material = hit.material

        if light.type == AmbientLight:
            return Color(0, 0, 0)

        light_direction, light_distance = light_dir_dist(hit, light)

        if shadow_trace(hit, light_direction, light_distance, scene=scene):
            return Color.custom_rgb(0, 0, 0)

        light_intensity = light.intensity_at(hit.point)
        if light_intensity <= 0.0:
            return Color.custom_rgb(0, 0, 0)

        n = hit.normal.normalize_ip()
        l = light_direction.normalize_ip()
        v = view_dir.normalize_ip()

        diffuse = self._lambert_diffuse(material, n, l)
        specular = self._blinn_specular(material, n, l, v)

        return (diffuse + specular) * light_intensity

    def shade_multiple_lights(self, hit: SurfaceInteraction, lights: list[Light], view_dir: Vector,
                              scene: Scene | None = None) -> Color:
        material = hit.material
        is_transmissive = getattr(material, "transparency", 0.0) > 0.0 and getattr(material, "ior", 1.0) > 1.0

        accum = Color(0, 0, 0)

        for light in lights:
            if light.type == AmbientLight:
                accum += light.intensity_at(hit.geom.point) * material.get_color()
            else:
                accum += self.shade(hit, light, view_dir, scene=scene)

        if is_transmissive:
            n = hit.normal.normalize_ip()
            accum += self._blinn_specular(material, n, -view_dir, view_dir)

        return clamp_color255(accum)

    @staticmethod
    def _lambert_diffuse(m: Material, n: Vector, l: Vector) -> Color:
        # turn off diffuse when the material is transmissive (glass)
        if getattr(m, "transparency", 0.0) > 0.0:
            return Color(0.0, 0.0, 0.0)

        ndotl = max(0.0, n.dot(l))
        return m.get_color() * ndotl

    def _blinn_specular(self, material: Material, n: Vector, l: Vector, v: Vector) -> Color:
        """
        Classic Blinn–Phong specular: (n·h)^shininess with optional Fresnel.
        """
        h = (l + v).normalize_ip()
        ndoth = max(0.0, n.dot(h))
        shininess = max(2.0, getattr(material, "shininess", 32.0))

        spec = material.get_specular_color() * (ndoth ** shininess)

        if self.use_fresnel and getattr(material, "ior", 1.0) > 1.0:
            dielectric_color = dielectric_f0(material.get_ior())
            F = fresnel_schlick(n, v, dielectric_color)
            spec = spec * F

        return spec
