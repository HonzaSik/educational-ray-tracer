from dataclasses import dataclass, field

from src.material.textures.noise.noise import Noise
from src.material.textures.noise.perlin_noise import PerlinNoise


@dataclass
class RidgeNoise(Noise):
    """
    Ridge noise texture. Similar to FBM noise but emphasizes ridges and valleys by inverting the absolute value of the noise and squaring it. This creates sharper features that resemble mountainous terrain.
     - base: The base noise function to use (default is Perlin noise)
     - octaves: Number of noise layers to combine
     - lacunarity: Frequency multiplier for each octave (default 2.0 means each octave has double the frequency of the previous one)
     - gain: Amplitude multiplier for each octave (default 0.5 means each octave has half the amplitude of the previous one)
     The final noise value is a weighted sum of the octaves, normalized to roughly [0, 1] and then scaled by the strength property from the Noise base class.
     Key idea: n = 1.0 - abs(n) creates ridges where the original noise had peaks, and squaring it sharpens those ridges.
     This type of noise is often used for generating terrain with pronounced features like mountains and valleys.
    """
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
            n = 1.0 - abs(n)
            n *= n
            total += amp * n

            freq *= self.lacunarity
            amp *= self.gain

        return total * self.strength
