"""
Ray tracing library package.
This package provides essential classes and functions for 3D vector operations and image handling.
"""

# core modules
from src.core.resolution import Resolution

# math modules
from src.core.math.vec3 import Vec3
from src.core.math.vector import Vector
from src.core.math.vertex import Vertex

# material modules
from src.material.color import Color

# io modules with pickle
from src.io.image_helper import convert_ppm_to_png, write_ppm

# light modules
from src.light.light import Light



__all__ = [
    "Resolution",
    "Vec3", "Vector", "Vertex",
    "Color",
    "convert_ppm_to_png", "write_ppm",
    "Light",
]
