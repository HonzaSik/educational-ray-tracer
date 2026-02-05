from dataclasses import dataclass, field
import math
from src import Vertex
from src.material.textures.noise.normal_base import Noise
from src.math.helpers import interpolate, perlin_fade
import random

# seed for same permutation each run
random.seed(42)
perm = list(range(256))
# shuffle the permutation table to get pseudo-random gradients
random.shuffle(perm)

#This Perlin noise implementation is based on the reference algorithm described by Perlin
def _grad(h: int, x: float, y: float, z: float) -> float:
    # reduce h to 4 bits - 16 values
    h &= 15
    # first 8 cases refer x, next 8 to y (axis U)
    u = x if h < 8 else y
    # 0-3: y, 12,14: x; else z (axis V) this way mixes directions to not to align with axes
    v = y if h < 4 else (x if h in (12, 14) else z)
    # final gradient value is a combination of the two axes with signs directed by bits 0 and 1 of h
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)


@dataclass
class PerlinNoise(Noise):
    #for speed, we duplicate the permutation list
    perm: list[int] = field(default_factory=lambda: perm + perm)

    def value(self, point: Vertex) -> float:
        # finds in which cube the point is located
        X = math.floor(point.x) & 255
        Y = math.floor(point.y) & 255
        Z = math.floor(point.z) & 255

        # find exact location in cube of the point [0,1]
        x = point.x - math.floor(point.x)
        y = point.y - math.floor(point.y)
        z = point.z - math.floor(point.z)

        # smooth the location with fade function to look smoother
        u = perlin_fade(x)
        v = perlin_fade(y)
        w = perlin_fade(z)

        # pick random gradients from permutation table for each of the cube's corners
        # 8 pseudo random locations
        A = self.perm[X] + Y
        AA = self.perm[A] + Z
        AB = self.perm[A + 1] + Z
        B = self.perm[X + 1] + Y
        BA = self.perm[B] + Z
        BB = self.perm[B + 1] + Z

        # gets how much each corner contributes to the final value based on the gradient and the location in the cube
        g000 = _grad(self.perm[AA], x, y, z)
        g100 = _grad(self.perm[BA], x - 1, y, z)
        g010 = _grad(self.perm[AB], x, y - 1, z)
        g110 = _grad(self.perm[BB], x - 1, y - 1, z)
        g001 = _grad(self.perm[AA + 1], x, y, z - 1)
        g101 = _grad(self.perm[BA + 1], x - 1, y, z - 1)
        g011 = _grad(self.perm[AB + 1], x, y - 1, z - 1)
        g111 = _grad(self.perm[BB + 1], x - 1, y - 1, z - 1)

        # blend all contributions together by interpolating along each axis
        # from 8->4
        x00 = interpolate(g000, g100, u)
        x10 = interpolate(g010, g110, u)
        x01 = interpolate(g001, g101, u)
        x11 = interpolate(g011, g111, u)

        # from 4->2
        y0 = interpolate(x00, x10, v)
        y1 = interpolate(x01, x11, v)

        # from 2->1
        return interpolate(y0, y1, w)
