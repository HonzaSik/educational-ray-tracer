from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from src.material.color import Color
from src.material.textures.noise.normal_base import Noise
from src.math.vector import Vector

@dataclass
class MaterialSample:
    base_color: Color
    spec_color: Color
    shininess: float
    ior: float = 1.5
    opacity: float = 1.0
    normal_noise: Optional[Noise] = None
    reflectivity: float = 0.0
    emission: Color = field(default_factory=lambda: Color(0.0, 0.0, 0.0))


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
        pass

    @abstractmethod
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
        raise NotImplementedError("Subclasses must implement get_reflectance_vector method.")

    def get_transparency(self) -> float:
        """
        Get the transparency of the material.
        :return: Transparency value
        """
        raise NotImplementedError("Subclasses must implement get_transparency method.")

    # todo remove this - temporary
    def get_ior(self) -> float:
        """
        Get the index of refraction of the material.
        :return: Index of refraction
        """
        raise NotImplementedError("Subclasses must implement get_ior method.")

    # todo remove this - temporary
    def get_specular_color(self) -> Color:
        """
        Get the specular color of the material.
        :return: Specular color
        """
        raise NotImplementedError("Subclasses must implement get_specular_color method.")

    def sample(self, hit) -> MaterialSample:
        """
        Default behavior: constant Phong-like properties from getters.
        Procedural materials override this.
        """
        shininess = float(getattr(self, "shininess", 32.0))
        return MaterialSample(
            base_color=self.get_color(),
            spec_color=self.get_specular_color(),
            shininess=shininess,
            opacity=1.0 - float(getattr(self, "transparency", 0.0)),
            ior=float(getattr(self, "ior", 1.0)),
        )