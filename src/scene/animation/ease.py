from typing import Callable

def linear(t: float) -> float:
    return t

def ease_in_out(t: float) -> float:
    if t < 0.5:
        return 2 * t * t
    else:
        return -1 + (4 - 2 * t) * t

Easing = Callable[[float], float]