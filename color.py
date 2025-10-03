from __future__ import annotations
from typing import Iterator
from vec3 import Vec3


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

def _clamp255(n: int) -> int:
    return 0 if n < 0 else 255 if n > 255 else n


class Color(Vec3):
    """
    Color class inheriting from Vec3, with color-specific methods.
    """

    # --- Factories ---
    @staticmethod
    def custom_albedo(r: float, g: float, b: float) -> Color:
        """Create from floats in 0..1"""
        return Color(_clamp01(r), _clamp01(g), _clamp01(b))

    @staticmethod
    def custom_rgb(r: int, g: int, b: int) -> Color:
        """Create from integers in 0..255"""
        return Color(_clamp255(r) / 255.0,
                     _clamp255(g) / 255.0,
                     _clamp255(b) / 255.0)

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
        """Convert to 8-bit RGB tuple"""
        return (_clamp255(int(self.r * 255)),
                _clamp255(int(self.g * 255)),
                _clamp255(int(self.b * 255)))

    @classmethod
    def from_hdr(cls, SKYBOX_HDR, direction) -> Color:
        # Placeholder for sampling an HDR environment map
        return cls(0.5, 0.5, 0.5)  # TODO implement properly


# --- Named Presets ---
Color.Black = Color(0.0, 0.0, 0.0)
Color.White = Color(1.0, 1.0, 1.0)
Color.Red   = Color(1.0, 0.0, 0.0)
Color.Green = Color(0.0, 1.0, 0.0)
Color.Blue  = Color(0.0, 0.0, 1.0)
