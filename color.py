from enum import Enum
from vec3 import Vec3

class Color(Enum):
    Black   = Vec3(0.0, 0.0, 0.0)
    White   = Vec3(1.0, 1.0, 1.0)
    Red     = Vec3(1.0, 0.0, 0.0)
    Green   = Vec3(0.0, 1.0, 0.0)
    Blue    = Vec3(0.0, 0.0, 1.0)
    Yellow  = Vec3(1.0, 1.0, 0.0)
    Cyan    = Vec3(0.0, 1.0, 1.0)
    Magenta = Vec3(1.0, 0.0, 1.0)
    Gray    = Vec3(0.5, 0.5, 0.5)
    SkyBlue = Vec3(0.262, 0.400, 0.455)

    def __iter__(self):
        return iter((self.value.x, self.value.y, self.value.z))

    @property
    def vec3(self) -> Vec3:
        return self.value

    @staticmethod
    def custom(r: float, g: float, b: float) -> Vec3:
        return Vec3(r, g, b)
