from dataclasses import dataclass, field
from src.material.color import Color
from src.material.material.material import Material


@dataclass
class PbrMaterial(Material):
    """
    Physically Based Rendering (PBR) material model with properties for realistic surface representation.
    1. base_color: The base color of the material.
    2. metallic: Controls how metallic the surface appears (0.0 to 1.0).
    3. roughness: Controls the surface roughness (0.0 to 1.0).
    4. reflectivity: The reflectivity of the material (0.0 to 1.0).
    5. transparency: The transparency of the material (0.0 to 1.0).
    6. ior: Index of refraction for transparent materials
    """
    base_color: Color = field(default_factory=lambda: Color.custom_rgb(200, 200, 200))
    metallic: float = 0.0
    roughness: float = 0.5
    reflectivity: float = 0.0
    transparency: float = 0.0
    ior: float = 1.5

    def __post_init__(self):
        for attr in ['metallic', 'roughness', 'reflectivity', 'transparency']:
            value = getattr(self, attr)
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{attr} must be between 0.0 and 1.0, got {value}")

    def get_reflectance(self) -> float:
        return self.reflectivity