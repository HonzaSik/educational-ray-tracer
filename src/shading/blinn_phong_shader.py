from __future__ import annotations
from .local_shading import LocalShading, apply_noise_normal_perturbation
from src.scene.surface_interaction import SurfaceInteraction
from src.material.color import Color, clamp_color255
from src.material.material import PhongMaterialSample
from src.scene.light import Light, LightType, AmbientLight
from src.math import Vector
from src.shading.fersnel import fresnel_reflectance, dielectric_f0
from .helpers import shadow_trace, light_dir_dist
from src.scene.scene import Scene
from src.material.material.phong_material import PhongMaterial


class BlinnPhongShader(LocalShading):
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

        material : PhongMaterial = hit.material # type: ignore
        ms: PhongMaterialSample = material.sample(hit)

        if light.type == LightType.AMBIENT:
            return light.intensity_at(hit.point) * ms.base_color

        light_direction, light_distance = light_dir_dist(hit, light)

        if shadow_trace(hit, light_direction, light_distance, scene=scene):
            return Color.custom_rgb(0, 0, 0)

        light_intensity = light.intensity_at(hit.point)
        if light_intensity <= 0.0:
            return Color.custom_rgb(0, 0, 0)

        n = hit.normal.normalize()
        noise_for_normals = ms.normal_noise if ms.normal_noise is not None else material.normal_noise
        n = apply_noise_normal_perturbation(hit, noise_for_normals, n)

        l = light_direction.normalize()
        v = view_dir.normalize()

        diffuse = self._lambert_from_sample(ms, n, l)
        specular = self._blinn_specular_from_sample(ms, n, l, v)

        return (diffuse + specular) * light_intensity

    def shade_multiple_lights(self, hit: SurfaceInteraction, lights: list[Light], view_dir: Vector,
                              scene: Scene | None = None) -> Color:

        material : PhongMaterial = hit.material

        material_sample: PhongMaterialSample = material.sample(hit)
        is_transmissive = getattr(material, "transparency", 0.0) > 0.0 and getattr(material, "ior", 1.0) > 1.0

        accum = Color(0, 0, 0)

        for light in lights:
            if light.type == LightType.AMBIENT:
                accum += light.intensity_at(hit.point) * material_sample.base_color
            else:
                accum += self.shade(hit, light, view_dir, scene=scene)

        if is_transmissive:
            n = hit.normal.normalize()
            accum += self._blinn_specular_from_sample(material_sample, n, -view_dir, view_dir)

        return clamp_color255(accum)

    @staticmethod
    def _lambert_from_sample(ms: PhongMaterialSample, n: Vector, l: Vector) -> Color:
        if ms.opacity <= 0.0:
            return Color(0.0, 0.0, 0.0)
        return ms.base_color * max(0.0, n.dot(l))

    def _blinn_specular_from_sample(self, ms: PhongMaterialSample, n: Vector, l: Vector, v: Vector) -> Color:
        h = (l + v).normalize()
        ndoth = max(0.0, n.dot(h))
        shininess = max(1.0, ms.shininess) # to avoid zero shininess which would cause specular to be always 1.0

        spec = ms.spec_color * (ndoth ** shininess)

        if self.use_fresnel and ms.ior > 1.0:
            kr = fresnel_reflectance(-v, n, ior_out=1.0, ior_in=ms.ior)
            spec = spec * kr

        return spec