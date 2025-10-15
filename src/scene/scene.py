from dataclasses import dataclass

from src.render import render, render_multithreaded
from src.scene.camera import Camera
from src.geometry.world import World
from src.scene.light import Light, LightType
from src.math import Vector
from src.math import Vertex
from pathlib import Path
from src.io.resolution import Resolution

#todo move elsewhere just for testing
from src.io.image_helper import write_ppm, convert_ppm_to_png
from IPython.display import Image, display
from time import time

from src.shading import BlinnPhongShader


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

    def rotate_camera(self, axis: Vector, angle: float) -> None:
        """
        Rotate the camera around a given axis by a given angle.
        :param axis: Axis to rotate around
        :param angle: Angle in degrees
        :return: None
        """
        self.camera.rotate(axis, angle)

    def set_camera_fov(self, fov: float) -> None:
        """
        Set the field of view of the camera.
        :param fov: Field of view in degrees
        :return: None
        """
        self.camera.fov = fov
        self.camera.__post_init__()

    def set_camera_resolution(self, resolution) -> None:
        """
        Set the resolution of the camera.
        :param resolution: Resolution to set
        :return: None
        """
        self.camera.set_resolution(resolution)
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


    def translate_light(self, light: Light, translation: Vector) -> None:
        """
        Translate a light by a given vector.
        :param light: Light to translate
        :param translation: Vector to translate the light
        :return: None
        """
        light.translate(translation)


    def render_preview(self, resolution: Resolution = Resolution.R144p) -> str:
        """
        Render a quick preview of the scene from the camera's perspective in 144p resolution if not specified.
        :return: Path to the saved image
        """
        start_time = time()
        lights = self.get_point_lights()
        print(f"Rendering preview at resolution {self.camera.resolution} with FOV {self.camera.fov}")
        p_px, p_w, p_h = render(samples_per_pixel=1, max_depth=1, cam=self.camera, world=self.world, lights=lights, skybox=None)
        write_ppm("./images/preview.ppm", p_px, p_w, p_h)
        convert_ppm_to_png("./images/preview.ppm", "./images/preview.png")
        print(f"Preview render took {time() - start_time:.2f} seconds")
        display(Image(filename="./images/preview.png"))
        return "./images/preview.png"


    def render_phong(self, image_png_path: str = "./images/phong.png", samples_per_pixel: int = 2, max_depth: int = 5) -> str:
        """
        Render the scene using Phong shading and save PNG (and an intermediate PPM).
        Returns the PNG path as a string.
        """
        png_path = Path(image_png_path)
        ppm_path = png_path.with_suffix(".ppm")
        self._ensure_images_dir(png_path)

        lights = self.get_point_lights()

        shader = BlinnPhongShader()

        # call your renderer
        pixels, w, h = render(
            samples_per_pixel=samples_per_pixel,
            max_depth=max_depth,
            cam=self.camera,
            world=self.world,
            lights=lights,
            skybox=self.skybox_path,
            shading_model=shader
        )

        # save to disk
        write_ppm(str(ppm_path), pixels, w, h)
        convert_ppm_to_png(str(ppm_path), str(png_path))
        print(f"Phong render saved to {png_path}")

        return str(png_path)


    def get_point_lights(self) -> list[Light]:
        """
        Get all point lights in the scene.
        :return: List of point lights
        """
        point_lights = [light for light in self.lights if isinstance(light, Light) and light.type == LightType.POINT]
        return point_lights


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

    def render_multithreaded(self, samples_per_pixel: int = 10, max_depth: int = 5, shading_model=None, image_png_path: str = "./images/fast_render.png") -> str:
        """
        Render the scene using ray tracing and save PNG (and an intermediate PPM).
        Returns the PNG path as a string.
        """
        png_path = Path(image_png_path)
        ppm_path = png_path.with_suffix(".ppm")
        self._ensure_images_dir(png_path)

        skybox = self.skybox_path
        print(f"Using skybox: {skybox}")

        lights = self.get_point_lights()

        print(f"Rendering fast at resolution {self.camera.resolution} with FOV {self.camera.fov} and samples_per_pixel={samples_per_pixel}, max_depth={max_depth}")
        print(f"No progress bar in multithreaded mode - switch to other render method for that if needed - this is supposed to be fast!")

        if shading_model is None:
            shader = BlinnPhongShader()
        else:
            shader = shading_model

        # call your renderer
        pixels, w, h = render_multithreaded(
            samples_per_pixel=samples_per_pixel,
            max_depth=max_depth,
            camera=self.camera,
            world=self.world,
            lights=lights,
            skybox=skybox,
            shading_model=shader
        )

        # save to disk
        write_ppm(str(ppm_path), pixels, w, h)

        convert_ppm_to_png(str(ppm_path), str(png_path))
        print(f"Fast render saved to {png_path}")

        return str(png_path)