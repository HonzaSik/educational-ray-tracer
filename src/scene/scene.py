from dataclasses import dataclass
from src.scene.camera import Camera
from src.geometry.world import World
from src.scene.light import Light, LightType
from src.math import Vector
from src.math import Vertex
from pathlib import Path
from enum import Enum


# enum of render methods
class RenderMethod(Enum):
    SHADOW_TRACE = "phong"
    SHADOW_TRACE_MULTITHREADED = "phong_multithreaded"
    RASTERIZE = "rasterize"
    PBR = "pbr"


class ShadingModel(Enum):
    BLINN_PHONG = "blinn_phong"
    PREVIEW = "preview"
    PBR = "pbr"


class QualityPreset(Enum):
    ULTRA_LOW = "ultra_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


@dataclass
class Scene:
    """Container for all scene elements. World(objects), camera, lights."""
    world: World
    camera: Camera
    lights: list[Light]
    skybox_path: str | None = None

    def __str__(self) -> str:
        return f"Scene(world={self.world}, camera={self.camera}, lights={self.lights})"

    def __repr__(self) -> str:
        return self.__str__()

    # -------- Scene add/remove methods --------
    def add_light(self, light: Light) -> None:
        """
        Add a light to the scene.
        :param light: Light to add
        :return: None
        """
        self.lights.append(light)

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

    def set_world(self, world: World) -> None:
        """
        Set the world of the scene.
        :param world: World to set
        :return: None
        """
        self.world = world

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
        self.camera.fov = fov
        self.camera.__post_init__()

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
        self.camera.__post_init__()

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

        if self.world is None or not self.world.objects:
            raise ValueError("Scene must have a world with at least one object.")

        if not self.lights:
            raise ValueError("Scene must have at least one light.")

        #todo more validations

        print("Scene validation passed.")

    @staticmethod
    def _ensure_images_dir(path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)