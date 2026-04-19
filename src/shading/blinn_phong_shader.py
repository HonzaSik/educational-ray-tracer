from __future__ import annotations
from .local_shading import LocalShading
from src.scene.surface_interaction import SurfaceInteraction
from src.material.color import Color, clamp_color255
from src.scene.light import Light
from src.math import Vector
from src.scene.scene import Scene
from src.material.material.phong_material import PhongMaterial

class BlinnPhongShader(LocalShading):
    def shade(
        self,
        hit: SurfaceInteraction,
        light: Light,
        view_dir: Vector,
        scene: Scene | None = None
    ) -> Color:
        material: PhongMaterial = hit.material

        n = hit.normal.normalize()
        l = (light.position - hit.point).normalize()
        v = view_dir.normalize()

        light_intensity = light.intensity_at(hit.point)

        diffuse = self._lambert(material.base_color, n, l)
        specular = self._blinn_phong(material.spec_color, material.shininess, n, l, v)

        return (diffuse + specular) * light_intensity * light.get_color_at(hit.point)

    def shade_multiple_lights(
        self,
        hit: SurfaceInteraction,
        lights: list[Light],
        view_dir: Vector,
        scene: Scene | None = None
    ) -> Color:
        material: PhongMaterial = hit.material
        result = material.ambient_color

        for light in lights:
            result += self.shade(hit, light, view_dir, scene)

        return clamp_color255(result)

    @staticmethod
    def _lambert(base_color: Color, n: Vector, l: Vector) -> Color:
        return base_color * max(0.0, n.dot(l))

    @staticmethod
    def _blinn_phong(spec_color: Color, shininess: float, n: Vector, l: Vector, v: Vector) -> Color:
        h = (l + v).normalize()
        return spec_color * (max(0.0, n.dot(h)) ** max(1.0, shininess))