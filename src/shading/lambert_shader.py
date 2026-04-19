from __future__ import annotations

from src.material.color import Color, clamp_color255
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.light import Light
from src.scene.scene import Scene
from src.math import Vector
from .local_shading import LocalShading


class LambertShader(LocalShading):
    def shade(
        self,
        hit: SurfaceInteraction,
        light: Light,
        view_dir: Vector,
        scene: Scene | None = None
    ) -> Color:
        material = hit.material

        n = hit.normal.normalize()
        l = (light.position - hit.point).normalize()
        intensity = light.intensity_at(hit.point)

        ndotl = max(0.0, n.dot(l))
        return material.get_color() * ndotl * intensity

    def shade_multiple_lights(
        self,
        hit: SurfaceInteraction,
        lights: list[Light],
        view_dir: Vector,
        scene: Scene | None = None
    ) -> Color:
        material = hit.material
        color = material.get_color()

        for light in lights:
            color += self.shade(hit, light, view_dir, scene)

        return clamp_color255(color)