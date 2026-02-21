from __future__ import annotations
from dataclasses import dataclass, field
from math import tan, radians
from src.math import Vertex, Vector
from src.geometry.ray import Ray


@dataclass
class Camera:
    """
    Simple pinhole camera model.
    fov: vertical field of view in degrees
    resolution: image resolution (width, height)
    """
    fov_deg: float = 70.0
    aspect_ratio: float = 16.0 / 9.0
    origin: Vertex = field(default_factory=lambda: Vertex(0, 0, 0))
    direction: Vector = field(default_factory=lambda: Vector(0, 0, -1))  # looking down -Z
    up_hint: Vector = field(default_factory=lambda: Vector(0, 1, 0))  # up direction

    fwd: Vector = field(init=False)
    right: Vector = field(init=False)
    up: Vector = field(init=False)
    half_width: float = field(init=False)
    half_height: float = field(init=False)

    def __post_init__(self):
        self.update_camera()

    def update_camera(self) -> None:
        """
            Calculate camera basis vectors and image plane dimensions.
            :return: None
        """
        fwd = self.direction.normalize()

        up = self.up_hint
        # if direction is parallel to up_hint, choose a different up vector
        if abs(fwd.dot(up)) > 0.999:
            up = Vector(1, 0, 0)

        # build orthonormal basis
        w = -fwd
        right = up.cross(w).normalize()
        true_up = w.cross(right)

        theta = radians(self.fov_deg)
        half_height = tan(theta * 0.5)
        half_width = self.aspect_ratio * half_height

        self.fwd = fwd
        self.right = right
        self.up = true_up
        self.half_width = half_width
        self.half_height = half_height


    def make_ray(self, u: float, v: float) -> Ray:
        """
        u, v in [-1, 1]
        (-1,-1)=bottom-left, (1,1)=top-right
        Image plane is 1 unit in front of the camera.
        """
        center_plane = self.origin + self.fwd

        position = (
                center_plane
                + self.right * (u * self.half_width)
                + self.up * (v * self.half_height)
        )
        return Ray(self.origin, (position - self.origin).normalize())

    def translate(self, offset: Vector) -> None:
        """
        Move camera by offset vector.
        """
        self.origin += offset

    def rotate_around_axis(self, axis: Vector, angle_deg: float) -> None:
        """
        Rotate camera direction and up_hint around axis by angle in degrees.
        """
        angle_rad = radians(angle_deg)
        # rotate direction
        new_dir = self.direction.rotate_around_axis(axis, angle_rad).normalize()
        self.direction = new_dir
        # rotate up_hint
        new_up = self.up_hint.rotate_around_axis(axis, angle_rad).normalize()
        self.up_hint = new_up

        self.update_camera()
        pass

    def zoom(self, factor: float) -> None:
        """
        Zoom camera by changing fov. factor < 1.0 zooms in, > 1.0 zooms out.
        """
        self.fov_deg *= factor
        self.update_camera()

    def set_aspect_ratio(self, aspect_ratio: float) -> None:
        """
        Set camera aspect ratio and recalculate image plane dimensions.
        """
        self.aspect_ratio = aspect_ratio
        self.update_camera()

    def copy(self) -> Camera:
        return Camera(
            fov_deg=self.fov_deg,
            aspect_ratio=self.aspect_ratio,
            origin=Vertex(self.origin.x, self.origin.y, self.origin.z),
            direction=Vector(self.direction.x, self.direction.y, self.direction.z),
            up_hint=Vector(self.up_hint.x, self.up_hint.y, self.up_hint.z)
        )
