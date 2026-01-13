from dataclasses import dataclass
from src.geometry.object_geometry import ObjectGeometry
from src.material.material.material import Material
from src.geometry.ray import Ray
from src.scene.surface_interaction import SurfaceInteraction


@dataclass
class Primitive:
    geometry: ObjectGeometry
    material: Material

    _id: int = -1  # internal ID for tracking purposes

    def intersect(self, ray: Ray, t_min=0.001, t_max=float("inf")):
        geom_hit = self.geometry.intersect(ray, t_min, t_max)
        if geom_hit is None:
            return None
        return SurfaceInteraction(geom=geom_hit, material=self.material)
