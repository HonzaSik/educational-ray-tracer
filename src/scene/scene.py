from dataclasses import dataclass

from src.render import LineRenderLoop, MultiProcessRowRenderLoop
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
from src.shading import BlinnPhongShader, NormalShader, DepthShader, DiffShader, HashMethod, DotProductShader, CurvatureShader
from enum import Enum
from src.render.loops.progress import ProgressDisplay, PreviewConfig


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

    def render(self, quality: QualityPreset = QualityPreset.MEDIUM,
               render_method: RenderMethod = RenderMethod.SHADOW_TRACE,
               shading_model: ShadingModel = ShadingModel.BLINN_PHONG,
               image_png_path: str = "./images/render.png") -> str:
        """
        Render the scene with specified quality, method, and shading model. Defaults to medium quality, shadow trace method, and Blinn-Phong shading.
        :param quality: Quality preset for rendering
        :param render_method: Rendering method to use
        :param shading_model: Shading model to apply
        :param image_png_path: Path to save the rendered image
        :return: Path to the saved image
        """
        quality_settings = {
            QualityPreset.ULTRA_LOW: (1, 1),
            QualityPreset.LOW: (1, 3),
            QualityPreset.MEDIUM: (5, 5),
            QualityPreset.HIGH: (10, 10),
            QualityPreset.ULTRA: (20, 15),
        }
        samples_per_pixel, max_depth = quality_settings[quality]

        if render_method == RenderMethod.SHADOW_TRACE:
            if shading_model == ShadingModel.BLINN_PHONG:
                return self.render_phong(samples_per_pixel=samples_per_pixel, max_depth=max_depth,
                                         image_png_path=image_png_path)
        elif render_method == RenderMethod.SHADOW_TRACE_MULTITHREADED:
            return self.render_multithreaded(samples_per_pixel=samples_per_pixel, max_depth=max_depth,
                                             image_png_path=image_png_path)
        else:
            raise NotImplementedError(
                f"Render method {render_method} with shading model {shading_model} not implemented yet.")

    def render_preview(self, shader: ShadingModel | None = None, image_preview: bool = True) -> str:
        """
        Render a quick preview of the scene from the camera's perspective in 144p resolution if not specified.
        :return: Path to the saved image
        """
        start_time = time()

        #todo make this not hardcoded
        # shader = DiffShader(a= NormalShader(), b=DepthShader(), hash_method=HashMethod.HALF_IMAGE)
        shader = NormalShader()
        # shader = DepthShader()
        # shader = DotProductShader()
        # shader = CurvatureShader()

        lights = self.get_all_lights()
        print(f"Rendering preview at resolution {self.camera.resolution} with FOV {self.camera.fov}")

        if not image_preview:
            preview_cfg = PreviewConfig(refresh_interval_rows=0, show_status=False)
            progress_mode = ProgressDisplay.TQDM_CONSOLE
        else:
            preview_cfg = PreviewConfig(refresh_interval_rows=30, show_status=True)
            progress_mode = ProgressDisplay.TQDM_IMAGE_PREVIEW

        loop = LineRenderLoop(
        cam=self.camera,
        world=self.world,
        lights=lights,
        samples_per_pixel=5,
        max_depth=1,
        skybox=None,
        shading_model=shader,
        progress= progress_mode,
        preview_cfg= preview_cfg
        )

        p_px, p_w, p_h = loop.render()

        write_ppm("./images/preview.ppm", p_px, p_w, p_h)
        convert_ppm_to_png("./images/preview.ppm", "./images/preview.png")
        print(f"Preview render took {time() - start_time:.2f} seconds")
        display(Image(filename="./images/preview.png"))
        return "./images/preview.png"

    def render_phong(self, image_png_path: str = "./images/phong.png", samples_per_pixel: int = 2,
                     max_depth: int = 5) -> str:
        """
        Render the scene using Phong shading and save PNG (and an intermediate PPM).
        Returns the PNG path as a string.
        """
        png_path = Path(image_png_path)
        ppm_path = png_path.with_suffix(".ppm")
        self._ensure_images_dir(png_path)

        lights = self.get_all_lights()

        shader = BlinnPhongShader()

        loop = LineRenderLoop(
            samples_per_pixel=samples_per_pixel,
            max_depth=max_depth,
            cam=self.camera,
            world=self.world,
            lights=lights,
            skybox=self.skybox_path,
            shading_model=shader
        )

        pixels, w, h = loop.render()

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

    def render_multithreaded(self, samples_per_pixel: int = 10, max_depth: int = 5, shading_model=None,
                             image_png_path: str = "./images/fast_render.png") -> str:
        """
        Render the scene using ray tracing and save PNG (and an intermediate PPM).
        Returns the PNG path as a string.
        """
        png_path = Path(image_png_path)
        ppm_path = png_path.with_suffix(".ppm")
        self._ensure_images_dir(png_path)

        skybox = self.skybox_path
        print(f"Using skybox: {skybox}")

        lights = self.get_all_lights()

        print(
            f"Rendering fast at resolution {self.camera.resolution} with FOV {self.camera.fov} and samples_per_pixel={samples_per_pixel}, max_depth={max_depth}")
        print(
            f"No progress bar in multithreaded mode - switch to other render method for that if needed - this is supposed to be fast!")

        if shading_model is None:
            shader = BlinnPhongShader()
        else:
            shader = shading_model

        # call your renderer
        loop = MultiProcessRowRenderLoop(
            samples_per_pixel=samples_per_pixel,
            max_depth=max_depth,
            world=self.world,
            lights=lights,
            skybox=skybox,
            shading_model=shader,
            cam=self.camera
        )

        pixels, w, h = loop.render()

        # save to disk
        write_ppm(str(ppm_path), pixels, w, h)

        convert_ppm_to_png(str(ppm_path), str(png_path))
        print(f"Fast render saved to {png_path}")

        return str(png_path)