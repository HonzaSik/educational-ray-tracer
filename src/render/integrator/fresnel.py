from src.math import Vector
from src.math.helpers import clamp_float_01
from src.material.color import Color

def fresnel_schlick(ray_dir: Vector, normal: Vector, ior_out: float = 1.0, ior_in: float = 1.5) -> float:
    """
    Schlick's approximation for Fresnel reflectance.
    ray_dir  ... směr paprsku ve směru letu
    normal   ... geometrická normála směřující ven z povrchu
    ior_out  ... index lomu prostředí, ze kterého paprsek přichází
    ior_in   ... index lomu prostředí, do kterého paprsek vstupuje
    """
    d = ray_dir.normalize()
    n = normal.normalize()

    cos_theta = n.dot(-d)

    # flip normal if ray is inside the medium
    if cos_theta < 0.0:
        n = -n
        cos_theta = n.dot(-d)
        ior_out, ior_in = ior_in, ior_out

    cos_theta = clamp_float_01(cos_theta)

    r0 = ((ior_out - ior_in) / (ior_out + ior_in)) ** 2
    return r0 + (1.0 - r0) * (1.0 - cos_theta) ** 5