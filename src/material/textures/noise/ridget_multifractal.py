from dataclasses import dataclass, field

from src.material.textures.noise.normal_base import Noise
from src.material.textures.noise.perlin_noise import PerlinNoise


@dataclass
class RidgeNoise(Noise):
    base: PerlinNoise = field(default_factory=PerlinNoise)
    octaves: int = 5
    lacunarity: float = 2.0
    gain: float = 0.5

    def value(self, p):
        x = (p + self.offset) * self.scale

        amp = 0.5
        freq = 1.0
        total = 0.0

        for _ in range(self.octaves):
            n = self.base.value(x * freq)
            n = 1.0 - abs(n)       # key idea
            n *= n                # sharpen ridges
            total += amp * n

            freq *= self.lacunarity
            amp *= self.gain

        return total * self.strength
