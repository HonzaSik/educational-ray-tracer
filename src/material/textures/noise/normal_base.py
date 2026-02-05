from abc import ABC, abstractmethod
from dataclasses import field, dataclass

from src.math.vector import Vector
from src.math.vertex import Vertex

@dataclass
class Noise(ABC):
    """
    Abstract base class for procedural noise textures.
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