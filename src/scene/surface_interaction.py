from __future__ import annotations
from dataclasses import dataclass
from src.geometry.geometry_hit import GeometryHit
from src.material import Material
from src.scene.object import Object


@dataclass
class SurfaceInteraction:
    geom: GeometryHit
    material: Material
    object: Object

    def replace_material(self, new_material: Material) -> SurfaceInteraction:
        return SurfaceInteraction(geom=self.geom, material=new_material)

    def hit_surface(self) -> GeometryHit:
        return self.geom

    @property
    def point(self): return self.geom.point

    @property
    def normal(self): return self.geom.normal

    @property
    def dist(self): return self.geom.dist

    @property
    def front_face(self): return self.geom.front_face

    @property
    def distance(self): return self.geom.dist