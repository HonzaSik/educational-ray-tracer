from dataclasses import dataclass
from src.core.math.vertex import Vertex

@dataclass
class Light:
    """
    Point light source in 3D space defined by position and intensity.
    """
    pos: Vertex
    intensity: float = 1.0