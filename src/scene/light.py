from dataclasses import dataclass

from src.material.color import Color
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
    color: Color = field(default_factory=lambda: Color(1.0, 1.0, 1.0))
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

    @abstractmethod
    def get_color_at(self, point: Vertex) -> Color:
        """
        Get the color of the light at a given point in the scene.

        Args:
            point (Vertex): The point in the scene to get the light color for.

        Returns:
            Color: The color of the light at the given point.
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
class PointLight:
    """
    Simple light with no falloff
    """
    position: Vertex
    color: Color
    intensity: float = 1.0
    type: LightType = LightType.POINT

    def intensity_at(self, point: Vertex) -> float:
        return self.intensity

    def get_color_at(self, point: Vertex) -> Color:
        return self.color

@dataclass
class PointLightFalloff:
    """
    Simple light with no falloff
    """
    position: Vertex
    color: Color = field(default_factory=lambda: Color(1.0, 1.0, 1.0))
    intensity: float = 1.0
    type: LightType = LightType.POINT

    def intensity_at(self, point: Vertex) -> float:
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        dz = point.z - self.position.z
        r2 = dx * dx + dy * dy + dz * dz
        return self.intensity / max(r2, 1e-6)

    def get_color_at(self, point: Vertex) -> Color:
        return self.color

@dataclass
class AmbientLight(Light):
    """
    Represents an ambient light source in a 3D scene.
    """
    type: LightType = LightType.AMBIENT
    color: Color = field(default_factory=lambda: Color(1.0, 1.0, 1.0))

    def intensity_at(self, point: Vertex) -> float:
        # Ambient light has constant intensity everywhere
        return self.intensity

    def get_color_at(self, point: Vertex) -> Color:
        return self.color

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

    def get_color_at(self, point: Vertex) -> Color:
        return self.color

@dataclass
class SpotLight(Light):
    position: Vertex = field(default_factory=lambda: Vertex(0.0, 0.0, 0.0))
    direction: Vector = field(default_factory=lambda: Vector(0.0, -1.0, 0.0))
    angle: float = pi / 6

    def __post_init__(self):
        self.direction = self.direction.normalize()

    def intensity_at(self, point: Vertex) -> float:
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        dz = point.z - self.position.z

        length = (dx * dx + dy * dy + dz * dz) ** 0.5

        if length < 1e-8:
            return 0.0

        to_point = Vector(dx / length, dy / length, dz / length)
        spot_effect = self.direction.dot(to_point)

        if spot_effect <= cos(self.angle):
            return 0.0

        return self.intensity * spot_effect

    def get_color_at(self, point: Vertex) -> Color:
        return self.color