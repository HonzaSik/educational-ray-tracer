from __future__ import annotations
from typing import Iterator, Union
import numpy as np
from src.math import Vec3
from src.math.helpers import interpolate

DT = np.float32
_skybox_cache: dict[str, "SkyboxHDR"] = {}

_LUT_N = 2048
_gamma_u8 = (255.99 * (np.linspace(0.0, 1.0, _LUT_N+1, dtype=DT) ** (DT(1/2.2)))).astype(np.uint8)

def _to_u8_fast(v: float) -> int:
    if v <= 0.0: return 0
    if v >= 1.0: return 255
    return int(_gamma_u8[int(v * _LUT_N)])

def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

def clamp255(n: int) -> int:
    return 0 if n < 0 else 255 if n > 255 else n

def to_u8(v: float) -> int:
    # keep name, route to fast version
    return _to_u8_fast(v)

def _as_np3(v: Union[Vec3, np.ndarray, tuple[float,float,float]]) -> np.ndarray:
    """Borrow/convert to contiguous float32[3] without surprises."""
    if isinstance(v, Vec3):
        # borrow the components; avoid allocations
        return np.array([v.x, v.y, v.z], dtype=DT)
    a = np.asarray(v, dtype=DT).reshape(3)
    return a

def interpolate_color(a: "Color", b: "Color", t: float) -> "Color":
    return Color(
        interpolate(a.r, b.r, t),
        interpolate(a.g, b.g, t),
        interpolate(a.b, b.b, t)
    )

def to_u8_color(col: "Color") -> "Color":
    return Color.custom_rgb(to_u8(col.x), to_u8(col.y), to_u8(col.z))

def clamp_color01(col: "Color") -> "Color":
    return Color(clamp01(col.x), clamp01(col.y), clamp01(col.z))

def clamp_color255(col: "Color") -> "Color":
    return Color.custom_rgb(
        clamp255(int(col.x * 255)),
        clamp255(int(col.y * 255)),
        clamp255(int(col.z * 255))
    )

class Color(Vec3):
    """Color = Vec3 in [0..1] with helpers."""

    @staticmethod
    def custom_albedo(r: float, g: float, b: float) -> "Color":
        """
        Create a custom color with specified red, green, and blue components.
        :param r: red component
        :param g: green component
        :param b: blue component
        :return: Color instance clamped to [0..1]
        """
        return Color(clamp01(r), clamp01(g), clamp01(b))

    @staticmethod
    def custom_rgb(r: int, g: int, b: int) -> "Color":
        return Color(clamp255(r)/255.0, clamp255(g)/255.0, clamp255(b)/255.0)

    # --- Properties ---
    @property
    def r(self) -> float: return self.x
    @property
    def g(self) -> float: return self.y
    @property
    def b(self) -> float: return self.z

    def __iter__(self) -> Iterator[float]:
        yield self.r; yield self.g; yield self.b

    def to_rgb8(self) -> tuple[int, int, int]:
        return (clamp255(int(self.r * 255)),
                clamp255(int(self.g * 255)),
                clamp255(int(self.b * 255)))

    @classmethod
    def background_color(cls, direction, skybox=None) -> "Color":
        if skybox is not None:
            return cls.from_hdr(skybox, direction)

        d = _as_np3(direction)                      # accept Vec3 or np
        n = float(np.linalg.norm(d))
        if n > 0: d = d / n
        t = 0.5 * (d[1] + 1.0)                      # y component
        return (1.0 - t) * cls.White + t * cls.custom_rgb(100, 100, 255)

    @classmethod
    def from_hdr(cls, skybox, direction) -> "Color":
        """
        skybox: str path or SkyboxHDR instance
        direction: Vec3 | np.ndarray(3,)
        """
        # lazy import here to avoid cycles
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
        if isinstance(col, Vec3):
            return cls(col.x, col.y, col.z)
        col_np = _as_np3(col)
        return cls(float(col_np[0]), float(col_np[1]), float(col_np[2]))

# --- Named Presets ---
Color.Black = Color(0.0, 0.0, 0.0)
Color.White = Color(1.0, 1.0, 1.0)
Color.Red   = Color(1.0, 0.0, 0.0)
Color.Green = Color(0.0, 1.0, 0.0)
Color.Blue  = Color(0.0, 0.0, 1.0)
