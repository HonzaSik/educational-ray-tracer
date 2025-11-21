from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field, replace
from src.material.color import Color
from enum import Enum
from src.math.vector import Vector

@dataclass()
class Material(ABC):
    """
    Abstract base class for materials. Defines common properties for different material types.
    """
    name: str = "default_material"

    def __init__(self):
        raise NotImplementedError("Material is an abstract base class and cannot be instantiated directly.")

    def get_reflectance(self) -> float:
        """
        Get the reflectance of the material.
        :return: Reflectance value
        """
        raise NotImplementedError("Subclasses must implement get_reflectance method.")

    def get_reflectance_vector(self) -> Vector:
        """
        Get the reflectance color vector of the material.
        :return: Reflectance color
        """
        raise NotImplementedError("Subclasses must implement get_refflectance_vector method.")

    def get_transparency(self) -> float:
        """
        Get the transparency of the material.
        :return: Transparency value
        """
        raise NotImplementedError("Subclasses must implement get_transparency method.")

    #todo remove this - temporary
    def get_ior(self) -> float:
        """
        Get the index of refraction of the material.
        :return: Index of refraction
        """
        raise NotImplementedError("Subclasses must implement get_ior method.")

    #todo remove this - temporary
    def get_specular_color(self) -> Color:
        """
        Get the specular color of the material.
        :return: Specular color
        """
        raise NotImplementedError("Subclasses must implement get_specular_color method.")

    #todo remove this - temporary
    def base_color_as_color(self) -> Color:
        """
        Get the base color of the material as a Color object.
        :return: Base color
        """
        raise NotImplementedError("Subclasses must implement base_color_as_Color method.")

