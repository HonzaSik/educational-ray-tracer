from dataclasses import dataclass, field
from src.material.color import Color
from src.light.light import Light
from src.material.material import Material

@dataclass
class ColorLibrary:
    """Simple library wrapper so you can access colors as attributes."""
    colors: dict[str, Color] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Color:
        try:
            return self.colors[name]
        except KeyError:
            raise AttributeError(f"No color named '{name}'")

    def add(self, name: str, color: Color):
        self.colors[name] = color

    def get_all_names(self) -> list[str]:
        return list(self.colors.keys())

@dataclass
class LightLibrary:
    """Container for various object libraries."""
    lights: dict[str, Light] = field(default_factory=dict)
    def __getattr__(self, name: str) -> Light:
        try:
            return self.lights[name]
        except KeyError:
            raise AttributeError(f"No light named '{name}'")

    def add(self, name: str, light: Light):
        self.lights[name] = light

    def get_all_names(self) -> list[str]:
        return list(self.lights.keys())


@dataclass
class MaterialLibrary:
    """Container for various object libraries."""
    materials: dict[str, Material] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Material:
        try:
            return self.materials[name]
        except KeyError:
            raise AttributeError(f"No material named '{name}'")

    def add(self, name: str, material: Material):
        self.materials[name] = material

    def get_all_names(self) -> list[str]:
        return list(self.materials.keys())
