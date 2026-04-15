from __future__ import annotations
from abc import ABC, abstractmethod

from src.material.textures.noise.noise import Noise
from src.shading.helpers import tangent_basis
from src.scene.scene import Scene
from src.material.color import Color
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.light import Light
from src.math import Vector


def apply_noise_normal_perturbation(
    hit: SurfaceInteraction,
    noise: Noise | None,
    vec: Vector
) -> Vector:
    # Apply normal perturbation based on noise. If noise_override is provided, it takes precedence over any noise in the material.
    noise = noise
    if noise is None:
        return vec

    # If noise is present, apply normal perturbation. The strength of the perturbation is determined by the noise's strength property.
    strength = getattr(noise, "strength", 0.0)
    if strength == 0.0:
        return vec

    scale = getattr(noise, "scale", 1.0)
    eps = getattr(noise, "eps", 1e-3)
    inv_eps = 1.0 / eps

    # Compute the tangent and bitangent vectors for the normal. This is necessary to compute the noise gradient in the tangent space of the surface.
    n = vec.normalize()
    tangent, bitangent = tangent_basis(n)

    # normal of the hit point, used as the base for perturbation
    p = hit.normal.normalize()

    # Find the noise values at the hit point and at small offsets in the tangent and bitangent directions. These values will be used to compute the noise gradient.
    h0 = noise.value(p * scale)
    ht = noise.value((p + tangent * eps) * scale)
    hb = noise.value((p + bitangent * eps) * scale)

    # Slope
    dht = (ht - h0) * inv_eps
    dhb = (hb - h0) * inv_eps

    # Modify normal and normalize the result.
    return (n - tangent * (strength * dht) - bitangent * (strength * dhb)).normalize()


class LocalShading(ABC):
    @abstractmethod
    def shade(self, hit: SurfaceInteraction, light: Light, view_dir: Vector, scene: Scene | None = None) -> Color:
        ...

    @abstractmethod
    def shade_multiple_lights(self, hit: SurfaceInteraction, lights: list[Light], view_dir: Vector, scene: Scene | None = None) -> Color:
        ...