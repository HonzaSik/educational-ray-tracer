from dataclasses import dataclass
from src.core.math.vertex import Vertex
from abc import ABC, abstractmethod


@dataclass
class Light(ABC):
    """
    Abstract base class for different types of lights in a 3D scene.
    """
    position: Vertex
    intensity: float
    falloff: float = 1.0

    @abstractmethod
    def light_intensity(self, point: Vertex) -> float:
        """
        Calculate the illumination at a given point from this light source.

        Args:
            point (Vertex): The point in the scene to be illuminated.

        Returns:
            float: The intensity of light at the given point.
        """
        pass


@dataclass
class PointLight(Light):
    """
    Represents a point light source in a 3D scene.
    """

    def light_intensity(self, point: Vertex) -> float:
        # Calculate distance from light to point
        distance = ((self.position.x - point.x) ** 2 +
                    (self.position.y - point.y) ** 2 +
                    (self.position.z - point.z) ** 2) ** 0.5
        # Apply falloff formula
        return self.intensity / (1 + self.falloff * distance ** 2)


@dataclass
class AmbientLight(Light):
    """
    Represents an ambient light source in a 3D scene.
    """

    def light_intensity(self, point: Vertex) -> float:
        # Ambient light has constant intensity everywhere
        return self.intensity