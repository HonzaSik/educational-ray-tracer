from __future__ import annotations
from .local_shading import LocalShading, apply_noise_normal_perturbation
from src.scene.surface_interaction import SurfaceInteraction
from src.material.color import Color, clamp_color255
from src.material.material import PhongMaterialSample
from src.scene.light import Light, LightType
from src.math import Vector
from src.shading.fresnel import fresnel_schlick
from .helpers import in_shadow, light_dir_dist
from src.scene.scene import Scene


class ExtendedBlinnPhongShader(LocalShading):
    """
    Blinn-Phong shader with optional Fresnel effects for specular highlights and support for transparency.
    """

    def shade(self, hit: SurfaceInteraction, light: Light, view_dir: Vector, scene: Scene | None = None) -> Color:
        if scene is None:
            raise ValueError("Scene must be provided for shading.")

        ms = self._get_phong_sample(hit)

        # because ambient light is not directional, we can skip shadow checks and normal perturbation for it
        if light.type == LightType.AMBIENT:
            return light.intensity_at(hit.point) * ms.ambient_color

        # test if the point is in shadow relative to this light; if so, skip diffuse and specular contributions
        light_direction, light_distance = light_dir_dist(hit, light)
        if in_shadow(hit, light_direction, light_distance, scene=scene):
            return Color.custom_rgb(0, 0, 0)

        # get the light intensity at the hit point; if it's zero or can be set near zero, skip shading calculations
        light_intensity = light.intensity_at(hit.point)
        if light_intensity <= 0.0:
            return Color.custom_rgb(0, 0, 0)

        # apply normal perturbation for more realistic shading before calculating diffuse and specular contributions
        n = hit.normal.normalize()
        n = apply_noise_normal_perturbation(hit, ms.normal_noise, n)

        # use extra Fresnel-Schlick approximation to modulate the specular contribution based on the view angle and material IOR this creates more realistic highlights that vary with angle but its simplified and not physically accurate
        l = light_direction.normalize()
        v = view_dir.normalize()
        # only apply Fresnel effects if the material has an IOR greater than 1.0
        kr = fresnel_schlick(-v, n, ior_out=1.0, ior_in=ms.ior) if ms.ior > 1.0 else 0.0

        # calculate each component and return them in correctly modulated by the light intensity
        diffuse = self._lambert_from_sample(ms, n, l) * (1.0 - kr)
        specular = self._blinn_specular_from_sample(ms, n, l, v, kr)
        return (diffuse + specular) * light_intensity * light.get_color_at(hit.point)

    def shade_multiple_lights(self, hit: SurfaceInteraction, lights: list[Light], view_dir: Vector, scene: Scene | None = None ) -> Color:
        accum = Color.custom_rgb(0, 0, 0)
        for light in lights:
            accum += self.shade(hit, light, view_dir, scene=scene)
        return accum

    @staticmethod
    def _lambert_from_sample(ms: PhongMaterialSample, n: Vector, l: Vector) -> Color:
        return ms.base_color * max(0.0, n.dot(l))

    @staticmethod
    def _blinn_specular_from_sample(ms: PhongMaterialSample, n: Vector, l: Vector, v: Vector, kr: float = 1.0) -> Color:
        h = (l + v).normalize()
        ndoth = max(0.0, n.dot(h))
        shininess = max(1.0, ms.shininess)
        return ms.spec_color * (ndoth ** shininess) * kr

    @staticmethod
    def _get_phong_sample(hit: SurfaceInteraction) -> PhongMaterialSample:
        sample = hit.material.sample(hit)
        if not isinstance(sample, PhongMaterialSample):
            raise TypeError("ExtendedBlinnPhongShader requires PhongMaterialSample.")
        return sample