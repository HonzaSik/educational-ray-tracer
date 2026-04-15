from src.math import Vector
from src.math.helpers import clamp_float_01
from src.material.color import Color

def fresnel_reflectance(ray_dir: Vector, normal: Vector, ior_out: float = 1.0, ior_in: float = 1.5) -> float:
    """
    Schlick's approximation for Fresnel reflectance.
    :param ray_dir: incoming ray direction (towards surface)
    :param normal: surface normal (pointing outward)
    :param ior_out: IOR of the medium the ray is coming from
    :param ior_in: IOR of the medium the ray is entering
    :return: scalar Fresnel reflectance [0, 1]
    """
    normal = normal.normalize()
    cos_theta = clamp_float_01(normal.dot(-ray_dir.normalize()))
    r0 = ((ior_out - ior_in) / (ior_out + ior_in)) ** 2
    return r0 + (1 - r0) * (1 - cos_theta) ** 5