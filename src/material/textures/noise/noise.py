from abc import ABC, abstractmethod
from dataclasses import field, dataclass
from src.math.vector import Vector
from src.math.vertex import Vertex

@dataclass
class Noise(ABC):
    """
    Abstract base class for procedural noise textures.
    scale: A scaling factor applied to the input coordinates before sampling the noise function.
    offset: A vector added to the input coordinates before sampling the noise function, allowing for shifting the noise pattern in space.
    strength: A multiplier applied to the final noise value, controlling the intensity of the noise effect.
    eps: A small epsilon value used to prevent issues with floating-point precision when sampling the noise function, especially for functions that may have discontinuities
    """
    scale: float = 1.0
    offset: Vector = field(default_factory=lambda: Vector(0.0, 0.0, 0.0))
    strength: float = 0.0
    eps: float = 1e-3

    @abstractmethod
    def value(self, position: Vertex | Vector) -> float:
        """
        Get the noise value at a given vector position.
        :param position: Vector position to sample the noise
        :return: Noise value as a float
        """
        raise NotImplementedError

    def noise_fn(self, x: float, y: float) -> float:
        """
        Get the noise value at a given (x, y) coordinate by calling the value method with a Vector for Z = 0.0.
        :param x: X coordinate to sample the noise
        :param y: Y coordinate to sample the noise
        :return: Noise value as a float
        """
        return self.value(Vector(x, y, 0.0))
