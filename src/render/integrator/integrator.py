from abc import abstractmethod, ABC
from src.material.color import Color
from src.geometry.ray import Ray


class Integrator(ABC):

    scene: object # not a strict type, but should be a Scene for experimental purposes. Want to keep it flexible for different integrator implementations

    @abstractmethod
    def cast_ray(self, ray: Ray, depth: int | None = None) -> Color:
        """
        Cast a ray into the scene and compute the resulting color. This method should be implemented by subclasses to define specific ray tracing behavior (e.g., direct illumination, path tracing, etc.). In a recursive integrator, this method will typically call itself recursively to handle reflections, refractions, and other effects that require multiple ray bounces.
        :param ray: The ray to cast into the scene.
        :param depth: The current recursion depth, which can be used to limit how many times the ray can bounce. If None, it should use a default maximum depth defined in the integrator.
        :return: The color resulting from casting the ray, which may include contributions from direct illumination, reflections, refractions, and other effects depending on the integrator's implementation.
        """
        raise NotImplementedError