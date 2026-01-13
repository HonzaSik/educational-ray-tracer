from __future__ import annotations
from abc import ABC, abstractmethod
from src.shading.helpers import tangent_basis
from src.scene.scene import Scene
from src.material.material.material import Material
from src.material.color import Color
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.light import Light
from src.math import Vector


def apply_noise_normal_perturbation(hit : SurfaceInteraction, material : Material, vec : Vector) -> Vector:
    noise = material.normal_noise if hasattr(material, "noise") else None
    strength = material.noise_strength if hasattr(material, "noise_strength") else 0.0

    if noise is None or strength == 0.0:
        return vec

    scale = material.noise_scale if hasattr(material, "noise_scale") else 1.0
    eps = material.noise_eps if hasattr(material, "noise_eps") else 1e-3
    inv_eps = 1.0 / eps

    point = hit.point
    tangent, bitangent = tangent_basis(vec)

    # point on the noise texture
    p = point * scale
    # central height
    h0 = noise.value(p)
    # heights at offset positions
    ht = noise.value((point + tangent * eps) * scale)
    hb = noise.value((point + bitangent * eps) * scale)

    # compute height differences on shifted positions
    dht = (ht - h0) * inv_eps
    dhb = (hb - h0) * inv_eps

    # perturbed normal adjusted by height differences and strength
    perturbed_normal = (vec - tangent * (strength * dht) - bitangent * (strength * dhb)).normalize_ip()
    return perturbed_normal


class ShadingModel(ABC):
    @abstractmethod
    def shade(self, hit: SurfaceInteraction, light: Light, view_dir: Vector, scene: Scene | None = None) -> Color:
        ...

    @abstractmethod
    def shade_multiple_lights(self, hit: SurfaceInteraction, lights: list[Light], view_dir: Vector, scene: Scene | None = None) -> Color:
        ...

    def apply_noise_texture(self, hit : SurfaceInteraction, material : Material, n : Vector) -> Vector:
        raise NotImplementedError("Normal mapping from texture not implemented yet.")
