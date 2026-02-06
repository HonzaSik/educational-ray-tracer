from __future__ import annotations
from dataclasses import dataclass
from typing import Union, Iterable, Any
import numpy as np
from src.math import Vec3
from src.math.helpers import interpolate

DT = np.float32
_skybox_cache: dict[str, "SkyboxHDR"] = {}


def _to_u8_fast(v: float) -> int:
    if v <= 0.0: return 0
    if v >= 1.0: return 255
    return int(v * 255.0 + 0.5)


def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def clamp_color255(col: Color) -> Color:
    r, g, b = col.as_rgb()
    return Color.custom_rgb(
        clamp255(int(r * 255)),
        clamp255(int(g * 255)),
        clamp255(int(b * 255)),
    )


def clamp_color01(col: Color) -> Color:
    return Color(np.clip(col.data, 0.0, 1.0))


def clamp255(n: int) -> int:
    return 0 if n < 0 else 255 if n > 255 else n


def to_u8(v: float) -> int:
    return _to_u8_fast(v)


def _as_np3(v: Union[Vec3, Color, np.ndarray, Iterable[float]]) -> np.ndarray:
    if isinstance(v, Vec3):
        return np.array([v.x, v.y, v.z], dtype=DT)
    elif isinstance(v, Color):
        r, g, b = v.as_rgb()
        return np.array([float(r), float(g), float(b)], dtype=DT)
    else:
        arr = np.asarray(v, dtype=DT).reshape(-1)
        if arr.shape[0] < 3:
            # fill missing components
            filled = np.zeros(3, dtype=DT)
            for i in range(arr.shape[0]):
                filled[i] = arr[i]
            for i in range(arr.shape[0], 3):
                filled[i] = filled[i - 1]
            return filled
        return arr[:3]


def interpolate_rgb_color(a: Color, b: Color, t: float) -> Color:
    ar, ag, ab = a.as_rgb()
    br, bg, bb = b.as_rgb()
    return Color(
        interpolate(ar, br, t),
        interpolate(ag, bg, t),
        interpolate(ab, bb, t),
    )


def to_u8_color(col: Color) -> Color:
    r, g, b = col.as_rgb()
    return Color.custom_rgb(
        to_u8(r),
        to_u8(g),
        to_u8(b),
    )


