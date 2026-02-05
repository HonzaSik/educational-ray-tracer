from __future__ import annotations
from dataclasses import dataclass, field
from src.material.textures.noise.normal_base import Noise
from src.material.textures.noise.perlin_noise import PerlinNoise
from src.math.vertex import Vertex
from src.math.vector import Vector

@dataclass
class FBMNoise(Noise):
    base: PerlinNoise = field(default_factory=PerlinNoise)
    octaves: int = 5
    lacunarity: float = 2.0   # frequency multiplier per octave
    gain: float = 0.5         # amplitude multiplier per octave

    def value(self, p: Vertex | Vector) -> float:
        # apply scale + offset once
        x = (p + self.offset) * self.scale

        amp = 1.0
        freq = 1.0
        total = 0.0
        amp_sum = 0.0

        for _ in range(self.octaves):
            total += amp * self.base.value(x * freq)
            amp_sum += amp
            amp *= self.gain
            freq *= self.lacunarity

        # normalize to roughly [-1, 1]
        if amp_sum > 0:
            total /= amp_sum

        return total * self.strength
