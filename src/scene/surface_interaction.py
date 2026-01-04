from __future__ import annotations
from dataclasses import dataclass
from src.geometry.geometry_hit import GeometryHit
from src.material import Material

@dataclass
class SurfaceInteraction:
    geom: GeometryHit
    material: Material

    def replace_material(self, new_material: Material) -> SurfaceInteraction:
        return SurfaceInteraction(geom=self.geom, material=new_material)

    def hit_surface(self) -> GeometryHit:
        return self.geom

    @property
    def point(self): return self.geom.point
    @property
    def normal(self): return self.geom.normal
    @property
    def uv(self): return self.geom.uv
    @property
    def dpdu(self): return self.geom.dpdu
    @property
    def dpdv(self): return self.geom.dpdv