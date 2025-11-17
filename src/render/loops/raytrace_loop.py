from __future__ import annotations
from typing import Tuple, Optional, List
from random import random
from src.material.color import Color, to_u8
from src.shading.shader_model import ShadingModel
from src.scene.light import Light
from src.scene.camera import Camera
from src.geometry.world import World
from .loop_model import RenderLoop
from .progress import ProgressDisplay, PreviewConfig
from src.render.helpers import ray_color
from dataclasses import dataclass

@dataclass
class LineRenderLoop(RenderLoop):
    """
    Reference implementation using your current ray tracer (Blinn-Phong by default).
    Only render_pixel() is specific; the loop + UI come from BaseRenderLoop.
    """
    def __init__(self,
                 cam: Camera,
                 world: World,
                 lights: List[Light],
                 samples_per_pixel: int = 10,
                 max_depth: int = 5,
                 skybox: Optional[str] = None,
                 shading_model: Optional[ShadingModel] = None,
                 progress: ProgressDisplay = ProgressDisplay.TQDM_IMAGE_PREVIEW,
                 preview_cfg: Optional[PreviewConfig] = None,
                 ) -> None:

        super().__init__(cam, world, lights, shading_model, progress, preview_cfg)
        self.spp = samples_per_pixel
        self.max_depth = max_depth
        self.skybox = skybox


    def render_pixel(self, i: int, j: int) -> Tuple[int, int, int]:

        u_base = (i / (self.width - 1)) - 0.5
        v_base = ((self.height - 1 - j) / (self.height - 1)) - 0.5

        acc = Color.custom_rgb(0, 0, 0)
        for _ in range(self.spp):
            du = (random() - 0.5) / (self.width - 1)
            dv = (random() - 0.5) / (self.height - 1)
            ray = self.cam.make_ray(u_base + du, v_base + dv)

            acc += ray_color(
                ray = ray,
                world = self.world,
                lights = self.lights,
                depth = self.max_depth,
                shader = self.shader,
                skybox = self.skybox
            )

        col = acc / self.spp
        return to_u8(col.x), to_u8(col.y), to_u8(col.z) #todo color xyz to rgb


    def render(self) -> Tuple[List[Tuple[int, int, int]], int, int]:
        pixels: List[Tuple[int, int, int]] = []
        total = self.width * self.height

        self.ui.start(total)

        for row in range(self.height):
            for i in range(self.width):

                rgb = self.render_pixel(i, row)
                pixels.append(rgb)

            self.on_row_end_update_preview(row, pixels)

        self.ui.update_end(pixels)
        return pixels, self.width, self.height
