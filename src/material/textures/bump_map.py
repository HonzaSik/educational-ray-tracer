from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from src.math import Vector

# height function h(u, v) -> float
HeightFn = Callable[[float, float], float]


@dataclass
class BumpMap:
    height: HeightFn
    strength: float = 0.5
    scale_u: float = 1.0
    scale_v: float = 1.0
    eps: float = 1e-3

    def perturb_normal(self, hit, base_normal: Vector) -> Vector:
        geom = getattr(hit, "geom", hit)
        uv = getattr(geom, "uv", None)
        dpdu = getattr(geom, "dpdu", None)
        dpdv = getattr(geom, "dpdv", None)

        if uv is None or dpdu is None or dpdv is None:
            return base_normal

        u, v = uv
        N = base_normal.normalize()

        u *= self.scale_u
        v *= self.scale_v

        h   = self.height(u, v)
        h_u = self.height(u + self.eps, v)
        h_v = self.height(u, v + self.eps)

        dHdu = (h_u - h) / self.eps
        dHdv = (h_v - h) / self.eps

        bump_vec = dpdu * dHdu + dpdv * dHdv
        N_pert = (N - self.strength * bump_vec).normalize()
        return N_pert
