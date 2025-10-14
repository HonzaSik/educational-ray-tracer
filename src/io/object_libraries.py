from dataclasses import dataclass, field
from src.material.color import Color
from src.scene.light import Light, LightType
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
        """
        Add a light to the library.
        :param name: Name of the light
        :param light: Light object
        :return: None
        """
        self.lights[name] = light

    def get_all_names(self) -> list[str]:
        """
        Get all light names from the library.
        :return: List of all light names
        """
        return list(self.lights.keys())

    def get_all_lights(self) -> list[Light]:
        """
        Get all lights from the library.
        :return: List of all Lights
        """
        return list(self.lights.values())

    def get_point_lights(self) -> list[Light]:
        """
        Get all point lights from the library.
        :return: List of Point Lights
        """
        return [light for light in self.lights.values() if isinstance(light.type, LightType) and light.type == LightType.POINT]

    def get_ambient_light(self) -> Light | None:
        """
        Get the ambient light from the library, if it exists. Assumes only one ambient light else returns the first one found.
        :return: Ambient Light or None if not found
        """
        for light in self.lights.values():
            if light.type == LightType.AMBIENT:
                return light
        return None


@dataclass
class MaterialLibrary:
    """Simple library wrapper so you can access materials as attributes."""
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