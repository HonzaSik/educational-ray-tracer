from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as _np

_Scalar = (int, float, _np.floating)

@dataclass
class Vec3:
    x: float
    y: float
    z: float

    # ---- unary ----
    def __neg__(self) -> "Vec3":
        return Vec3(-self.x, -self.y, -self.z)

    # ---- arithmetic (vec <op> vec | scalar) ----
    def __add__(self, o: "Vec3 | _Scalar") -> "Vec3":
        if isinstance(o, Vec3):
            return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)
        if isinstance(o, _Scalar):
            return Vec3(self.x + o, self.y + o, self.z + o)
        return NotImplemented

    def __radd__(self, o: "Vec3 | _Scalar") -> "Vec3":
        return self.__add__(o)

    def __sub__(self, o: "Vec3 | _Scalar") -> "Vec3":
        if isinstance(o, Vec3):
            return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)
        if isinstance(o, _Scalar):
            return Vec3(self.x - o, self.y - o, self.z - o)
        return NotImplemented

    def __rsub__(self, o: "Vec3 | _Scalar") -> "Vec3":
        if isinstance(o, Vec3):
            return Vec3(o.x - self.x, o.y - self.y, o.z - self.z)
        if isinstance(o, _Scalar):
            return Vec3(o - self.x, o - self.y, o - self.z)
        return NotImplemented

    def __mul__(self, o: "Vec3 | _Scalar") -> "Vec3":
        # componentwise if Vec3, scalar if number
        if isinstance(o, Vec3):
            return Vec3(self.x * o.x, self.y * o.y, self.z * o.z)
        if isinstance(o, _Scalar):
            return Vec3(self.x * o, self.y * o, self.z * o)
        return NotImplemented

    def __rmul__(self, o: "Vec3 | _Scalar") -> "Vec3":
        return self.__mul__(o)

    def __truediv__(self, o: "Vec3 | _Scalar") -> "Vec3":
        if isinstance(o, Vec3):
            return Vec3(self.x / o.x, self.y / o.y, self.z / o.z)
        if isinstance(o, _Scalar):
            return Vec3(self.x / o, self.y / o, self.z / o)
        return NotImplemented

    # ---- vector ops ----
    def dot(self, o: "Vec3") -> float:
        return self.x * o.x + self.y * o.y + self.z * o.z

    def cross(self, o: "Vec3") -> "Vec3":
        return Vec3(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x,
        )

    def norm(self) -> float:
        return math.sqrt(self.dot(self))

    def normalize(self) -> "Vec3":
        n = self.norm()
        return self / n if n > 0 else Vec3(0.0, 0.0, 0.0)
