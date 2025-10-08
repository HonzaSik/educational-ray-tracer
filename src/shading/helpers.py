from src.math import Vector
from src.geometry.ray import Ray
from src.geometry.hit_point import HitPoint
from src.geometry.world import World
from src.scene.light import Light

#shadow bias to avoid self-intersection
_BIAS = 1e-4

def shadow_trace(hit: HitPoint, light_direction: Vector, light_distance: float, world: World) -> bool:
    """
    Trace a shadow ray from the hit point towards the light source.
    :param hit: HitPoint where the primary ray hit an object
    :param light_direction: Vector direction to the light source
    :param light_distance: float distance to the light source
    :param world: World containing all scene objects
    :return: true if in shadow, false otherwise
    """
    # small offset to avoid self-intersection
    shadow_origin = hit.point + hit.normal * _BIAS

    shadow_ray = Ray(shadow_origin, light_direction)
    shadow_hit = world.intersect(shadow_ray)
    return shadow_hit is not None and shadow_hit.dist < light_distance

def light_dir_dist(hit: HitPoint, light: Light) -> tuple[Vector, float]:
    """
    Compute the direction and distance from the hit point to the light source.
    :param hit: HitPoint where the primary ray hit an object
    :param light: Light source
    :return: (direction Vector to light, distance float to light)
    """
    light_position = light.position
    to_light = light_position - hit.point
    distance = to_light.norm()
    direction = to_light / distance if distance > 0 else Vector(0, 0, 0)
    return direction, distance