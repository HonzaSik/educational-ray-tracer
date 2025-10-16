# src/shading/blinn_phong_shader.py
from __future__ import annotations
from abc import ABC
from typing import Optional
from .shader_model import ShadingModel
from src.geometry.hit_point import HitPoint
from src.geometry.world import World
from src.material.color import Color, clamp_color255
from src.material.material import Material
from src.scene.light import Light, AmbientLight
from src.math import Vector
from src.math import fresnel_schlick, dielectric_f0
from .helpers import shadow_trace, light_dir_dist


class BlinnPhongShader(ShadingModel, ABC):
    """
    Blinn–Phong shader with optional Fresnel for dielectrics. Supports multiple lights, ambient, and emission.
    """
    def __init__(
        self,
        use_fresnel: bool = True,
    ) -> None:
        self.use_fresnel = use_fresnel


    def shade(self, hit: HitPoint, world: World, light: Light, view_dir: Vector) -> Color:
        """
        Shade a single light with shadows, attenuation, diffuse, and specular.
        """
        if light.type == AmbientLight: # Ambient light is handled in shade_multiple_lights
            return Color(0, 0, 0)

        light_direction, light_distance = light_dir_dist(hit, light)

        # Shadow
        if shadow_trace(hit, light_direction, light_distance, world):
            return Color.custom_rgb(0, 0, 0)

        light_intensity = light.intensity_at(hit.point)
        if light_intensity <= 0.0:
            return Color.custom_rgb(0, 0, 0)


        # Normalize vectors
        n = hit.normal.normalize_ip()
        l = light_direction.normalize_ip()
        v = view_dir.normalize_ip()

        diffuse = self._lambert_diffuse(hit.material, n, l)
        specular = self._blinn_specular(hit.material, n, l, v)

        return (diffuse + specular) * light_intensity


    def shade_multiple_lights(self, hit, world, lights, view_dir) -> Color:
        material = hit.material
        is_transmissive = getattr(material, "transparency", 0.0) > 0.0 and getattr(material, "ior", 1.0) > 1.0

        accum = Color(0, 0, 0)

        emmiters = world.emitters()
        hited_objects_color = []
        hited = False

        for emitter in emmiters:
            for i in range(10):  # todo hardcoded for testing
                emitter_point = emitter.random_point()
                to_emitter = (emitter_point - hit.point)
                light_distance = to_emitter.norm()

                if light_distance < 1e-6:
                    continue

                # normalize direction
                to_emitter.normalize_ip()

                # shadow test
                if not shadow_trace(hit, to_emitter, light_distance, world):
                    hited = True
                    # inverse square falloff
                    falloff = 1.0 / (light_distance * light_distance)
                    # accumulate color
                    color = emitter.material.emission * material.base_color * falloff
                    hited_objects_color.append(color)

        if hited:
            for obj in hited_objects_color:
                accum += obj

        for light in lights:
            if light.type == AmbientLight:
                accum += light.intensity_at(hit.point) * material.base_color
            else:
                accum += self.shade(hit, world, light, view_dir)

        accum += material.emission

        if is_transmissive:
            accum += self._blinn_specular(material, hit.normal, -view_dir, view_dir)

        return clamp_color255(accum)


    @staticmethod
    def _lambert_diffuse(m: Material, n: Vector, l: Vector) -> Color:
        # turn off diffuse when the material is transmissive (glass)
        if getattr(m, "transparency", 0.0) > 0.0:
            return Color(0.0, 0.0, 0.0)
        ndotl = max(0.0, n.dot(l))
        return m.base_color * ndotl

    def _blinn_specular(self, m: Material, n: Vector, l: Vector, v: Vector) -> Color:
        """
        Classic Blinn–Phong specular: (n·h)^shininess with optional Fresnel.
        """
        h = (l + v).normalize_ip()
        ndoth = max(0.0, n.dot(h))
        shininess = max(2.0, getattr(m, "shininess", 32.0))

        # Just use the specular color
        spec = m.spec_color * (ndoth ** shininess)

        if self.use_fresnel and getattr(m, "ior", 1.0) > 1.0:
            dielectric_color = dielectric_f0(m.ior)
            F = fresnel_schlick(n, v, dielectric_color)
            spec = spec * F

        return spec