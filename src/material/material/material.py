from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from src.material.color import Color
from src.material.material.sample import Sample
from src.material.textures.noise.normal_base import Noise
from src.math.vector import Vector


@dataclass
class Material(ABC):
    """
    Abstract base class for materials. Defines common properties for different material types.
    """
    name: str = "default_material"
    normal_noise: Optional[Noise] = None

    @abstractmethod
    def get_color(self) -> Color:
        """
        Get the base color of the material as a Color object.
        :return: Base color
        """
        NotImplementedError("get_color not implemented for this material")
        return Color(1.0, 1.0, 1.0)

    def get_reflectance(self) -> float:
        """
        Get the reflectance of the material.
        :return: Reflectance value
        """
        NotImplementedError("Reflectance not implemented for this material")
        return 0.0

    def get_reflectance_vector(self) -> Vector:
        """
        Get the reflectance color vector of the material.
        :return: Reflectance color
        """
        NotImplementedError("Transparency not implemented for this material")
        return Vector(0.0, 0.0, 0.0)

    def get_transparency(self) -> float:
        """
        Get the transparency of the material.
        :return: Transparency value
        """
        NotImplementedError("Transparency not implemented for this material")
        return 0.0

    def get_ior(self) -> float:
        """
        Get the index of refraction of the material.
        :return: Index of refraction
        """
        pass

    # todo remove this - temporary
    def get_specular_color(self) -> Color:
        """
        Get the specular color of the material.
        :return: Specular color
        """
        pass

    def sample(self, hit) -> Sample:
        """
        Optional method to sample material properties at a hit point. Can be overridden by procedural materials.
        :param hit: Hit information
        :return: MaterialSample with properties at the hit point
        """
        pass