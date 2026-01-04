from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple, List, Optional

from src.scene.camera import Camera
from src.scene.light import Light
from src.shading.shading_model import ShadingModel
from src.shading.blinn_phong_shader import BlinnPhongShader
from .progress import ProgressUI, PreviewConfig, ProgressDisplay
from src.scene.scene import Scene
from src.render.render_config import RenderConfig
from src.io.image_helper import write_ppm, convert_ppm_to_png
from src.render.post_process.post_process_pipeline import post_process_pipeline
from src.render.post_process.post_process_config import PostProcessConfig
from src.render.resolution import Resolution

class ImgFormat(Enum):
    PPM = "ppm"
    PNG = "png"

@dataclass
class RenderLoop(ABC):
    """
    Abstract render loop model.
    Provides basic structure for rendering with a camera, world, lights, and shading model.
    Handles progress reporting and image preview updates.

    Parameters:
    - scene: Scene object containing camera, world, and lights.
    - shading_model: Optional shading model to use. Defaults to Blinn-Phong if None
    - preview_config: Optional configuration for image preview during rendering.
    - render_config: Optional configuration for rendering parameters.
    - post_process_config: Optional configuration for post-processing steps.
    """

    scene: Scene = None
    shading_model: Optional[ShadingModel] = None
    preview_config: Optional[PreviewConfig] = None
    render_config: Optional[RenderConfig] = None
    post_process_config: Optional[PostProcessConfig] = None

    def __post_init__(self):
        # Initialize core components from the scene and configurations
        self.camera : Camera = self.scene.camera
        self.lights : List[Light] = self.scene.lights
        self.skybox : Optional[str] = self.scene.skybox_path if self.scene.skybox_path is not None else None

        # Set default shading model if none provided
        self.shader : ShadingModel = self.shading_model if self.shading_model is not None else BlinnPhongShader()

        # Set rendering parameters from render_config or use defaults
        self.spp : int = self.render_config.samples_per_pixel if self.render_config is not None else 1
        self.max_depth : int = self.render_config.max_depth if self.render_config is not None else 3
        self.width: int = self.render_config.resolution.width if self.render_config is not None else Resolution.R360p.width
        self.height: int = self.render_config.resolution.height if self.render_config is not None else Resolution.R360p.height

        # Set post-processing configuration
        self.post_process_config : PostProcessConfig = self.post_process_config if self.post_process_config is not None else PostProcessConfig()
        self.ui : ProgressUI = ProgressUI(
            mode = self.preview_config.progress_display if self.preview_config is not None else ProgressDisplay.NONE,
            width = self.width if self.preview_config is not None else Resolution.R360p.width,
            height = self.height if self.preview_config is not None else Resolution.R360p.height,
            preview = self.preview_config if self.preview_config is not None else PreviewConfig()
        )

        if self.spp <= 0:
            raise ValueError("Samples per pixel must be a positive integer.")
        if self.max_depth <= 0:
            raise ValueError("Max depth must be a positive integer.")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Image width and height must be positive integers.")
        if self.ui is None:
            raise ValueError("Progress UI must be initialized.")
        if self.camera is None:
            raise ValueError("Camera must be provided.")
        if self.lights is None:
            raise ValueError("Lights must be provided.")
        if self.shader is None:
            raise ValueError("Shading model must be provided.")

        self.camera.set_aspect_ratio(self.width / self.height)


    def on_row_end_update_preview(self, current_row: int, pixels_u8: List[Tuple[int, int, int]]) -> None:
        """
        Called at the end of each row to update preview if needed.
        :param current_row: Current row index.
        :param pixels_u8: Current list of rendered pixels as (R,G,B) uint8 tuples.
        :return:
        """
        config = self.ui.preview
        #checks if preview is enabled
        if self.ui.img_widget is not None and config.refresh_interval_rows > 0:
            # each interval_rows, update the preview or at the last row
            if ((current_row + 1) % config.refresh_interval_rows == 0) or (current_row + 1 == self.height):
                self.ui.update_row(pixels_u8, current_row + 1)

    @abstractmethod
    def render_pixel(self, i: int, j: int) -> Tuple[int, int, int]:
        """Return (R,G,B) uint8 for pixel (i,j)."""
        ...

    @abstractmethod
    def render_all_pixels(self) -> Tuple[List[Tuple[int, int, int]], int, int]:
        """Main render loop. Returns pixel list, width, height."""
        ...

    def render(self, filename: str, img_format_list: Optional[ImgFormat] = None) -> list[Path]:
        """
        Renders the scene and saves the output to a file in the specified formats.
        :param filename: Name of the output file.
        :param img_format_list: Desired image formats to save (PPM, PNG). If None, infers from filename extension.
        :return: Path to the saved image file.
        """
        if img_format_list is None:
            ext = Path(filename).suffix.lower()
            if ext == ".ppm":
                img_format_list = [ImgFormat.PPM]
            elif ext == ".png":
                img_format_list = [ImgFormat.PNG]
            else:
                raise ValueError("Unsupported file extension. Please use .ppm or .png or specify img_format_list.")

        #render all pixels only once
        pixels, width, height = self.render_all_pixels()
        saved_paths: [Path] = []

        if self.post_process_config.enabled:
            pixels, width, height = post_process_pipeline(
                pixels = pixels,
                width = width,
                height = height,
                config = self.post_process_config
            )

        for img_format in img_format_list:
            if img_format == ImgFormat.PPM:
                saved_paths.append(self._save_as_ppm(filename, pixels, width, height))
            elif img_format == ImgFormat.PNG:
                saved_paths.append(self._save_as_png(filename, pixels, width, height))
            else:
                raise ValueError(f"Unsupported image format: {img_format}")

        if saved_paths is None:
            raise RuntimeError("No image was saved. Please check the image format.")
        return saved_paths


    def _save_as_ppm(self, filename: str, pixels: List[Tuple[int, int, int]], width: int, height: int) -> Path:
        """
        Saves the rendered pixels to a PPM file.
        :param filename: Name of the output file.
        :param pixels: List of rendered pixels as (R,G,B) uint8 tuples.
        :param width: Width of the image.
        :param height: Height of the image.
        :return: Path to the saved PPM file.
        """
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        write_ppm(filename, pixels, width, height)
        return Path(filename)


    def _save_as_png(self, filename: str, pixels: List[Tuple[int, int, int]], width: int, height: int) -> Path:
        """
        Saves the rendered pixels to a PNG file.
        :param filename: Name of the output file.
        :param pixels: List of rendered pixels as (R,G,B) uint8 tuples.
        :param width: Width of the image.
        :param height: Height of the image.
        :return: Path to the saved PNG file.
        """
        ppm_temp_path = Path(filename).with_suffix(".ppm")
        self._save_as_ppm(ppm_temp_path.as_posix(), pixels, width, height)

        png_path = Path(filename)
        convert_ppm_to_png(ppm_temp_path.as_posix(), png_path.as_posix())

        #remove temporary ppm file
        ppm_temp_path.unlink(missing_ok=True)

        return png_path

