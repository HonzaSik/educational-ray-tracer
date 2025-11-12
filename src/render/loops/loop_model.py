from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
from src.scene.camera import Camera
from src.geometry.world import World
from src.scene.light import Light
from src.shading.shader_model import ShadingModel
from src.shading.blinn_phong_shader import BlinnPhongShader
from .progress import ProgressUI, ProgressDisplay, PreviewConfig

class RenderLoop(ABC):
    """
    Abstract render loop model.
    Provides basic structure for rendering with a camera, world, lights, and shading model.
    Handles progress reporting and image preview updates.

    Attributes:
        cam (Camera): The camera used for rendering.
        world (World): The 3D world containing objects to be rendered.
        lights (List[Light]): List of lights in the scene.
        shader (ShadingModel): The shading model used for rendering.
        samples_per_pixel (int): Number of samples per pixel for anti-aliasing.
        max_depth (int): Maximum recursion depth for ray tracing.
        skybox: Optional skybox for background rendering.
    """
    def __init__(self,
                cam: Camera,
                world: World,
                lights: List[Light],
                shading_model: Optional[ShadingModel] = None,
                progress: ProgressDisplay = ProgressDisplay.TQDM_IMAGE_PREVIEW,
                preview_config: Optional[PreviewConfig] = None,
                samples_per_pixel = 1,
                max_depth = 5,
                skybox = None,
                ) -> None:

        self.cam : Camera = cam
        self.world : World = world
        self.lights : List[Light] = lights
        self.shader : ShadingModel = shading_model if shading_model is not None else BlinnPhongShader()
        self.samples_per_pixel : int = samples_per_pixel
        self.max_depth : int = max_depth
        self.skybox : Optional[str] = skybox
        self.width: int = cam.resolution.width
        self.height: int = cam.resolution.height
        self.ui : ProgressUI = ProgressUI(
            mode=progress,
            width=self.width,
            height=self.height,
            preview=preview_config
        )


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
    def render(self) -> Tuple[List[Tuple[int, int, int]], int, int]:
        """Main render loop. Returns pixel list, width, height."""
        ...
