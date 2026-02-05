from dataclasses import dataclass, field
import math

from src.material.color import clamp01
from src.material.material.material import MaterialSample
from src.material.material.phong_material import PhongMaterial
from src.material.textures.noise.normal_base import Noise
from src.material.textures.noise.perlin_noise import PerlinNoise
from src.math import Vector  # adjust import if needed


@dataclass
class MarbleMaterial(PhongMaterial):
    vein_scale: float = 6.0          # try 4..12
    warp_strength: float = 2.0       # try 0.5..3.0
    vein_sharpness: float = 4.0      # try 2..8
    warp_noise: Noise = field(default_factory=PerlinNoise)
    bump_noise: Noise | None = None
    light_color_factor: float = 1.0
    dark_color_factor: float = 0.75

    def sample(self, hit: "SurfaceInteraction") -> MaterialSample:
        p = hit.point
        dir = Vector(1.0, 0.35, 0.15).normalize()
        u = p.dot(dir)
        w = self.warp_noise.value(p * 1.2)

        phase = (
                u * self.vein_scale
                + w * self.warp_strength
                + 0.3 * self.warp_noise.value(p * 3.7)
        )
        s = 0.5 + 0.5 * math.sin(phase)
        vein = 1.0 - (abs(s - 0.5) * 2.0)
        vein = clamp01(vein)
        veins = vein ** self.vein_sharpness

        light = self.base_color * self.light_color_factor
        dark  = self.base_color * self.dark_color_factor
        albedo = dark * (1.0 - veins) + light * veins

        shin = max(10.0, self.shininess * (0.6 + 0.3 * veins))

        return MaterialSample(
            base_color=albedo,
            spec_color=self.spec_color,
            shininess=float(shin),
            ior=self.ior,
            opacity=1.0 - self.transparency,
            normal_noise=self.bump_noise,
        )