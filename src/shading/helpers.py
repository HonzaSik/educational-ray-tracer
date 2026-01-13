from src.scene.scene import Scene
from src.math import Vector
from src.geometry.ray import Ray
from src.scene.surface_interaction import SurfaceInteraction
from src.scene.light import Light

_BIAS = 1e-3

def tangent_basis(vec: Vector) -> tuple[Vector, Vector]:
    """
    Create a tangent basis (T, B) given a normal vector (vec).
    :param vec: Normal vector
    :return: (Tangent Vector, Bitangent Vector)
    """
    #helper vector to avoid degenerate cross product
    up = Vector(0, 1, 0) if abs(vec.y) < 0.999 else Vector(1, 0, 0)
    # compute tangent and bitangent
    tangent = up.cross(vec).normalize_ip()
    bitangent = vec.cross(tangent)
    return tangent, bitangent


def shadow_trace(geometry_hit: SurfaceInteraction, light_direction: Vector, light_distance: float,
                 scene: Scene) -> bool:
    """
    Trace a shadow ray from the hit point towards the light source.
    :param geometry_hit: HitPoint where the primary ray hit an object
    :param light_direction: Vector direction to the light source
    :param light_distance: float distance to the light source
    :param scene: Scene containing the objects to check for shadows
    :return: true if in shadow, false otherwise
    """

    if scene is None:
        raise ValueError("Scene must not be None for shadow tracing.")

    shadow_origin = geometry_hit.geom.point + geometry_hit.geom.normal * _BIAS
    shadow_ray = Ray(shadow_origin, light_direction)
    shadow_hit = scene.intersect(shadow_ray)
    return shadow_hit is not None and shadow_hit.geom.dist < light_distance


def light_dir_dist(geometry_hit: SurfaceInteraction, light: Light) -> tuple[Vector, float]:
    """
    Compute the direction and distance from the hit point to the light source.
    :param geometry_hit: HitPoint where the primary ray hit an object
    :param light: Light source
    :return: (direction Vector to light, distance float to light)
    """
    light_position = light.position
    to_light = light_position - geometry_hit.geom.point
    distance = to_light.norm()
    direction = to_light / distance if distance > 0 else Vector(0, 0, 0)
    return direction, distance
