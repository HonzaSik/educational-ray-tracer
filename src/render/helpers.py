from src.geometry.ray import Ray
from src.geometry.hit_point import HitPoint
from src.geometry.world import World
from src.material.color import Color, interpolate_color, clamp_color01
from src.material.material import Material
from src.scene.light import Light
from src.math import Vector
from src.math import reflect, refract
from src.math.helpers import clamp_float_01
from src.math import fresnel_schlick
from src.shading.blinn_phong_shader import BlinnPhongShader
from src.shading.shader_model import ShadingModel

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