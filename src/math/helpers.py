def clamp_float_01(x: float) -> float:
    """
    Clamp scalar to [0, 1].
    0 if x < 0, 1 if x > 1, else x.
    :param x: input scalar
    """
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def interpolate(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between a and b by factor t in [0, 1].
    :param a: point a
    :param b: point b
    :param t: interpolation factor
    :return: interpolated value
    """
    return a * (1.0 - t) + b * t