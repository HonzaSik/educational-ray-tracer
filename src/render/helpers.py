from src.scene.scene import Scene
from src.geometry.geometry_hit import GeometryHit
from src.geometry.ray import Ray
from src.scene.surface_interaction import SurfaceInteraction
from src.material.color import Color, clamp_color01
from src.material.material.material import Material
from src.scene.light import Light
from src.math import Vector, dielectric_f0
from src.math import reflect, refract
from src.math.helpers import clamp_float_01
from src.math import fresnel_schlick
from src.shading.blinn_phong_shader import BlinnPhongShader
from src.shading.shading_model import ShadingModel

def cast_ray(
    ray: Ray,
    lights: list[Light],
    depth: int = 3,
    shader: ShadingModel | None = None,
    skybox: str | None = None,
    scene: Scene | None = None,
) -> Color:

    if shader is None:
        shader = BlinnPhongShader()


    if depth <= 0:
        return Color.custom_rgb(0, 0, 0)

    hit = scene.intersect(ray)

    if hit is not None:
        # direct lighting
        local_color = shader.shade_multiple_lights(hit, lights, -ray.direction, scene=scene).clamp_01()

        material = hit.material

        reflectivity: float = material.get_reflectance()
        transparency: float = material.get_transparency()

        if reflectivity <= 0.0 and transparency <= 0.0:
            return local_color

        n_geom = hit.geom.normal.normalize()

        if hasattr(material, "perturb_normal"):
            n_shade = material.perturb_normal(hit, n_geom).normalize()
        else:
            n_shade = n_geom

        if reflectivity >= transparency:
            reflected_ray = handle_reflection(ray, hit, n_geom, n_shade, material)
            reflected_color = cast_ray(reflected_ray, lights, depth - 1, shader=shader, skybox=skybox, scene=scene)
            return clamp_color01(local_color + reflected_color * reflectivity)
        else:
            refracted_ray = handle_refraction(ray, hit, n_geom, material)
            refracted_color = cast_ray(refracted_ray, lights, depth - 1, shader=shader, skybox=skybox, scene=scene)
            return clamp_color01(local_color + refracted_color * transparency)

    return Color.background_color(ray.direction, skybox=skybox) # background color


def handle_reflection(
    ray: Ray,
    hit: SurfaceInteraction,
    n_geom: Vector,
    n_shade: Vector,
    material: Material,
) -> Ray:
    # Make sure shading normal faces against the ray
    if n_shade.dot(ray.direction) > 0.0:
        n_shade = -n_shade

    # Use *shading* normal for reflection direction
    R = reflect(ray.direction, n_shade).normalize()

    # Fresnel-Schlick with shading normal
    ior = getattr(material, "ior", 1.5)
    f = fresnel_schlick(n_shade, -ray.direction, dielectric_f0(ior))

    # (you already compute energy etc., leaving it as-is)
    def luminance(c: Color) -> float:
        return 0.2126*c.x + 0.7152*c.y + 0.0722*c.z

    f_avg = luminance(f)
    user_refl = clamp_float_01(getattr(material, "reflectivity", 0.0))
    energy = clamp_float_01(user_refl + (1.0 - user_refl) * f_avg)

    # Use geometric normal for bias to avoid acne
    bias = max(1e-4, 1e-3 * min(1.0, hit.geom.dist)) if hasattr(hit.geom, "dist") else 1e-4
    origin = hit.geom.point + n_geom * bias

    return Ray(origin, R)


def handle_refraction(
    ray: Ray,
    hit: SurfaceInteraction,
    n_geom: Vector,
    material: Material,
) -> Ray:
    trans  = clamp_float_01(getattr(material, "transparency", 0.0))
    ior_m  = getattr(material, "ior", 1.5)

    front_face = n_geom.dot(ray.direction) < 0.0
    outward_n  = n_geom if front_face else -n_geom
    ior_out    = 1.0 if front_face else ior_m
    ior_in     = ior_m if front_face else 1.0

    Tdir = refract(ray.direction, outward_n, ior_out=ior_out, ior_in=ior_in)

    bias = max(1e-4, 1e-3 * min(1.0, hit.geom.dist)) if hasattr(hit.geom, "dist") else 1e-4

    if Tdir is None:
        next_dir = reflect(ray.direction, outward_n).normalize()
        origin   = hit.geom.point + outward_n * bias
        return Ray(origin, next_dir)
    else:
        origin = hit.geom.point - outward_n * bias
        return Ray(origin, Tdir.normalize())
