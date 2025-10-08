from dataclasses import dataclass
from enum import Enum
from src.math import Vector
from src.math import Vertex
from abc import ABC, abstractmethod
from math import pi

#enum types of lights
class LightType(Enum):
    POINT = "point"
    AMBIENT = "ambient"

@dataclass
class Light(ABC):
    """
    Abstract base class for different types of lights in a 3D scene.
    """
    position: Vertex
    intensity: float
    falloff: float = 1.0
    type: LightType = None

    @abstractmethod
    def intensity_at(self, point: Vertex) -> float:
        """
        Calculate the illumination at a given point from this light source.

        Args:
            point (Vertex): The point in the scene to be illuminated.

        Returns:
            float: The intensity of light at the given point.
        """
        pass

    def translate(self, translation: Vector) -> None:
        """
        Translate the light's position by a given vector.

        Args:
            translation (Vertex): The vector by which to translate the light.
        """
        self.position += translation


@dataclass
class PointLight(Light):
    """
    Represents a point light source in a 3D scene.
    """
    type: LightType = LightType.POINT

    def intensity_at(self, point: Vertex) -> float:
        dx = self.position.x - point.x
        dy = self.position.y - point.y
        dz = self.position.z - point.z
        r2 = dx*dx + dy*dy + dz*dz
        if r2 <= 1e-8:
            return 0.0
        # inverse-square with optional extra falloff factor
        inv_square = self.intensity / (4.0 * pi * r2)
        return inv_square / (1.0 + self.falloff * r2)


@dataclass
class AmbientLight(Light):
    """
    Represents an ambient light source in a 3D scene.
    """
    type: LightType = LightType.AMBIENT

    def intensity_at(self, point: Vertex) -> float:
        # Ambient light has constant intensity everywhere
        return self.intensity