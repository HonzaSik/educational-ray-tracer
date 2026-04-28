from dataclasses import dataclass, field
from src.render.integrator.integrator import Integrator
from src.scene.scene import Scene
from src.geometry.ray import Ray
from src.scene.surface_interaction import SurfaceInteraction
from src.material.color import Color
from src.material.material.material import Material
from src.scene.light import Light
from src.math.vector import Vector
from src.math.optics import reflect, refract
from src.shading.blinn_phong_shader import BlinnPhongShader
from src.render.integrator.fresnel import fresnel_schlick
from src.shading.local_shading import LocalShading, apply_noise_normal_perturbation

@dataclass
class RecursiveIntegrator(Integrator):
    max_depth: int
    scene: Scene
    lights: list[Light]
    shader: LocalShading | None = None
    _bias_min: float = 1e-3

    def __post_init__(self):
        if self.shader is None:
            self.shader = BlinnPhongShader()

    def cast_ray(self, ray: Ray, depth: int | None = None) -> Color:
        """
        Cast a ray into the scene and compute the color seen along that ray, accounting for local shading, reflections, and refractions up to a maximum recursion depth.
        :param ray: The ray to cast into the scene.
        :param depth: Depth called internaly to limit recursion. If None, it will use the max_depth defined in the integrator, so camera rays will start with depth=None, and recursive calls will increment the depth until it reaches max_depth.
        :return:
        """

        if depth is None:
            depth = self.max_depth

        hit = self.scene.intersect(ray)
        if hit is None:
            return Color.background_color(ray.direction, skybox=self.scene.skybox)

        local_color = self.shader.shade_multiple_lights(
            hit=hit, lights=self.lights, view_dir=-ray.direction, scene=self.scene
        )

        if depth <= 0:
            return local_color

        material = hit.material
        reflectivity = material.get_reflectance()
        transparency = material.get_transparency()

        if reflectivity <= 0.0 and transparency <= 0.0:
            return local_color

        n_geom, n_shade = self._get_normals(hit, material)

        if transparency > 0.0:
            result = local_color * (1.0 - transparency)

            reflected_ray = self._reflection_ray(ray, hit, n_geom, n_shade)
            reflected_color = self.cast_ray(reflected_ray, depth - 1)

            kr = self._fresnel(ray, n_shade, material)
            refracted_ray = self._refraction_ray(ray, hit, n_geom, n_shade, material)

            if refracted_ray is None:
                result += reflected_color * transparency
            else:
                refracted_color = self.cast_ray(refracted_ray, depth - 1)
                result += reflected_color * (transparency * kr)
                result += refracted_color * (transparency * (1.0 - kr))

            return result

        if reflectivity > 0.0:
            reflected_ray = self._reflection_ray(ray, hit, n_geom, n_shade)
            reflected_color = self.cast_ray(reflected_ray, depth - 1)
            return local_color * (1.0 - reflectivity) + reflected_color * reflectivity

        return local_color

    @staticmethod
    def _get_normals(hit: SurfaceInteraction, material: Material) -> tuple[Vector, Vector]:
        # geometric normal are real surface normals used for ray offsetting
        # shading normal may be perturbed by a normal-noise map
        n_geom = hit.geom.normal.normalize()
        if hasattr(material, "normal_noise"):
            n_shade = apply_noise_normal_perturbation(hit, material.normal_noise, n_geom)
        else:
            n_shade = n_geom
        return n_geom, n_shade

    def _bias(self) -> float:
        return self._bias_min

    def _reflection_ray(self, ray: Ray, hit: SurfaceInteraction, n_geom: Vector, n_shade: Vector) -> Ray:
        # flip shading normal to face against the incoming ray
        n = n_shade if n_shade.dot(ray.direction) <= 0.0 else -n_shade
        R = reflect(ray.direction, n).normalize()
        # bias along the geometric normal to avoid self-intersection on the true surface
        n_geom_facing = n_geom if n_geom.dot(ray.direction) <= 0.0 else -n_geom
        origin = hit.geom.point + n_geom_facing * self._bias()
        return Ray(origin, R)

    def _refraction_ray(self, ray: Ray, hit: SurfaceInteraction, n_geom: Vector, n_shade: Vector, material: Material) -> Ray | None:
        ior_m = material.get_ior()
        front_face = n_shade.dot(ray.direction) < 0.0
        outward_n = n_shade if front_face else -n_shade
        ior_out, ior_in = (1.0, ior_m) if front_face else (ior_m, 1.0)

        # tdir is the refracted ray direction. If None, total internal reflection occurs and we should not cast a refraction ray.
        Tdir = refract(ray.direction, outward_n, ior_out=ior_out, ior_in=ior_in)
        if Tdir is None:
            return None

        # bias into the surface (opposite side from reflection)
        n_geom_facing = n_geom if n_geom.dot(ray.direction) <= 0.0 else -n_geom
        origin = hit.geom.point - n_geom_facing * self._bias()
        return Ray(origin, Tdir.normalize())

    @staticmethod
    def _fresnel(ray: Ray, n_shade: Vector, material: Material) -> float:
        # Schlick's approximation, with air assumed on the outside
        ior_m = material.get_ior()
        front_face = n_shade.dot(ray.direction) < 0.0
        n = n_shade if front_face else -n_shade
        ior_out, ior_in = (1.0, ior_m) if front_face else (ior_m, 1.0)
        return fresnel_schlick(ray.direction, n, ior_out=ior_out, ior_in=ior_in)