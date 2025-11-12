from src.io.resolution import Resolution
from src.math.vector import Vector
from dataclasses import dataclass

@dataclass
class AnimationSetup:
    move_from: Vector | None = None
    move_to: Vector | None = None
    move_duration: float | None = None  # in seconds

    rotate_axis: Vector | None = None
    rotate_angle: float | None = None  # in degrees
    rotate_duration: float | None = None  # in seconds

    zoom_from: float | None = None  # fov in degrees
    zoom_to: float | None = None  # fov in degrees
    zoom_duration: float | None = None  # in seconds
