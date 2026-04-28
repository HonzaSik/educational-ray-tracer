from dataclasses import dataclass, field
from src.geometry.ray import Ray
from src.scene.camera.camera import Camera
from src.scene.light import Light, LightType
from src.math import Vector
from src.math import Vertex
from pathlib import Path
from src.scene.object import Object
from src.scene.surface_interaction import SurfaceInteraction


@dataclass
class Scene:
    camera: Camera
    lights: list[Light] = field(default_factory=list)
    objects: list[Object] = field(default_factory=list)
    skybox: str | None = None # path to skybox texture HDR or "black", "white", or "sky" for built-in options


    def __str__(self) -> str:
        return f"Scene(camera={self.camera}, lights={self.lights}, primitives={self.objects}, skybox={self.skybox})"

    def __repr__(self) -> str:
        return self.__str__()

    # -------- Scene add/remove methods --------
    def add_objects(self, objects: Object | list[Object]) -> None:
        """
        Add one or more primitives to the scene.
        If the scene has no primitives, it initializes the list.
        :param objects:
        :return: None
        """
        if self.objects is None:
            self.objects = []

        if isinstance(objects, Object):
            self.objects.append(objects)
        elif isinstance(objects, list):
            self.objects.extend(objects)
        else:
            raise TypeError("primitives must be a Primitive or a list of Primitives")

    def in_shadow(self, point: Vertex, light: Light) -> bool:
        """
        Check if a point is in shadow with respect to a given light source.
        :param point: Point to check for shadow
        :param light: Light source to check against
        :return: True if in shadow, False otherwise
        """
        light_dir = (light.position - point).normalize()
        light_distance = (light.position - point).norm()

        shadow_origin = point + light_dir * 1e-3
        shadow_ray = Ray(origin=shadow_origin, direction=light_dir)

        hit = self.intersect(shadow_ray)
        return hit is not None and hit.geom.dist < light_distance

    def remove_object(self, obj: Object) -> None:
        """
        Remove an object from the scene.
        :param obj: Object to remove
        :return: None
        """
        if self.objects is not None and obj in self.objects:
            self.objects.remove(obj)

    def clear_objects(self) -> None:
        """
        Clear all objects from the scene.
        :return: None
        """
        if self.objects is not None:
            self.objects.clear()

    # The hit point is currently computed directly in the scene.
    # Later, this will likely be moved to a dedicated abstract method
    # to better support acceleration structures.
    # For now it is not a big deal since it uses only few objects for education and is not a bottleneck
    def intersect(self, ray: Ray) -> SurfaceInteraction | None:
        """
        Intersect a ray with the scene's objects.
        :param ray: Ray to intersect
        :return: SurfaceInteraction if hit, None otherwise
        """
        if self.objects is None:
            return None

        closest_hit = None
        closest_distance = float('inf')

        for primitive in self.objects:
            hit = primitive.intersect(ray)
            if hit and hit.geom.dist < closest_distance:
                closest_distance = hit.geom.dist
                closest_hit = hit

        return closest_hit

    def get_objects(self) -> list[Object]:
        """
        Get all objects in the scene.
        :return: List of objects
        """
        return self.objects if self.objects is not None else []

    def add_lights(self, lights: Light | list[Light]) -> None:
        """Add one light or an iterable of lights to the scene."""
        if isinstance(lights, Light):
            self.lights.append(lights)
        elif isinstance(lights, list):
            self.lights.extend(lights)
        else:
            raise TypeError("lights must be a Light or an iterable of Lights")

    def remove_light(self, light: Light) -> None:
        """
        Remove a light from the scene.
        :param light: Light to remove
        :return: None
        """
        self.lights.remove(light)

    def translate_light(self, light: Light, translation: Vector) -> None:
        """
        Translate a light by a given vector.
        :param light: Light to translate
        :param translation: Vector to translate the light
        :return: None
        """
        light.translate(translation)

    def clear_lights(self) -> None:
        """
        Clear all lights from the scene.
        :return: None
        """
        self.lights.clear()

    def set_camera(self, camera: Camera) -> None:
        """
        Set the camera of the scene.
        :param camera: Camera to set
        :return: None
        """
        self.camera = camera

    # -------- camera manipulation methods --------

    def translate_camera(self, translation: Vector) -> None:
        """
        Translate the camera by a given vector.
        :param translation: Vector to translate the camera
        :return: None
        """
        self.camera.translate(translation)

    def set_camera_fov(self, fov: float) -> None:
        """
        Set the field of view of the camera.
        :param fov: Field of view in degrees
        :return: None
        """
        self.camera.fov_deg = fov
        self.camera.update_camera()

    def move_camera_to(self, position: Vertex) -> None:
        """
        Move the camera to a given position.
        :param position: Position to move the camera to
        :return: None
        """
        self.camera.origin = position

    def look_at(self, target: Vertex) -> None:
        """
        Make the camera look at a given target point.
        :param target: Target point to look at
        :return: None
        """
        new_direction = (target - self.camera.origin).normalize()
        self.camera.direction = new_direction
        self.camera.update_camera()

    def get_camera(self) -> Camera:
        """
        Get the current camera of the scene.
        :return: Camera
        """
        return self.camera

    def zoom_camera(self, factor: float) -> None:
        """
        Zoom the camera in or out by a given factor. Factor < 1.0 zooms in, > 1.0 zooms out.
        :param factor: Zoom factor
        :return: None
        """
        self.camera.zoom(factor)

    def get_point_lights(self) -> list[Light]:
        """
        Get all point lights in the scene.
        :return: List of point lights
        """
        point_lights = [light for light in self.lights if isinstance(light, Light) and light.type == LightType.POINT]
        return point_lights

    def get_all_lights(self) -> list[Light]:
        """
        Get all lights in the scene.
        :return: List of all lights
        """
        return self.lights

    def get_all_not_ambient_lights(self) -> list[Light]:
        """
        Get all non-ambient lights in the scene.
        :return: List of non-ambient lights
        """
        return [light for light in self.lights if light.type != LightType.AMBIENT]

    def get_ambient_light(self) -> Light | None:
        """
        Get the ambient light in the scene, if any.
        :return: Ambient light or None if not found
        """
        for light in self.lights:
            if light.type == LightType.AMBIENT:
                return light
        return None

    def validate(self) -> None:
        """
        Validate the scene configuration.
        """
        if self.camera is None:
            raise ValueError("Scene must have a camera.")

        if not self.lights:
            raise ValueError("Scene must have at least one light.")

        print("Scene validation passed.")

    def normal_at(self, point: Vertex) -> Vector:
        """
        Get the normal vector at a given point in the scene by intersecting a ray from above.
        Used for curvature shader to approximate curvature by sampling normals at nearby points.
        :param point: Point to get the normal at
        :return: Normal vector at the point
        """
        ray = Ray(origin=point + Vector(0, 1e-3, 0), direction=Vector(0, -1, 0))
        hit = self.intersect(ray)
        if hit is not None:
            return hit.geom.normal.normalize()
        else:
            return Vector(0, 1, 0)

    @staticmethod
    def _ensure_images_dir(path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

    def set_skybox(self, skybox_path: str) -> None:
        """
        Set the HFR skybox texture for the scene.
        :param skybox_path: Path to the skybox texture or "black", "white", or "sky" for built-in options
        :return: None
        """
        self.skybox = skybox_path
        self.camera.update_camera()
