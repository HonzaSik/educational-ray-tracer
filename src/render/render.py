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
from src.shading.shader_model import ShadingModel
from .helpers import ray_color

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


    for j in tqdm(range(res.height), desc="Rendering", unit="rows"):
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