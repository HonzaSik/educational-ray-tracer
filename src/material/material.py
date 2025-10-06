from __future__ import annotations
from dataclasses import dataclass, field, replace
from src.material.color import Color

@dataclass
class Material:
    """
    Material properties for surface shading.
    mirror - 0 <= mirror <= 1
    albedo - base color of the material
    """
    name: str = "Default"
    base_color: Color = field(default_factory=lambda: Color.custom_rgb(255,255,255))
    reflectivity: float = 0.0 # 0=matte, 1=perfect mirror
    spec_color: Color = field(default_factory=lambda: Color.custom_rgb(255,255,255))
    shininess: float = 32.0 # specular exponent for shininess
    emission: Color = field(default_factory=lambda: Color(0.0, 0.0, 0.0))
    transparency: float = 0.0 # 0=opaque, 1=fully transparent
    ior: float = 1.5   # index of refraction
    metallic: float = 0.0 # 0=dielectric, 1=metal


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