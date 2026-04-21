from dataclasses import dataclass
from src.render.integrator.integrator import Integrator
from src.scene.scene import Scene
from src.geometry.ray import Ray
from src.scene.surface_interaction import SurfaceInteraction
from src.material.color import Color
from src.material.material.material import Material
from src.scene.light import Light
from src.math.vector import Vector
from src.math.optics import reflect, refract
from src.shading.extended_blinn_phong_shader import ExtendedBlinnPhongShader
from src.shading.fresnel import fresnel_schlick
from src.shading.local_shading import LocalShading, apply_noise_normal_perturbation

@dataclass
class RecursiveIntegrator(Integrator):
    max_depth: int
    scene: Scene
    lights: list[Light]
    shader: LocalShading | None = None
    skybox: str | None = None
    _bias_scale: float = 1e-3
    _bias_min: float = 1e-3

    def cast_ray(self, ray: Ray, depth: int | None = None) -> Color:
        """
        Cast a ray into the scene and compute the color seen along that ray, accounting for local shading, reflections, and refractions up to a maximum recursion depth.
        :param ray: The ray to cast into the scene.
        :param depth: Depth called internaly to limit recursion. If None, it will use the max_depth defined in the integrator, so camera rays will start with depth=None, and recursive calls will increment the depth until it reaches max_depth.
        :return:
        """

        if self.shader is None:
            self.shader = ExtendedBlinnPhongShader()

        if depth is None:
            depth = self.max_depth

        if depth <= 0:
            return Color.custom_rgb(0, 0, 0)

        # determine the closest intersection of the ray with the scene geometry but if there is no intersection, return the background color (which may be determined by a skybox if one is present in the scene)
        hit = self.scene.intersect(ray)
        if hit is None:
            return Color.background_color(ray.direction, skybox=self.skybox)

        local_color = self.shader.shade_multiple_lights(hit=hit, lights=self.lights, view_dir=-ray.direction, scene=self.scene)

        # this catches the case where user creates a material that doesn't have reflectance or transparency properties, in which case we just do local shading without reflection/refraction
        material = hit.material

        reflectivity = material.get_reflectance()
        transparency = material.get_transparency()

        if reflectivity <= 0.0 and transparency <= 0.0:
            return local_color

        n_geom, n_shade = self._get_normals(hit, material)

        if reflectivity > 0.0 and transparency > 0.0:
            # Make two recursive calls: one for reflection and one for refraction, and combine the results using approximated Fresnel equations by Schlick's approximation
            reflected_ray = self._reflection_ray(ray, hit, n_geom, n_shade)
            refracted_ray = self._refraction_ray(ray, hit, n_geom, n_shade, material)
            reflected_color = self.cast_ray(reflected_ray, depth - 1)
            refracted_color = self.cast_ray(refracted_ray, depth - 1)

            ior_m = material.get_ior()
            front_face = n_shade.dot(ray.direction) < 0.0
            ior_out, ior_in = (1.0, ior_m) if front_face else (ior_m, 1.0)
            kr = fresnel_schlick(ray.direction, n_shade, ior_out=ior_out, ior_in=ior_in)

            result = (
                    local_color * (1.0 - kr) * (1.0 - transparency) # local color contribution is reduced by both reflectivity and transparency
                    + reflected_color * kr # reflected color contribution is determined by the Fresnel reflectance
                    + refracted_color * (1.0 - kr) * transparency # refracted color contribution is reduced by the Fresnel reflectance and transparency
            )

        elif reflectivity > 0.0:
            # Only reflection, no refraction
            reflected_ray = self._reflection_ray(ray, hit, n_geom, n_shade)
            reflected_color = self.cast_ray(reflected_ray, depth - 1)
            result = local_color * (1.0 - reflectivity) + reflected_color * reflectivity

        elif transparency > 0.0:
            # Only refraction, no reflection
            refracted_ray = self._refraction_ray(ray, hit, n_geom, n_shade, material)
            refracted_color = self.cast_ray(refracted_ray, depth - 1)
            result = local_color * (1.0 - transparency) + refracted_color * transparency

        else:
            # No reflection or refraction, just local shading
            result = local_color

        return result

    @staticmethod
    def _get_normals(hit: SurfaceInteraction, material: Material) -> tuple[Vector, Vector]:
        # gets the geometric normal and the shading normal (which may be perturbed by normal noise) for the hit point this is important for correct reflection/refraction ray generation
        n_geom = hit.geom.normal.normalize()
        if hasattr(material, "normal_noise"):
            n_shade = apply_noise_normal_perturbation(hit, material.normal_noise, n_geom)
        else:
            n_shade = n_geom
        return n_geom, n_shade

    def _bias(self) -> float:
        return self._bias_min

    def _reflection_ray(self, ray: Ray, hit: SurfaceInteraction, n_geom: Vector, n_shade: Vector) -> Ray:
        n = n_shade if n_shade.dot(ray.direction) <= 0.0 else -n_shade
        R = reflect(ray.direction, n).normalize()
        origin = hit.geom.point + n_geom * self._bias()
        return Ray(origin, R)

    def _refraction_ray(self, ray: Ray, hit: SurfaceInteraction, n_geom: Vector, n_shade: Vector, material: Material) -> Ray:
        ior_m = getattr(material, "ior", 1.5)
        front_face = n_shade.dot(ray.direction) < 0.0
        outward_n = n_shade if front_face else -n_shade
        ior_out, ior_in = (1.0, ior_m) if front_face else (ior_m, 1.0)
        bias = self._bias()

        Tdir = refract(ray.direction, outward_n, ior_out=ior_out, ior_in=ior_in)

        if Tdir is None:
            R = reflect(ray.direction, outward_n).normalize()
            origin = hit.geom.point + n_geom * bias
            return Ray(origin, R)

        origin = hit.geom.point - n_geom * bias
        return Ray(origin, Tdir.normalize())