from dataclasses import dataclass, field
from typing import Optional
from src.material.color import Color
from src.material.material.material import Material
from src.material.material.sample import Sample
from src.material.textures.noise.noise import Noise
from src.math.vector import Vector


@dataclass
class PhongMaterialSample(Sample):
    """
    A sample of Phong material properties at a specific point on the surface.
     - base_color: The base color of the material at the sample point.
     - spec_color: The specular color of the material at the sample point.
     - shininess: The shininess coefficient for specular highlights.
     - ior: Index of refraction for transparent materials (default 1.5).
     - opacity: Opacity of the material (0.0 to 1.0, default 1.0).
     - normal_noise: Optional procedural noise for normal perturbation.
     - reflectivity: Reflectivity of the material (0.0 to 1.0, default 0.0).
     - emission: Emissive color of the material (default black).
    """
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
    """
    Phong material model with properties for specular highlights and basic reflectivity.
     - base_color: The base color of the material.
     - spec_color: The specular color of the material.
     - shininess: The shininess coefficient for specular highlights. (min 0.0, higher is shinier max 256.0)
     - reflectivity: The reflectivity of the material (0.0 to 1.0).
     - transparency: The transparency of the material (0.0 to 1.0).
     - ior: Index of refraction for transparent materials (default 1.5).
     - name: Name of the material (default "phong_material").
     - normal_noise: Optional procedural noise for normal perturbation.
    """
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

    def get_transparency(self) -> float:
        return self.transparency

    def get_ior(self) -> float:
        return self.ior

    def get_specular_color(self) -> Color:
        return self.spec_color

    def get_color(self) -> Color:
        return self.base_color

    def sample(self, hit) -> PhongMaterialSample:
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
