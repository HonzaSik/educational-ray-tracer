from dataclasses import dataclass, field
from typing import Optional
from src.material.color import Color
from src.material.material.material import Material
from src.material.material.sample import Sample
from src.material.textures.noise.normal_base import Noise
from src.math.vector import Vector


@dataclass
class PhongMaterialSample(Sample):
    base_color: Color
    spec_color: Color
    shininess: float
    ior: float = 1.5
    opacity: float = 1.0
    normal_noise: Optional[Noise] = None
    reflectivity: float = 0.0
    emission: Color = field(default_factory=lambda: Color(0.0, 0.0, 0.0))

@dataclass
class PhongMaterial(Material):
    name: str = "phong_material"
    base_color: Color = field(default_factory=lambda: Color.custom_rgb(200, 200, 200))
    spec_color: Color = field(default_factory=lambda: Color.custom_rgb(255, 255, 255))
    shininess: float = 32.0
    reflectivity: float = 0.0
    transparency: float = 0.0
    ior: float = 1.5

    def __post_init__(self):
        for attr in ['reflectivity', 'transparency']:
            value = getattr(self, attr)
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{attr} must be between 0.0 and 1.0, got {value}")

    def get_reflectance(self) -> float:
        return self.reflectivity

    def get_reflectance_vector(self) -> Vector:
        raise NotImplementedError

    def get_transparency(self) -> float:
        return self.transparency

    def get_ior(self) -> float:
        return self.ior

    def get_specular_color(self) -> Color:
        return self.spec_color

    def get_color(self) -> Color:
        return self.base_color

    def sample(self, hit) -> Sample:
        """
        Default behavior: constant Phong-like properties from getters.
        Procedural materials override this.
        """
        shininess = float(getattr(self, "shininess", 32.0))
        return PhongMaterialSample(
            base_color=self.get_color(),
            spec_color=self.get_specular_color(),
            shininess=shininess,
            opacity=1.0 - float(getattr(self, "transparency", 0.0)),
            ior=float(getattr(self, "ior", 1.0)),
        )
