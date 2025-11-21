from __future__ import annotations
from enum import Enum
from typing import Tuple


class CustomResolution:
    _w: int
    _h: int

    def __init__(self, width: int, height: int):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers.")
        self._w = width
        self._h = height

    @property
    def width(self) -> int: return self._w

    @property
    def height(self) -> int: return self._h

    @property
    def size(self) -> Tuple[int, int]: return self._w, self._h

    @property
    def pixels(self) -> int: return self._w * self._h

    def __iter__(self):
        return iter((self._w, self._h))
    def __len__(self):
        return 2
    def __repr__(self) -> str:
        return f"CustomResolution({self._w}x{self._h})"

class Resolution(Enum):
    """
    Common screen resolutions as (width, height) tuples. You can also create custom resolutions with Resolution.custom(width, height).
    """
    R144p   = (256, 144)
    R240p   = (426, 240)
    R360p   = (640, 360)
    R480p  = (854, 480)
    HD      = (1280, 720)
    FullHD  = (1920, 1080)
    QHD     = (2560, 1440)
    UHD4K   = (3840, 2160)
    XGA     = (1024, 768)
    SXGA    = (1280, 1024)

    def __iter__(self):
        # makes unpacking work wihnout .value
        return iter(self.value)

    def __len__(self):
        return 2

    @property
    def width(self) -> int: return self.value[0]

    @property
    def height(self) -> int: return self.value[1]

    @property
    def size(self) -> Tuple[int, int]: return self.value

    @property
    def pixels(self) -> int: return self.width * self.height

    @staticmethod
    def custom(width: int, height: int) -> CustomResolution:
        return CustomResolution(width, height)

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height

