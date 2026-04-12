from __future__ import annotations
from dataclasses import dataclass, field
from math import tan, radians
from src.math import Vertex, Vector
from src.geometry.ray import Ray
from .camera import Camera

@dataclass
class PinholeCamera(Camera):
    """
    Classic pinhole camera model.
    fov_deg: vertical field of view in degrees.
    """
    fov_deg: float = 70.0
    direction: Vector = field(default_factory=lambda: Vector(0, 0, -1))
    up_hint: Vector = field(default_factory=lambda: Vector(0, 1, 0))

    forward: Vector = field(init=False)
    right: Vector = field(init=False)
    up: Vector = field(init=False)
    half_width: float = field(init=False)
    half_height: float = field(init=False)

    def __post_init__(self):
        self.update_camera()

    def update_camera(self) -> None:
        fwd = self.direction.normalize()
        up = self.up_hint
        if abs(fwd.dot(up)) > 0.999:
            up = Vector(1, 0, 0)

        w = -fwd
        right = up.cross(w).normalize()
        true_up = w.cross(right)

        half_height = tan(radians(self.fov_deg) * 0.5)

        self.forward = fwd
        self.right = right
        self.up = true_up
        self.half_width = self.aspect_ratio * half_height
        self.half_height = half_height

    def make_ray(self, u: float, v: float) -> Ray:
        center_plane = self.origin + self.forward
        position = (
            center_plane
            + self.right * (u * self.half_width)
            + self.up * (v * self.half_height)
        )
        return Ray(self.origin, (position - self.origin).normalize())

    def rotate_around_axis(self, axis: Vector, angle_deg: float) -> None:
        angle_rad = radians(angle_deg)
        self.direction = self.direction.rotate_around_axis(axis, angle_rad).normalize()
        self.up_hint = self.up_hint.rotate_around_axis(axis, angle_rad).normalize()
        self.update_camera()

    def zoom(self, factor: float) -> None:
        self.fov_deg *= factor
        self.update_camera()

    def copy(self) -> PinholeCamera:
        return PinholeCamera(
            fov_deg=self.fov_deg,
            aspect_ratio=self.aspect_ratio,
            origin=Vertex(self.origin.x, self.origin.y, self.origin.z),
            direction=Vector(self.direction.x, self.direction.y, self.direction.z),
            up_hint=Vector(self.up_hint.x, self.up_hint.y, self.up_hint.z),
        )