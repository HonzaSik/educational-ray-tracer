from dataclasses import dataclass, field
from src.material.color import Color
from src.material.material.material import Material
from src.math.vector import Vector


@dataclass
class PhongMaterial(Material):
    """
    Phong material model with properties for specular highlights, reflectivity, and transparency.
    1. base_color: The base color of the material.
    2. spec_color: The specular color of the material.
    3. shininess: Controls the size of the specular highlight.
    4. reflectivity: The reflectivity of the material (0.0 to 1.0).
    5. transparency: The transparency of the material (0.0 to 1.0).
    6. ior: Index of refraction for transparent materials
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

    def get_reflectance_vector(self) -> Vector:
        raise NotImplementedError("PhongMaterial does not implement get_reflectance_vector method.")

    def get_transparency(self) -> float:
        return self.transparency

    def get_ior(self) -> float:
        return self.ior

    def get_specular_color(self) -> Color:
        return self.spec_color

    def get_color(self) -> Color:
        return self.base_color
