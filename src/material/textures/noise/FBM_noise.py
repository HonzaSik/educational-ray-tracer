from __future__ import annotations
from dataclasses import dataclass, field
from src.material.textures.noise.noise import Noise
from src.material.textures.noise.perlin_noise import PerlinNoise
from src.math.vertex import Vertex
from src.math.vector import Vector

@dataclass
class FBMNoise(Noise):
    """
    Fractal Brownian Motion (FBM) noise texture. Combines multiple octaves of Perlin noise to create more complex, natural-looking patterns.
     - base: The base noise function to use (default is Perlin noise)
     - octaves: Number of noise layers to combine
     - lacunarity: Frequency multiplier for each octave (default 2.0 means each octave has double the frequency of the previous one)
     - gain: Amplitude multiplier for each octave (default 0.5 means each octave has half the amplitude of the previous one)
     The final noise value is a weighted sum of the octaves, normalized to roughly [-1, 1] and then scaled by the strength property from the Noise base class.
    """
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
        sum = 0.0

        for _ in range(self.octaves):
            total += amp * self.base.value(x * freq)
            sum += amp
            amp *= self.gain
            freq *= self.lacunarity

        # normalize the result to [-1, 1]
        if sum > 0:
            total /= sum

        return total * self.strength
