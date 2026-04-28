from dataclasses import dataclass, field
import math

from jupyter_core.application import base_flags

from src.material.color import clamp01
from src.material.material.phong_material import PhongMaterial, PhongMaterialSample
from src.material.textures.noise.noise import Noise
from src.material.textures.noise.perlin_noise import PerlinNoise
from src.math import Vector  # adjust import if needed


@dataclass
class MarbleMaterial(PhongMaterial):
    """
    Procedural marble material that simulates the appearance of marble veins using a combination of sine waves and noise.
        - vein_scale: Controls the frequency of the veins (higher values create more veins)
        - warp_strength: Controls how much the veins are warped by noise (higher values create more irregular veins)
        - vein_sharpness: Controls how sharp the veins are (higher values create sharper veins
        - warp_noise: The noise function used to warp the veins (default is Perlin noise)
        - noise: Optional noise function that can be used to add additional detail to the material (
            for example, to create a more rough or bumpy surface)
        - light_color_factor: Multiplier for the base color in the lighter areas of the veins
        - dark_color_factor: Multiplier for the base color in the darker areas of the veins
    """
    vein_scale: float = 6.0
    warp_strength: float = 2.0
    vein_sharpness: float = 4.0
    warp_noise: Noise = field(default_factory=PerlinNoise)
    noise: Noise | None = None
    light_color_factor: float = 1.0
    dark_color_factor: float = 0.75

    def sample(self, hit) -> PhongMaterialSample:
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
        base_color = dark * (1.0 - veins) + light * veins
        ambient_color = self.base_color * 0.5

        shin = max(10.0, self.shininess * (0.7 + 0.3 * veins))

        return PhongMaterialSample(
            base_color=base_color,
            spec_color=self.spec_color,
            shininess=float(shin),
            ior=self.ior,
            transparency=self.transparency,
            normal_noise=self.noise,
            ambient_color=ambient_color,
        )