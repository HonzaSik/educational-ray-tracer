from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from src.material.color import Color
from src.material.material.material_sample import MaterialSample
from src.material.textures.noise.noise import Noise


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

    def get_specular_color(self) -> Color:
        """
        Get the specular color of the material.
        :return: Specular color
        """
        pass

    def get_ambient_color(self) -> Color:
        """
        Get the ambient color of the material.
        :return: Ambient color
        """
        pass

    def get_shininess(self) -> float:
        """
        Get the shininess of the material for specular highlights.
        :return: Shininess value
        """
        pass

    @abstractmethod
    def sample(self, hit) -> MaterialSample:
        """
        Optional method to sample material properties at a hit point. Can be overridden by procedural materials.
        :param hit: Hit information
        :return: MaterialSample with properties at the hit point
        """
        pass