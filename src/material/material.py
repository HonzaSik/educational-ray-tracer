from __future__ import annotations
from dataclasses import dataclass, field, replace
from src.material.color import Color
from enum import Enum

class MaterialType(Enum):
    PHONG = 1
    PBR = 2
    CUSTOM = 3

def create_phong_material(name: str, base_color: Color, spec_color: Color = Color.custom_rgb(255,255,255), shininess: float = 32.0, reflectivity: float = 0.0, transparency: float = 0.0, ior: float = 1.5) -> Material:
    return Material(
        name=name,
        material_type=MaterialType.PHONG,
        base_color=base_color,
        spec_color=spec_color,
        shininess=shininess,
        reflectivity=reflectivity,
        transparency=transparency,
        ior=ior
    )

@dataclass
class Material:
    """
    Material properties for surface shading.
    mirror - 0 <= mirror <= 1
    albedo - base color of the material
    """

    # name - no effect on rendering, just for identification
    name: str = "Default"
    material_type: MaterialType = MaterialType.PHONG

    # shared material properties for all renderers
    base_color: Color = field(default_factory=lambda: Color.custom_rgb(255,255,255)) # base color of the material
    emission: Color = field(default_factory=lambda: Color(0.0, 0.0, 0.0)) # self-illumination color of the material (black=none)

    # classic Phong model properties
    spec_color: Color = field(default_factory=lambda: Color.custom_rgb(255,255,255)) # specular color of the material (white=full specular, black=no specular)
    shininess: float = 32.0 # specular exponent for shininess (1=dull, 128=very shiny)

    # pbr model properties
    ior: float = 1.5   # index of refraction for transparent materials (1.0=air, 1.3=water, 1.5=glass, 2.4=diamond)
    metallic: float = 0.0 # 0=dielectric, 1=metal
    roughness: float = 0.0 # 0=smooth, 1=rough

    # additional properties for advanced rendering effects
    reflectivity: float = 0.0 # 0=matte, 1=perfect mirror
    transparency: float = 0.0 # 0=opaque, 1=fully transparent


    @classmethod
    def make(cls, *, name: str, base_color: Color, spec_color: Color = Color.custom_rgb(255,255,255), **kw) -> Material:
        """
        Create a Material instance with the given base color, specular color, and additional properties.

        :param name: The name of the material.
        :param base_color: The base color of the material.
        :param spec_color: The specular color of the material (default is Color.White).
        :param kw: Additional keyword arguments for other material properties.
        :return: A Material instance.
        """
        return cls(name=name, base_color=base_color, spec_color=spec_color, **kw)

    def get_material_name(self) -> str:
        return self.name

    def with_color(self, base_color: Color) -> Material:
        return replace(self, base_color=base_color)

    def with_specular(self, spec_color: Color, shininess: float | None = None) -> Material:
        return replace(self, spec_color=spec_color, shininess=shininess or self.shininess)

    def with_reflectivity(self, reflectivity: float) -> Material:
        return replace(self, reflectivity=reflectivity)

    def with_transparency(self, transparency: float, ior: float | None = None) -> Material:
        return replace(self, transparency=transparency, ior=ior or self.ior)

    def with_metallic(self, metallic: float) -> Material:
        return replace(self, metallic=metallic)

    def make_emissive(self, emission: Color) -> Material:
        return replace(self, emission=emission)

    def make_reflective(self, reflectivity: float) -> Material:
        return replace(self, reflectivity=reflectivity)

    #----------- Preset Materials ----------

    @classmethod
    def make_plastic(cls, *, name: str, base_color: Color, reflectivity: float = 0.5, shininess: float = 32.0) -> Material:
        return cls(name=name, base_color=base_color, reflectivity=reflectivity, shininess=shininess, metallic=0.0, roughness=0.5)

    @classmethod
    def make_metal(cls, *, name: str, base_color: Color, reflectivity: float = 1.0, shininess: float = 64.0) -> Material:
        return cls(name=name, base_color=base_color, reflectivity=reflectivity, shininess=shininess, metallic=1.0, roughness=0.3)

    @classmethod
    def make_glass(cls, *, name: str, base_color: Color, transparency: float = 0.9, ior: float = 1.5, roughness: float = 0.00) -> Material:
        return cls(name=name, base_color=base_color, transparency=transparency, ior=ior, roughness=roughness, reflectivity=0.1)