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
from src.material.material import Material

# io modules
from src.io.image_helper import convert_ppm_to_png, write_ppm
from src.io.pickle_manager import PickleManager

# light modules
from src.light.light import PointLight, AmbientLight, Light

from src.io.object_libraries import LightLibrary, MaterialLibrary, ColorLibrary



__all__ = [
    "Resolution",
    "Vec3", "Vector", "Vertex",
    "Color", "Material",
    "convert_ppm_to_png", "write_ppm", "PickleManager",
    "PointLight", "AmbientLight", "Light",
    "LightLibrary", "MaterialLibrary", "ColorLibrary"
]
