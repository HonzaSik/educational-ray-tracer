from __future__ import annotations
from dataclasses import dataclass
from numpy import cos, sin, sqrt

Number = float | int

@dataclass(slots=True)
class Vec3:
    """
    3D vector with basic operations.
    Can be used for points, directions, colors, etc.
    3 floats, no allocations except for operations that return new Vec3.
    """
    x: float
    y: float
    z: float

    # basic ops (return new objects)
    def __neg__(self) -> Vec3:
        return Vec3(-self.x, -self.y, -self.z)

    def __add__(self, o: Vec3) -> Vec3:
        return Vec3(self.x+o.x, self.y+o.y, self.z+o.z)

    def __sub__(self, o: Vec3) -> Vec3:
        return Vec3(self.x-o.x, self.y-o.y, self.z-o.z)

    def __mul__(self, s: Number) -> Vec3:
        return Vec3(self.x*s, self.y*s, self.z*s)

    __rmul__ = __mul__

    def __truediv__(self, s: Number) -> Vec3:
        inv = 1.0/float(s)
        return Vec3(self.x*inv, self.y*inv, self.z*inv)

    # in-place ops (modify self, return self)
    def iadd(self, o: Vec3) -> Vec3:
        self.x += o.x
        self.y += o.y
        self.z += o.z
        return self

    def isub(self, o: Vec3) -> Vec3:
        self.x -= o.x
        self.y -= o.y
        self.z -= o.z
        return self

    def imul(self, s: Number) -> Vec3:
        s = float(s)
        self.x *= s
        self.y *= s
        self.z *= s
        return self

    def idiv(self, s: Number) -> Vec3:
        inv = 1.0/float(s)
        self.x *= inv
        self.y *= inv
        self.z *= inv
        return self

    # Hadamard products (component-wise multiplication)
    def hadamard(self, o: Vec3) -> Vec3:
        return Vec3(self.x*o.x, self.y*o.y, self.z*o.z)

    def hadamard_ip(self, o: Vec3) -> Vec3:
        self.x*=o.x
        self.y*=o.y
        self.z*=o.z
        return self

    # vector operations
    def dot(self, o: Vec3) -> float:
        return self.x*o.x + self.y*o.y + self.z*o.z

    def cross(self, o: Vec3) -> Vec3:
        return Vec3(
            self.y*o.z - self.z*o.y,
            self.z*o.x - self.x*o.z,
            self.x*o.y - self.y*o.x
        )

    # length and normalization
    def norm(self) -> float:
        return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    def normalize(self) -> Vec3:
        """
        Return a safely normalized copy of this vector.
        If the vector has zero length, returns a zero vector.
        0,0,0 -> 0,0,0
        1,0,0 -> 1,0,0
        1,1,1 -> 0.577,0.577,0.577
        10,0,0 -> 1,0,0
        :return:
        """
        n2 = self.x*self.x + self.y*self.y + self.z*self.z
        if n2 == 0.0: return Vec3(0.0,0.0,0.0)
        inv = 1.0 / sqrt(n2)
        return Vec3(self.x*inv, self.y*inv, self.z*inv)

    def normalize_ip(self) -> Vec3:
        """
        Safely normalize this vector in-place so that it has length 1 and no allocation is done.
        If the vector has zero length, sets it to zero vector.
        :return:
        """
        n2 = self.x*self.x + self.y*self.y + self.z*self.z
        if n2 == 0.0: self.x = self.y = self.z = 0.0
        else:
            inv = 1.0 / sqrt(n2)
            self.x *= inv; self.y *= inv; self.z *= inv
        return self

    def clamp01(self) -> Vec3:
        return Vec3(
            0.0 if self.x < 0.0 else 1.0 if self.x > 1.0 else self.x,
            0.0 if self.y < 0.0 else 1.0 if self.y > 1.0 else self.y,
            0.0 if self.z < 0.0 else 1.0 if self.z > 1.0 else self.z,
        )

    def clamp01_ip(self) -> Vec3:
        self.x = 0.0 if self.x < 0.0 else 1.0 if self.x > 1.0 else self.x
        self.y = 0.0 if self.y < 0.0 else 1.0 if self.y > 1.0 else self.y
        self.z = 0.0 if self.z < 0.0 else 1.0 if self.z > 1.0 else self.z
        return self

    def lerp(self, b: Vec3, t: float) -> Vec3:
        """
        Linear interpolation between this vector (a) and b by t in [0..1]
        :param b: target vector
        :param t: interpolation factor in [0..1]
        :return: interpolated vector
        """
        return Vec3(
            self.x + (b.x - self.x) * t,
            self.y + (b.y - self.y) * t,
            self.z + (b.z - self.z) * t,
        )

    def orthonormal_basis(self) -> tuple[Vec3,Vec3,Vec3]:
        n = self.normalize_ip()
        if abs(n.x) > abs(n.z):
            t = Vec3(-n.y, n.x, 0.0).normalize_ip()
        else:
            t = Vec3(0.0, -n.z, n.y).normalize_ip()
        b = n.cross(t)
        return t, b, n

    def __repr__(self) -> str:
        """
        String representation
        :return: str
        """
        return f"Vec3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"


    def __radd__(self, o):
        """
        Add Vec3
        :param o: Vec3
        :return: Vec3
        """
        if isinstance(o, Vec3):
            return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __mul__(self, o):
        """
        Multiply by scalar
        :param o: scalar or Vec3
        :return: Vec3
        """
        if isinstance(o, (int, float)):
            return Vec3(self.x * o, self.y * o, self.z * o)
        if isinstance(o, Vec3):
            return Vec3(self.x * o.x, self.y * o.y, self.z * o.z)


    def rotate_around_axis(self, axis: Vec3, angle_rad: float) -> Vec3:
        """
        Rotate this vector around given axis by angle in radians using Rodrigues' rotation formula.
        """
        k = axis.normalize()
        v = self
        cos_theta = cos(angle_rad)
        sin_theta = sin(angle_rad)
        rotated = (v * cos_theta +
                   k.cross(v) * sin_theta +
                   k * (k.dot(v)) * (1 - cos_theta))
        return rotated