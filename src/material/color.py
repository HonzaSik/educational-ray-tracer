from __future__ import annotations
from typing import Iterator
from src.math import Vec3
from src.math.helpers import interpolate

_skybox_cache = {}

def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

def clamp255(n: int) -> int:
    return 0 if n < 0 else 255 if n > 255 else n

def to_u8(v: float) -> int:
    """
    Convert float color component in [0, 1] to uint8 [0, 255].
    Apply gamma correction (gamma=2.2).
    :param v: input float color component
    :return: uint8 color component
    """
    v = max(0.0, min(1.0, v))
    v = v ** (1.0 / 2.2) #todo gamma correction configurable?
    return int(255.99 * v)

def interpolate_color(a: Color, b: Color, t: float) -> Color:
    """
    Linear interpolation between two Vec3 by factor t in [0, 1].
    :param a: point a (Vec3)
    :param b: point b (Vec3)
    :param t: interpolation factor
    :return: interpolated Vec3
    """
    return Color(
        interpolate(a.r, b.r, t),
        interpolate(a.g, b.g, t),
        interpolate(a.b, b.b, t)
    )

def to_u8_color(col: Color) -> Color:
    """
    Convert Vec3 color in [0, 1] to tuple of uint8 [0, 255].
    :param col: input Vec3 color
    :return: tuple of uint8 color components
    """
    return Color.custom_rgb(to_u8(col.r), to_u8(col.g), to_u8(col.b))

def clamp_color01(col: Color) -> Color:
    """
    Clamp Vec3 color components to [0, 1].
    :param col: input Vec3 color
    :return: clamped Vec3 color
    """
    return Color(
        clamp01(col.x),
        clamp01(col.y),
        clamp01(col.z)
    )

def clamp_color255(col: Color) -> Color:
    """
    Clamp Vec3 color components to [0, 255].
    :param col: input Vec3 color
    :return: clamped Vec3 color
    """
    return Color.custom_rgb(
        clamp255(int(col.x * 255)),
        clamp255(int(col.y * 255)),
        clamp255(int(col.z * 255))
    )

class Color(Vec3):
    """
    Color class inheriting from Vec3, with color-specific methods.
    """

    # --- Factories ---
    @staticmethod
    def custom_albedo(r: float, g: float, b: float) -> Color:
        """Create from floats in 0..1"""
        return Color(clamp01(r), clamp01(g), clamp01(b))

    @staticmethod
    def custom_rgb(r: int, g: int, b: int) -> Color:
        """Create from integers in 0..255"""
        return Color(clamp255(r) / 255.0,
                     clamp255(g) / 255.0,
                     clamp255(b) / 255.0)

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
        return (clamp255(int(self.r * 255)),
                clamp255(int(self.g * 255)),
                clamp255(int(self.b * 255)))

    @classmethod
    def background_color(cls, direction, skybox=None) -> Color:
        if skybox is not None:
            return Color.from_hdr(skybox, direction)
        #normalize direction
        direction = direction.normalize()

        t = 0.5 * (direction.y + 1.0)
        return (1.0 - t) * Color.White + t * Color.custom_rgb(100, 100, 255)

    @classmethod
    def from_hdr(cls, skybox, direction) -> Color:
        """
        Gets color from skybox in given direction. If skybox is not provided or error occurs, returns a gradient color.
        :param skybox: Path to HDR image file or SkyboxHDR instance
        :param direction: Direction vector to sample color
        :return: Color of the skybox in the given direction
        """

        if isinstance(skybox, str):
            # Lazy load SkyboxHDR
            from src.scene.skybox import SkyboxHDR

            try:
                # Load skybox if not cached
                if skybox not in _skybox_cache:
                    _skybox_cache[skybox] = SkyboxHDR(skybox)

                # Retrieve from cache if already loaded
                skybox = _skybox_cache[skybox]

                color = skybox.color_from_dir(direction)
                return cls(color.x, color.y, color.z)

            except Exception as e:
                print(f"Warning: Failed to load skybox '{skybox}': {e}")

        return cls.background_color(direction, skybox=None)

# --- Named Presets ---
Color.Black = Color(0.0, 0.0, 0.0)
Color.White = Color(1.0, 1.0, 1.0)
Color.Red   = Color(1.0, 0.0, 0.0)
Color.Green = Color(0.0, 1.0, 0.0)
Color.Blue  = Color(0.0, 0.0, 1.0)
