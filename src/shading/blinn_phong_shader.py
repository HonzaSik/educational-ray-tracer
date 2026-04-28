from __future__ import annotations
from .local_shading import LocalShading, apply_noise_normal_perturbation
from src.scene.surface_interaction import SurfaceInteraction
from src.material.color import Color
from src.material.material import PhongMaterialSample
from src.scene.light import Light, LightType
from src.math import Vector
from src.shading.helpers import in_shadow, light_dir_dist
from src.scene.scene import Scene



class BlinnPhongShader(LocalShading):
    """
    Blinn-Phong shader extended on material sample with support for normal perturbation.
    """

    def shade(self, hit: SurfaceInteraction, light: Light, view_dir: Vector, scene: Scene | None = None) -> Color:
        if scene is None:
            raise ValueError("Scene must be provided for shading.")

        ms = self._get_phong_sample(hit)

        # because ambient light is not directional, we can skip shadow checks and normal perturbation for it
        if light.type == LightType.AMBIENT:
            return light.intensity_at(hit.point) * ms.ambient_color

        # get the light intensity at the hit point; if it's zero or can be set near zero, skip shading calculations
        light_intensity = light.intensity_at(hit.point)
        if light_intensity <= 0.0:
            return Color.custom_rgb(0, 0, 0)

        # test if the point is in shadow relative to this light; if so, skip diffuse and specular contributions
        light_direction, light_distance = light_dir_dist(hit, light)

        v = view_dir.normalize()
        n = hit.normal.normalize()
        # apply normal perturbation for more realistic shading before calculating diffuse and specular contributions
        n = apply_noise_normal_perturbation(hit, ms.normal_noise, n)
        l = light_direction.normalize()

        ndotl = n.dot(l)
        if ndotl <= 0.0:
            return Color.custom_rgb(0, 0, 0)

        if in_shadow(hit, light_direction, light_distance, scene=scene):
            return Color.custom_rgb(0, 0, 0)

        #check if the light is facing the surface
        ndotl = n.dot(l)
        if ndotl <= 0.0:
            return Color.custom_rgb(0, 0, 0)

        diffuse = self._lambert_from_sample(ms, n, l)
        specular = self._blinn_specular_from_sample(ms, n, l, v) * ndotl # not accurate by blinn-phong model, but gives better results by reducing specular highlights on grazing angles
        return (diffuse + specular) * light_intensity * light.get_color_at(hit.point)

    def shade_multiple_lights(self, hit: SurfaceInteraction, lights: list[Light], view_dir: Vector, scene: Scene | None = None ) -> Color:
        if scene is None:
            raise ValueError("Scene must be provided for shading.")

        accum = Color.custom_rgb(0, 0, 0)
        for light in lights:
            accum += self.shade(hit, light, view_dir, scene=scene)
        return accum

    @staticmethod
    def _lambert_from_sample(ms: PhongMaterialSample, n: Vector, l: Vector) -> Color:
        return ms.base_color * max(0.0, n.dot(l))

    @staticmethod
    def _blinn_specular_from_sample(ms: PhongMaterialSample, n: Vector, l: Vector, v: Vector) -> Color:
        h = (l + v).normalize()
        ndoth = max(0.0, n.dot(h))
        shininess = max(1.0, ms.shininess)
        return ms.spec_color * (ndoth ** shininess)

    @staticmethod
    def _get_phong_sample(hit: SurfaceInteraction) -> PhongMaterialSample:
        sample = hit.material.sample(hit)
        if not isinstance(sample, PhongMaterialSample):
            raise TypeError("BlinnPhongShader requires PhongMaterialSample.")
        return sample