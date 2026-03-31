from .vector import Vector
from numpy import sqrt

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