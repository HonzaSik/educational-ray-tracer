from dataclasses import dataclass
import math
from src.material.textures.noise.normal_base import Noise
from src.math.vector import Vector
from src.math.vertex import Vertex

@dataclass
class VoronoiNoise(Noise):
    jitter: float = 1.0   # randomness inside cell

    def _hash(self, ix, iy, iz):
        # simple deterministic hash
        return (
            math.sin(ix * 127.1 + iy * 311.7 + iz * 74.7) * 43758.5453
        ) % 1.0

    def value(self, p: Vertex | Vector) -> float:
        x = (p + self.offset) * self.scale

        ix = int(math.floor(x.x))
        iy = int(math.floor(x.y))
        iz = int(math.floor(x.z))

        min_d = 1e9

        # check neighboring cells
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    cx = ix + dx
                    cy = iy + dy
                    cz = iz + dz

                    # random feature point in cell
                    fx = cx + self._hash(cx, cy, cz) * self.jitter
                    fy = cy + self._hash(cy, cz, cx) * self.jitter
                    fz = cz + self._hash(cz, cx, cy) * self.jitter

                    d = (x - Vector(fx, fy, fz)).length()
                    min_d = min(min_d, d)

        return min_d * self.strength
