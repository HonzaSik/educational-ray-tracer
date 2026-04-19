from dataclasses import dataclass, field
from src.material.material.phong_material import PhongMaterial, PhongMaterialSample
from src.material.textures.noise.noise import Noise
from src.material.textures.noise.perlin_noise import PerlinNoise
from src.math.helpers import smooth_interpolation
from src.scene.surface_interaction import SurfaceInteraction

@dataclass
class RockMaterial(PhongMaterial):
    color_noise: Noise = field(default_factory=PerlinNoise)
    color_scale: float = 3.0
    bump_noise: Noise | None = None

    def phong_sample(self, hit: SurfaceInteraction) -> PhongMaterialSample:
        p = hit.point  # world mapping for rocks; for planets use hit.normal.normalize()

        t = 0.5 * self.color_noise.value(p * self.color_scale) + 0.5  # -> [0,1]
        t = smooth_interpolation(0.35, 0.75, t)  # nicer mask

        # tint between darker and your base_color
        dark = self.base_color * 0.55
        albedo = dark * (1.0 - t) + self.base_color * t

        # shininess varies too (rough patches)
        shin = self.shininess * (0.6 + 0.8 * (1.0 - t))

        # choose bump noise: if not provided, reuse color_noise but stronger scale/strength via its own settings
        nnoise = self.bump_noise if self.bump_noise is not None else self.normal_noise

        return PhongMaterialSample(
            base_color=albedo,
            spec_color=self.spec_color,
            shininess=float(shin),
            ior=self.ior,
            transparency=self.transparency,
            normal_noise=nnoise,
        )