@dataclass
class Color:
    """
    Represents color whatever way you want: as RGB color, or as 3D vector, also supports numpy array operations.
    Can be constructed from individual float components, from iterable of floats, or from numpy array.
    """
    data: np.ndarray

    def __init__(self, *values: float | Iterable[float] | np.ndarray):
        if len(values) == 1 and not isinstance(values[0], (int, float)):
            arr = np.asarray(values[0], dtype=DT).reshape(-1)
        else:
            arr = np.asarray(values, dtype=DT).reshape(-1)
        self.data = arr.astype(DT)

    @property
    def r(self) -> float:
        return float(self.data[0])

    @r.setter
    def r(self, value: float) -> None:
        self.data[0] = DT(value)

    @property
    def g(self) -> float:
        return float(self.data[1])

    @g.setter
    def g(self, value: float) -> None:
        self.data[1] = DT(value)

    @property
    def b(self) -> float:
        return float(self.data[2])

    @b.setter
    def b(self, value: float) -> None:
        self.data[2] = DT(value)

    @property
    def x(self) -> float:
        return self.r

    @property
    def y(self) -> float:
        return self.g

    @property
    def z(self) -> float:
        return self.b

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return self.data.shape[0]

    def _binary_operation(self, other: Any, op) -> Color:
        if isinstance(other, Color):
            return Color(op(self.data, other.data))
        else:
            return Color(op(self.data, other))

    def __add__(self, other: Any) -> Color:
        return self._binary_operation(other, np.add)

    def __radd__(self, other: Any) -> Color:
        return self.__add__(other)

    def __sub__(self, other: Any) -> Color:
        return self._binary_operation(other, np.subtract)

    def __mul__(self, other: Any) -> Color:
        return self._binary_operation(other, np.multiply)

    def __rmul__(self, other: Any) -> Color:
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> Color:
        return self._binary_operation(other, np.divide)

    def to_vec3(self) -> Vec3:
        if len(self.data) < 3:
            r = float(self.data[0]) if len(self.data) > 0 else 0.0
            g = float(self.data[1]) if len(self.data) > 1 else r
            b = r
        else:
            r, g, b = map(float, self.data[:3])
        return Vec3(r, g, b)

    def as_rgb(self) -> tuple[float, float, float]:
        """Return (r,g,b) from Color, filling missing components as needed. Or (0,0,0) if empty."""
        n = len(self.data)
        if n == 0:
            return 0.0, 0.0, 0.0
        if n == 1:
            v = float(self.data[0])
            return v, v, v
        if n == 2:
            r = float(self.data[0])
            g = float(self.data[1])
            return r, g, g
        r, g, b = map(float, self.data[:3])
        return r, g, b

    @classmethod
    def from_vec3(cls, v: Vec3) -> Color:
        return cls(v.x, v.y, v.z)

    @staticmethod
    def linear_rgb(r: float, g: float, b: float) -> Color:
        """
        Create a custom color with specified red, green, and blue components.
        :param r: red component
        :param g: green component
        :param b: blue component
        :return: Color instance clamped to [0..1]
        """
        return Color(clamp01(r), clamp01(g), clamp01(b))

    @staticmethod
    def custom_rgb(r: int, g: int, b: int) -> Color:
        return Color(clamp255(r) / 255.0, clamp255(g) / 255.0, clamp255(b) / 255.0)

    def to_rgb8(self) -> tuple[int, int, int]:
        r, g, b = self.as_rgb()
        return (
            clamp255(int(r * 255)),
            clamp255(int(g * 255)),
            clamp255(int(b * 255)),
        )

    def clamp_01(self) -> Color:
        return Color(np.clip(self.data, 0.0, 1.0))

    @classmethod
    def background_color(cls, direction, skybox=None) -> Color:
        """
        Generate a background color based on the given direction and optional skybox.
        :param direction: Vec3 | np.ndarray(3,)
        :param skybox: str path or SkyboxHDR instance
        :return: Color
        """
        if skybox is not None:
            return cls.from_hdr(skybox, direction)

        direction = _as_np3(direction)
        normal = float(np.linalg.norm(direction))

        if normal > 0:
            direction = direction / normal

        y_axis = 0.5 * (direction[1] + 1.0)
        color = (1.0 - y_axis) * cls.custom_rgb(255, 255, 255) + y_axis * cls.custom_rgb(100, 100, 255)
        return color

    @classmethod
    def from_hdr(cls, skybox, direction) -> Color:
        """
        skybox: str path or SkyboxHDR instance
        direction: Vec3 | np.ndarray(3,)
        """
        # lazy import here to avoid cycles #todo fix cycles
        if isinstance(skybox, str):
            from src.scene.skybox import SkyboxHDR
            try:
                if skybox not in _skybox_cache:
                    _skybox_cache[skybox] = SkyboxHDR(skybox)
                skybox = _skybox_cache[skybox]
            except Exception as e:
                print(f"Warning: Failed to load skybox '{skybox}': {e}")
                return cls.background_color(direction, skybox=None)
        else:
            skybox = skybox

        col = skybox.color_from_dir(direction)

        if isinstance(col, Color):
            r, g, b = col.as_rgb()
            return cls(r, g, b)

        if isinstance(col, Vec3):
            return cls(col.x, col.y, col.z)

        col_np = _as_np3(col)
        return cls(float(col_np[0]), float(col_np[1]), float(col_np[2]))


# color presets
Color.Black = Color(0.0, 0.0, 0.0)
Color.White = Color(1.0, 1.0, 1.0)
Color.Red = Color(1.0, 0.0, 0.0)
Color.Green = Color(0.0, 1.0, 0.0)
Color.Blue = Color(0.0, 0.0, 1.0)
