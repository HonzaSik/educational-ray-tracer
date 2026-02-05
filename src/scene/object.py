from dataclasses import dataclass
from src.geometry.primitive import Primitive
from src.material.material.material import Material
from src.geometry.ray import Ray
from src.scene.surface_interaction import SurfaceInteraction


@dataclass
class Object:
    """
    Scene object composed of geometry and material.
    """
    geometry: Primitive
    material: Material
    _id: int | None = None  # Optional unique identifier

    def intersect(self, ray: Ray, t_min=0.001, t_max=float("inf")):
        geom_hit = self.geometry.intersect(ray, t_min, t_max)
        if geom_hit is None:
            return None
        return SurfaceInteraction(geom=geom_hit, material=self.material, object=self)

    def normal_at(self, point):
        return self.geometry.normal_at(point)