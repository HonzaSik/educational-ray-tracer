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

    @property
    def aspect_ratio(self) -> float:
        return self._w / self._h


class Resolution(Enum):
    """
    Common screen resolutions as (width, height) tuples. You can also create custom resolutions with Resolution.custom(width, height).
    """
    # Common 16:9 resolutions
    R144p = (256, 144)
    R240p = (426, 240)
    R360p = (640, 360)
    R480p = (854, 480)
    HD = (1280, 720)
    FullHD = (1920, 1080)
    QHD = (2560, 1440)
    UHD4K = (3840, 2160)

    # Common 4:3 resolutions
    R240p_4_3 = (320, 240)  # QVGA
    R360p_4_3 = (480, 360)
    R480p_4_3 = (640, 480)  # VGA
    SVGA = (800, 600)
    XGA = (1024, 768)
    SXGA_4_3 = (1280, 960)
    UXGA = (1600, 1200)
    QXGA = (2048, 1536)

    # 1:1 resolutions
    R256p_1_1 = (256, 256)
    R512p_1_1 = (512, 512)
    R1024p_1_1 = (1024, 1024)
    R2048p_1_1 = (2048, 2048)
    R4096p_1_1 = (4096, 4096)

    # Ultrawide resolutions
    UW_HD = (2560, 1080)  # Ultrawide Full HD
    UW_QHD = (3440, 1440)  # Ultrawide QHD
    UW_4K = (5120, 2160)  # Ultrawide 4K


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
