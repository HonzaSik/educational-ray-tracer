from dataclasses import dataclass, field

from src.material.material.material import MaterialSample
from src.material.material.phong_material import PhongMaterial

from src.material.textures.noise.normal_base import Noise
from src.material.textures.noise.perlin_noise import PerlinNoise


def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

def smoothstep(e0: float, e1: float, x: float) -> float:
    t = clamp01((x - e0) / (e1 - e0))
    return t * t * (3.0 - 2.0 * t)

@dataclass
class RockMaterial(PhongMaterial):
    # noise driving color / roughness variation
    color_noise: Noise = field(default_factory=PerlinNoise)
    color_scale: float = 3.0

    # noise driving bump (normal perturbation)
    bump_noise: Noise | None = None

    def sample(self, hit: "SurfaceInteraction") -> MaterialSample:
        p = hit.point  # world mapping for rocks; for planets use hit.normal.normalize()

        t = 0.5 * self.color_noise.value(p * self.color_scale) + 0.5  # -> [0,1]
        t = smoothstep(0.35, 0.75, t)  # nicer mask

        # tint between darker and your base_color
        dark = self.base_color * 0.55
        albedo = dark * (1.0 - t) + self.base_color * t

        # shininess varies too (rough patches)
        shin = self.shininess * (0.6 + 0.8 * (1.0 - t))

        # choose bump noise: if not provided, reuse color_noise but stronger scale/strength via its own settings
        nnoise = self.bump_noise if self.bump_noise is not None else self.normal_noise

        return MaterialSample(
            base_color=albedo,
            spec_color=self.spec_color,
            shininess=float(shin),
            ior=self.ior,
            opacity=1.0 - self.transparency,
            normal_noise=nnoise,
        )
