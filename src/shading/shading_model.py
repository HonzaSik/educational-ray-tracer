from __future__ import annotations
from abc import ABC, abstractmethod

from src.material.textures.noise.normal_base import Noise
from src.shading.helpers import tangent_basis
from src.scene.scene import Scene
from src.material.material.material import Material
from src.material.color import Color
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.light import Light
from src.math import Vector


def apply_noise_normal_perturbation(
    hit: SurfaceInteraction,
    noise_override: Noise | None,
    vec: Vector
) -> Vector:
    noise = noise_override
    if noise is None:
        return vec

    strength = getattr(noise, "strength", 0.0)
    if strength == 0.0:
        return vec

    scale = getattr(noise, "scale", 1.0)
    eps = getattr(noise, "eps", 1e-3)
    inv_eps = 1.0 / eps

    n = vec.normalize()
    tangent, bitangent = tangent_basis(n)

    # sphere-friendly mapping (works great for planets)
    p = hit.normal.normalize()

    h0 = noise.value(p * scale)
    ht = noise.value((p + tangent * eps) * scale)
    hb = noise.value((p + bitangent * eps) * scale)

    dht = (ht - h0) * inv_eps
    dhb = (hb - h0) * inv_eps

    return (n - tangent * (strength * dht) - bitangent * (strength * dhb)).normalize()


class ShadingModel(ABC):
    @abstractmethod
    def shade(self, hit: SurfaceInteraction, light: Light, view_dir: Vector, scene: Scene | None = None) -> Color:
        ...

    @abstractmethod
    def shade_multiple_lights(self, hit: SurfaceInteraction, lights: list[Light], view_dir: Vector, scene: Scene | None = None) -> Color:
        ...

    def apply_noise_texture(self, hit : SurfaceInteraction, material : Material, n : Vector) -> Vector:
        raise NotImplementedError("Normal mapping from texture not implemented yet.")
