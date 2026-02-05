from dataclasses import dataclass
from src.math import Vertex
from enum import Enum
from src.math import Vector
from abc import ABC, abstractmethod
from math import pi, cos
from dataclasses import field


# enum types of lights
class LightType(Enum):
    POINT = "point"
    AMBIENT = "ambient"
    DIRECTIONAL = "directional"
    SPOT = "spot"
    AREA = "area"


@dataclass
class Light(ABC):
    """
    Abstract base class for different types of lights in a 3D scene.
    """
    intensity: float
    position: Vertex = field(default_factory=lambda: Vertex(0.0, 0.0, 0.0))
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
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        dz = point.z - self.position.z
        r2 = dx*dx + dy*dy + dz*dz
        if r2 < 1e-8:
            return 0.0
        inv_square = self.intensity / (4.0 * pi * r2)
        if self.falloff > 0.0:
            return inv_square / (1.0 + self.falloff * r2)
        return inv_square


@dataclass
class AmbientLight(Light):
    """
    Represents an ambient light source in a 3D scene.
    """
    type: LightType = LightType.AMBIENT

    def intensity_at(self, point: Vertex) -> float:
        # Ambient light has constant intensity everywhere
        return self.intensity

@dataclass
class DirectionalLight(Light):
    """
    Represents a directional light source in a 3D scene.
    """
    direction: Vector = field(default_factory=lambda: Vector(0.0, -1.0, 0.0))
    type: LightType = LightType.DIRECTIONAL

    def intensity_at(self, point: Vertex) -> float:
        # Directional light has constant intensity everywhere
        return self.intensity

@dataclass
class SpotLight(Light):
    """
    Represents a spotlight source in a 3D scene.
    """
    direction: Vector = field(default_factory=lambda: Vector(0.0, -1.0, 0.0))
    angle: float = pi / 6  # spotlight cone angle in radians
    type: LightType = LightType.SPOT

    def intensity_at(self, point: Vertex) -> float:
        # Calculate direction to point
        to_point = (point - self.position).normalize()

        spot_effect = (self.direction.normalize()).dot(to_point)

        if spot_effect > cos(self.angle):
            return self.intensity * spot_effect
        return 0.0