from dataclasses import dataclass
from src.render.integrator.integrator import Integrator
from src.scene.scene import Scene
from src.geometry.ray import Ray
from src.scene.surface_interaction import SurfaceInteraction
from src.material.color import Color, clamp_color01
from src.material.material.material import Material
from src.scene.light import Light
from src.math import Vector
from src.math import reflect, refract
from src.shading.blinn_phong_shader import BlinnPhongShader
from src.shading.local_shading import LocalShading, apply_noise_normal_perturbation



@dataclass
class RecursiveIntegrator(Integrator):
    max_depth: int
    scene: Scene
    lights: list[Light]
    shader: LocalShading | None = None
    skybox: str | None = None
    _bias_scale: float = 1e-3
    _bias_min: float = 1e-4

    def cast_ray(self, ray: Ray, depth: int | None = None) -> Color:
        if self.shader is None:
            self.shader = BlinnPhongShader()

        if depth is None:
            depth = self.max_depth

        if depth <= 0:
            return Color.custom_rgb(0, 0, 0)

        hit = self.scene.intersect(ray)

        if hit is None:
            return Color.background_color(ray.direction, skybox=self.skybox)

        local_color = self.shader.shade_multiple_lights(hit=hit, lights=self.lights, view_dir=-ray.direction, scene=self.scene)

        material = hit.material
        reflectivity = material.get_reflectance()
        transparency = material.get_transparency()

        if reflectivity <= 0.0 and transparency <= 0.0:
            return local_color

        n_geom, n_shade = self._get_normals(hit, material)

        if reflectivity > 0.0 and transparency > 0.0:
            # Fresnel-like blend: reflect + refract sum to 1
            reflected_ray = self._reflection_ray(ray, hit, n_geom, n_shade)
            refracted_ray = self._refraction_ray(ray, hit, n_geom, n_shade, material)
            reflected_color = self.cast_ray(reflected_ray, depth - 1)
            refracted_color = self.cast_ray(refracted_ray, depth - 1)
            result = local_color * (1.0 - transparency) + reflected_color * reflectivity + refracted_color * transparency

        elif reflectivity > 0.0:
            reflected_ray = self._reflection_ray(ray, hit, n_geom, n_shade)
            reflected_color = self.cast_ray(reflected_ray, depth - 1)
            result = local_color * (1.0 - reflectivity) + reflected_color * reflectivity

        elif transparency > 0.0:
            refracted_ray = self._refraction_ray(ray, hit, n_geom, n_shade, material)
            refracted_color = self.cast_ray(refracted_ray, depth - 1)
            result = local_color * (1.0 - transparency) + refracted_color * transparency

        else:
            result = local_color

        return clamp_color01(result)

    def _get_normals(self, hit: SurfaceInteraction, material: Material) -> tuple[Vector, Vector]:
        n_geom = hit.geom.normal.normalize()
        if hasattr(material, "normal_noise"):
            n_shade = apply_noise_normal_perturbation(hit, material.normal_noise, n_geom)
        else:
            n_shade = n_geom
        return n_geom, n_shade

    def _bias(self, hit: SurfaceInteraction) -> float:
        dist = getattr(hit.geom, "dist", None)
        if dist is not None:
            return max(self._bias_min, self._bias_scale * min(1.0, dist))
        return self._bias_min

    def _reflection_ray(self, ray: Ray, hit: SurfaceInteraction, n_geom: Vector, n_shade: Vector) -> Ray:
        n = n_shade if n_shade.dot(ray.direction) <= 0.0 else -n_shade
        R = reflect(ray.direction, n).normalize()
        origin = hit.geom.point + n_geom * self._bias(hit)
        return Ray(origin, R)

    def _refraction_ray(self, ray: Ray, hit: SurfaceInteraction, n_geom: Vector, n_shade: Vector, material: Material) -> Ray:
        ior_m = getattr(material, "ior", 1.5)
        front_face = n_shade.dot(ray.direction) < 0.0
        outward_n = n_shade if front_face else -n_shade
        ior_out, ior_in = (1.0, ior_m) if front_face else (ior_m, 1.0)
        bias = self._bias(hit)

        Tdir = refract(ray.direction, outward_n, ior_out=ior_out, ior_in=ior_in)

        if Tdir is None:
            R = reflect(ray.direction, outward_n).normalize()
            origin = hit.geom.point + n_geom * bias
            return Ray(origin, R)

        origin = hit.geom.point - n_geom * bias
        return Ray(origin, Tdir.normalize())