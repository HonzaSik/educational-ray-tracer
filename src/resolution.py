from enum import Enum
from typing import Tuple

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
    def custom(width: int, height: int) -> Tuple[int, int]:
        """
        Create a custom resolution.
        :param width: Width in pixels
        :param height: Height in pixels
        :return: (width, height) tuple
        """
        return width, height
