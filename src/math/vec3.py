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

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

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

    def __rtruediv__(self, o: "Vec3 | _Scalar") -> "Vec3":
        if isinstance(o, Vec3):
            return Vec3(o.x / self.x, o.y / self.y, o.z / self.z)
        if isinstance(o, _Scalar):
            return Vec3(o / self.x, o / self.y, o / self.z)
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

    def clamp01(self) -> "Vec3":
        return Vec3(
            0.0 if self.x < 0.0 else 1.0 if self.x > 1.0 else self.x,
            0.0 if self.y < 0.0 else 1.0 if self.y > 1.0 else self.y,
            0.0 if self.z < 0.0 else 1.0 if self.z > 1.0 else self.z,
        )

    def normalize(self) -> "Vec3":
        n = self.norm()
        return self / n if n > 0 else Vec3(0.0, 0.0, 0.0)

    def interpolate_vec3(self: Vec3, b: Vec3, t: float) -> Vec3:
        """
        Linear interpolation between two Vec3 by factor t in [0, 1].
        :param self: point a (Vec3)
        :param b: point b (Vec3)
        :param t: interpolation factor
        :return: interpolated Vec3
        """
        return self * (1.0 - t) + b * t

    def orthonormal_basis(self) -> tuple["Vec3", "Vec3", "Vec3"]:
        """
        Generate an orthonormal basis (tangent, bitangent, normal) from a given normal vector.
        :param n: normal vector (must be normalized)
        :return: tuple of (tangent, bitangent, normal)
        """
        n = self.normalize()  # ensure normal is normalized
        if abs(n.x) > abs(n.z):
            tangent = Vec3(-n.y, n.x, 0.0).normalize()
        else:
            tangent = Vec3(0.0, -n.z, n.y).normalize()
        bitangent = n.cross(tangent)
        return tangent, bitangent, n
