from __future__ import annotations
from dataclasses import dataclass

from src.math import Vertex
from src.geometry.primitive import Primitive
from src.material.material.material import Material
from src.geometry.ray import Ray, transform_point
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.transform import Transform, transform_normal


@dataclass
class Object:
    """
    Scene object composed of geometry and material.
    """
    geometry: Primitive
    material: Material
    transform: Transform | None = None

    def __post_init__(self):
        if self.transform is None:
            self.transform = Transform.identity()

    def intersect(self, ray: Ray, t_min=0.001, t_max=float("inf")):
        """
        Intersect the ray with the object's geometry, applying inverse transformation if necessary.
        Transforms the ray into object local space, performs intersection there, then transforms
        the hit point and normal back to world space.
        :param ray: Ray to intersect with the object
        :param t_min: minimum valid distance for intersection
        :param t_max: maximum valid distance for intersection
        :return: SurfaceInteraction if hit occurs, else None
        """
        world_ray = ray
        ray = ray.transformed(self.transform.inverse)

        geom_hit = self.geometry.intersect(ray, t_min, t_max)
        if geom_hit is None:
            return None

        geom_hit.point = transform_point(self.transform.matrix, geom_hit.point)
        geom_hit.dist = (geom_hit.point - world_ray.origin).norm()
        geom_hit.normal = transform_normal(self.transform.inverse_T, geom_hit.normal).normalize()

        return SurfaceInteraction(geom=geom_hit, material=self.material)

    def normal_at(self, point: Vertex) -> Vertex:
        """
        Compute surface normal at a world-space point.
        Transforms point to local space, queries geometry, transforms normal back.
        """
        local_point = transform_point(self.transform.inverse, point)
        local_normal = self.geometry.normal_at(local_point)
        return transform_normal(self.transform.inverse_T, local_normal).normalize()

    def translate(self, x: float, y: float, z: float) -> Object:
        self.transform = self.transform.combine(Transform.translate(x, y, z))
        return self

    def scale(self, scale_x: float, scale_y: float, scale_z: float) -> Object:
        self.transform = self.transform.combine(Transform.scale(scale_x, scale_y, scale_z))
        return self

    def rotate_y(self, angle_degrees: float) -> Object:
        self.transform = self.transform.combine(Transform.rotate_y(angle_degrees))
        return self

    def rotate_x(self, angle_degrees: float) -> Object:
        self.transform = self.transform.combine(Transform.rotate_x(angle_degrees))
        return self

    def rotate_z(self, angle_degrees: float) -> Object:
        self.transform = self.transform.combine(Transform.rotate_z(angle_degrees))
        return self