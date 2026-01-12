from .vector import Vector
from math import sqrt
from src.material.color import Color
from .helpers import clamp_float_01


def reflect(v: Vector, n: Vector) -> Vector:
    """
    Reflect vector v about normal n.
    :param v: incoming vector
    :param n: normal vector (must be normalized)
    :return: reflected vector
    """
    return v - n * (2.0 * v.dot(n))


def refract(v: Vector, n: Vector, ior_out: float, ior_in: float) -> Vector | None:
    """
    Refract vector v through surface with normal n using Snell's law.
    :param v: incoming vector
    :param n: normal vector at intersection (must be normalized)
    :param ior_out: index of refraction of the medium ray is exiting
    :param ior_in: index of refraction of the medium ray is entering
    :return: refracted vector or None if total internal reflection occurs
    """
    v = v.normalize_ip()
    n = n.normalize_ip()

    eta = ior_out / ior_in  # ratio of indices
    cos_i = -n.dot(v)  # cosine of angle of incidence

    if cos_i < 0.0:  # ray is inside the medium
        n = -n
        cos_i = -cos_i
        eta = 1.0 / eta

    sin2_t = eta * eta * max(0.0, 1.0 - cos_i * cos_i)  # sin^2(theta_t)
    if sin2_t >= 1.0:  # total internal reflection
        return None

    cos_t = sqrt(max(0.0, 1.0 - sin2_t))  # cosine of angle of refraction
    t = v * eta + n * (eta * cos_i - cos_t)
    return t.normalize_ip()


def fresnel_schlick(normal: Vector, view_dir: Vector, f0: Color) -> Color:
    """
    Schlick's approximation for Fresnel reflectance.
    :param normal: surface normal
    :param view_dir: view direction - towards the camera
    :param f0: base reflectance at normal incidence (Color)
    :return: Fresnel reflectance Color
    """
    normal = normal.normalize()
    view_dir = view_dir.normalize()
    cos_theta = clamp_float_01(normal.dot(-view_dir))
    return f0 + (Color(1.0, 1.0, 1.0) - f0) * ((1.0 - cos_theta) ** 5)


def dielectric_f0(ior: float) -> Color:
    """
    Calculate base reflectance F0 for dielectric material based on index of refraction.
    :param ior: index of refraction
    :return: base reflectance Color
    """
    f0 = ((ior - 1.0) / (ior + 1.0)) ** 2
    return Color(f0, f0, f0)
