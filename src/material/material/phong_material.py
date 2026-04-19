from dataclasses import dataclass, field
from typing import Optional
from src.material.color import Color
from src.material.material.material import Material
from src.material.material.material_sample import MaterialSample
from src.material.textures.noise.noise import Noise


@dataclass
class PhongMaterialSample(MaterialSample):
    """
    A sample of Phong material properties at a specific point on the surface.
    Used for shading calculations; can be modified by procedural materials.
     - base_color: The base color of the material at the sample point.
     - spec_color: The specular color of the material at the sample point.
     - ambient_color: The ambient color of the material at the sample point.
     - shininess: The shininess coefficient for specular highlights.
     - reflectivity: Reflectivity of the material (0.0 to 1.0).
     - ior: Index of refraction for transparent materials (default 1.5).
     - transparency: Transparency of the material (0.0 to 1.0, default 0.0).
     - normal_noise: Optional procedural noise for normal perturbation.
    """
    base_color: Color
    spec_color: Color
    ambient_color: Color
    shininess: float
    reflectivity: float
    ior: float = 1.5
    transparency: float = 0.0
    normal_noise: Optional[Noise] = None

    def get_color(self) -> Color:
        return self.base_color

    def get_specular_color(self) -> Color:
        return self.spec_color

    def get_ambient_color(self) -> Color:
        return self.ambient_color

    def get_shininess(self) -> float:
        return self.shininess

    def get_reflectance(self) -> float:
        return self.reflectivity

    def get_transparency(self) -> float:
        return self.transparency

    def get_ior(self) -> float:
        return self.ior

    def get_normal_noise(self) -> Optional[Noise]:
        return self.normal_noise


@dataclass
class PhongMaterial(Material):
    """
    Phong material model with properties for specular highlights and basic reflectivity.
     - base_color: The base color of the material.
     - spec_color: The specular color of the material.
     - ambient_color: The ambient color of the material.
     - shininess: The shininess coefficient for specular highlights. (0.0 to 256.0)
     - reflectivity: The reflectivity of the material (0.0 to 1.0).
     - transparency: The transparency of the material (0.0 to 1.0).
     - ior: Index of refraction for transparent materials (default 1.5).
     - name: Name of the material (default "phong_material").
     - normal_noise: Optional procedural noise for normal perturbation.
    """
    name: str = "phong_material"
    # base properties
    base_color: Color = field(default_factory=lambda: Color.custom_rgb(200, 200, 200))
    spec_color: Color = field(default_factory=lambda: Color.custom_rgb(255, 255, 255))
    ambient_color: Color = field(default_factory=lambda: Color.custom_rgb(30, 30, 30))
    shininess: float = 32.0

    # extended properties for reflectivity and transparency
    reflectivity: float = 0.0
    transparency: float = 0.0
    ior: float = 1.5

    #noise for normal perturbation
    normal_noise: Optional[Noise] = None

    _CLAMP = {
        "reflectivity": (0.0, 1.0),
        "transparency": (0.0, 1.0),
    }

    def __post_init__(self):
        for attr, (min_val, max_val) in self._CLAMP.items():
            value = getattr(self, attr)
            if not (min_val <= value <= max_val):
                raise ValueError(
                    f"{attr} must be between {min_val} and {max_val}, got {value}"
                )

    def get_color(self) -> Color:
        return self.base_color

    def get_specular_color(self) -> Color:
        return self.spec_color

    def get_ambient_color(self) -> Color:
        return self.ambient_color

    def get_reflectance(self) -> float:
        return self.reflectivity

    def get_transparency(self) -> float:
        return self.transparency

    def get_ior(self) -> float:
        return self.ior

    def sample(self, hit) -> PhongMaterialSample:
        """
        Returns constant Phong properties at the hit point.
        Procedural subclasses override this to vary properties across the surface.
        normal_noise is passed through so procedural subclasses can set it.
        """
        return PhongMaterialSample(
            base_color=self.get_color(),
            spec_color=self.get_specular_color(),
            ambient_color=self.get_ambient_color(),
            shininess=self.shininess,
            reflectivity=self.get_reflectance(),
            ior=self.get_ior(),
            transparency=self.get_transparency(),
            normal_noise=self.normal_noise,
        )