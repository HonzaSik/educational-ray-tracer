from src.geometry.ray import Ray
from src.geometry.hit_point import HitPoint
from src.geometry.world import World
from src.material.color import Color, interpolate_color, to_u8, clamp_color01
from src.material.material import Material
from src.scene.light import Light
from src.scene.camera import Camera
from src.math import Vector
from random import random
from typing import Tuple
from tqdm.notebook import tqdm #todo move this away so that render does not depend on tqdm only when in notebook
from src.math import reflect, refract
from src.math.helpers import clamp_float_01
from src.math import fresnel_schlick
from src.shading.blinn_phong_shader import BlinnPhongShader
from src.shading.model import ShadingModel

def ray_color(
    ray: Ray,
    world: World,
    lights: list[Light],
    depth: int = 3,
    shader: ShadingModel | None = None,
    skybox: str | None = None,
) -> Color:
    if shader is None:
        shader = BlinnPhongShader() # default shader

    if depth <= 0:
        return Color.custom_rgb(0, 0, 0)

    hit = world.hit(ray)
    if hit is not None:
        # direct lighting
        local_color = shader.shade_multiple_lights(hit, world, lights, -ray.direction).clamp01()

        m = hit.material
        reflectivity = clamp_float_01(m.reflectivity)
        transparency = clamp_float_01(m.transparency)

        if reflectivity <= 0.0 and transparency <= 0.0:
            return local_color

        n = hit.normal.normalize()

        if reflectivity >= transparency:
            reflected_ray, _ = handle_reflection(ray, hit, n, m, throughput=1.0)
            reflected_color = ray_color(reflected_ray, world, lights, depth - 1, shader=shader, skybox=skybox)
            return clamp_color01(local_color + reflected_color * reflectivity)
        else:
            refracted_ray, _ = handle_refraction(ray, hit, n, m, throughput=1.0)
            refracted_color = ray_color(refracted_ray, world, lights, depth - 1, shader=shader, skybox=skybox)
            return clamp_color01(local_color + refracted_color * transparency)

    return Color.background_color(ray.direction, skybox=skybox) # background color


def handle_reflection(ray: Ray,
                      hit: HitPoint,
                      normal: Vector,
                      material: Material,
                      throughput: float) -> tuple[Ray, float]:
    R = reflect(ray.direction, normal).normalize()

    # Fresnel-Schlick
    f0_base = Color(0.04, 0.04, 0.04)
    metallic = clamp_float_01(getattr(material, "metallic", 0.0))
    f0 = interpolate_color(f0_base, material.base_color, metallic)
    F = fresnel_schlick(normal, -ray.direction, f0).clamp01()

    # Energy mixing
    def luminance(c: Color) -> float:
        return 0.2126*c.x + 0.7152*c.y + 0.0722*c.z

    F_avg = luminance(F)
    user_refl = clamp_float_01(getattr(material, "reflectivity", 0.0))
    energy = clamp_float_01(user_refl + (1.0 - user_refl) * F_avg)
    throughput *= energy

    next_dir = R

    bias = max(1e-4, 1e-3 * min(1.0, hit.dist))
    origin = hit.point + normal * bias
    return Ray(origin, next_dir), throughput



def handle_refraction(ray: Ray,
                      hit: HitPoint,
                      n_geom: Vector,
                      material: Material,
                      throughput: float) -> tuple[Ray, float]:
    trans = clamp_float_01(getattr(material, "transparency", 0.0))
    ior_m = getattr(material, "ior", 1.5)

    front_face = n_geom.dot(ray.direction) < 0.0
    outward_n = n_geom if front_face else -n_geom
    ior_out = 1.0 if front_face else ior_m
    ior_in  = ior_m if front_face else 1.0

    Tdir = refract(ray.direction, outward_n, ior_out=ior_out, ior_in=ior_in)
    throughput *= trans

    bias = max(1e-4, 1e-3 * min(1.0, hit.dist))
    if Tdir is None:
        # TIR -> reflect
        next_dir = reflect(ray.direction, outward_n).normalize()
        origin = hit.point + outward_n * bias
        return Ray(origin, next_dir), throughput
    else:
        origin = hit.point - outward_n * bias
        return Ray(origin, Tdir.normalize()), throughput


def render(
            cam: Camera | None = None,
            world: World | None = None,
            lights: list[Light] = None,
            samples_per_pixel: int = 10,
            max_depth: int = 5,
            skybox: str | None = None,
            shading_model: ShadingModel | None = None,
        ) -> Tuple[list[Tuple[int, int, int]], int, int]:
    """
    Render the scene using ray tracing.
    :param lights:
    :param shading_model: shading model to use (default is Blinn-Phong)
    :param skybox: path to an HDR image for environment lighting
    :param lights: list of Light sources in the scene
    :param world:
    :param cam:
    :param samples_per_pixel: number of samples per pixel for anti-aliasing
    :param max_depth: maximum recursion depth for ray tracing
    :return: list of pixel colors as (R, G, B) tuples, image width, image height
    """

    if world is None:
        raise ValueError("World must be provided for rendering.")

    if cam is None:
        raise ValueError("Camera must be provided for rendering.")

    if not lights:
        raise ValueError("At least one light source must be provided for rendering.")

    #camera setup
    res = cam.resolution

    pixels = []

    if shading_model is None:
        shader = BlinnPhongShader()
    else:
        shader = shading_model

    for j in tqdm(range(res.height), desc="Rendering", unit="row"):
        v_base = ((res.height - 1 - j) / (res.height - 1)) - 0.5

        for i in range(res.width):
            u_base = (i / (res.width - 1)) - 0.5
            acc = Color.custom_rgb(0, 0, 0)

            for _ in range(samples_per_pixel):
                du = (random() - 0.5) / (res.width - 1)
                dv = (random() - 0.5) / (res.height - 1)
                ray = cam.make_ray(u_base + du, v_base + dv)
                acc += ray_color(ray, world, lights, depth=max_depth, shader=shader, skybox=skybox)

            col = acc * (1.0 / samples_per_pixel)
            pixels.append((to_u8(col.x), to_u8(col.y), to_u8(col.z)))

    return pixels, res.width, res.height