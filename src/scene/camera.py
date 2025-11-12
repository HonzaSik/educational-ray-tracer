from __future__ import annotations
from dataclasses import dataclass, field
from math import tan, radians
from src.math import Vertex, Vector
from src.io.resolution import Resolution
from src.geometry.ray import Ray

@dataclass
class Camera:
    """
    Simple pinhole camera model.
    fov: vertical field of view in degrees
    resolution: image resolution (width, height)
    """
    fov: float = 70.0
    resolution: Resolution = Resolution.R360p
    origin: Vertex = field(default_factory=lambda: Vertex(0, 0, 0))
    direction: Vector = field(default_factory=lambda: Vector(0, 0, -1)) # looking down -Z
    up_hint: Vector = field(default_factory=lambda: Vector(0, 1, 0)) # up direction

    def __post_init__(self):
        """
        Calculate camera basis vectors and image plane dimensions.
        :return: None
        """
        # normalize forward
        fwd = self.direction.normalize()
        # guard against collinearity with up
        if abs(fwd.dot(self.up_hint)) > 0.999:
            self.up_hint = Vector(1, 0, 0) # use right vector if collinear

        # build ONB (right, true_up, forward)
        w = (-fwd).normalize()                       # camera looks along -w
        right = self.up_hint.cross(w).normalize()
        true_up = w.cross(right)

        aspect = self.resolution.width / self.resolution.height
        theta = radians(self.fov)
        half_height = tan(theta * 0.5)
        half_width  = aspect * half_height

        self.fwd = fwd
        self.right = right
        self.up = true_up
        self.half_width = half_width
        self.half_height = half_height

    def make_ray(self, u: float, v: float) -> Ray:
        """
        u, v in [-0.5, 0.5]; (-0.5,-0.5)=bottom-left, (+0.5,+0.5)=top-right
        Image plane is 1 unit in front of the camera.
        """
        # point on image plane: origin + (-w) + x*right + y*up
        x = u * (2.0 * self.half_width)
        y = v * (2.0 * self.half_height)
        img_plane_center = self.origin + self.fwd  # 1 unit ahead
        pixel_pos = img_plane_center + self.right * x + self.up * y
        return Ray(self.origin, (pixel_pos - self.origin).normalize())

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

        self.__post_init__()
        pass


    def zoom(self, factor: float) -> None:
        """
        Zoom camera by changing fov. factor < 1.0 zooms in, > 1.0 zooms out.
        """
        self.fov *= factor
        self.__post_init__()

    def set_resolution(self, res) -> None:
        self.resolution = res
        self.__post_init__()

    def copy(self) -> Camera:
        return Camera(
            fov=self.fov,
            resolution=self.resolution,
            origin=Vertex(self.origin.x, self.origin.y, self.origin.z),
            direction=Vector(self.direction.x, self.direction.y, self.direction.z),
            up_hint=Vector(self.up_hint.x, self.up_hint.y, self.up_hint.z)
        )