# src/shading/compare_checker_shader.py
from dataclasses import dataclass
from .shading_model import ShadingModel
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.light import Light
from src.material.color import Color
from src.math import Vector, Vertex
from enum import Enum
import math


def _hash_checker(v: Vertex, scale: float) -> int:
    """Classic checkerboard pattern (alternating X/Z cells)."""
    coord = v * scale
    xi, zi = math.floor(coord.x), math.floor(coord.z)
    return (int(xi) + int(zi)) & 1  # 0 or 1


def _hash_checked_lines(v: Vertex, scale: float) -> int:
    """Diagonal grid pattern with lines double width."""
    coord = v * scale
    x_cell = math.floor(coord.x)
    y_cell = math.floor(coord.y)
    line_x = (coord.x - x_cell) < 0.5
    line_y = (coord.y - y_cell) < 0.5
    return 0 if line_x ^ line_y else 1


def _hash_stripes(v: Vertex, scale: float) -> int:
    """Vertical stripe pattern (alternating by X axis)."""
    coord = v * scale
    return int(math.floor(coord.x)) % 2


def _hash_circles(v: Vertex, scale: float) -> int:
    """Concentric rings in XZ plane."""
    r = math.sqrt(v.x * v.x + v.z * v.z)
    ring = math.floor(r * scale)
    return ring % 2


def _half_left_right(x: float) -> int:
    """Left half is 0, right half is 1."""
    return 0 if x < 0 else 1


class HashMethod(Enum):
    CHECKER = "checker"
    CHECKED_LINES = "checked_lines"
    STRIPES = "stripes"
    CIRCLES = "circles"
    HALF_IMAGE = "half_image"


@dataclass
class DiffShader(ShadingModel):
    """
    Compares two shading models side-by-side using a procedural pattern.
    """
    a: ShadingModel
    b: ShadingModel
    scale: float = 4.0
    hash_method: HashMethod = HashMethod.CHECKER


    def _select_hash(self, v: Vertex) -> int:
        """Return 0/1 based on the selected pattern."""
        if self.hash_method == HashMethod.CHECKER:
            return _hash_checker(v, self.scale)
        elif self.hash_method == HashMethod.CHECKED_LINES:
            return _hash_checked_lines(v, self.scale)
        elif self.hash_method == HashMethod.STRIPES:
            return _hash_stripes(v, self.scale)
        elif self.hash_method == HashMethod.CIRCLES:
            return _hash_circles(v, self.scale)
        elif self.hash_method == HashMethod.HALF_IMAGE:
            return _half_left_right(v.x)
        else:
            return 0


    def shade(self, hit: SurfaceInteraction, light: Light | None, view_dir: Vector) -> Color:
        """
        Shade using either shader A or B based on the selected pattern using hashing.
        0 = shader A, 1 = shader B
        """
        use_a = self._select_hash(hit.geom.point) == 0
        color = (self.a if use_a else self.b).shade(hit, light, view_dir)
        return color.clamp_01()

    def shade_multiple_lights(self, hit, lights, view_dir) -> Color:
        """
        Shade using either shader A or B based on the selected pattern using hashing.
        0 = shader A, 1 = shader B
        """
        use_a = self._select_hash(hit.geom.point) == 0
        return (self.a if use_a else self.b).shade_multiple_lights(view_dir = view_dir, lights = lights, hit = hit)