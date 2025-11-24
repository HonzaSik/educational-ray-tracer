from __future__ import annotations
from typing import Tuple, Optional, List
from random import random
from src.material.color import Color, to_u8
from src.shading.shading_model import ShadingModel
from .render_loop import RenderLoop
from .progress import PreviewConfig
from src.render.helpers import ray_color
from dataclasses import dataclass

from src.render.render_config import RenderConfig
from src.scene.scene import Scene
from src.render.post_process.post_process_config import PostProcessConfig


@dataclass
class LinearRayCaster(RenderLoop):
    """
    A basic single-threaded ray tracing render loop that processes the image line by line.
    Inherits from the abstract RenderLoop class and implements the render logic.
    """

    def render_pixel(self, i: int, j: int) -> Tuple[int, int, int]:

        u_base = (i / (self.width - 1)) - 0.5
        v_base = ((self.height - 1 - j) / (self.height - 1)) - 0.5

        acc = Color.custom_rgb(0, 0, 0)
        for _ in range(self.spp):
            du = (random() - 0.5) / (self.width - 1)
            dv = (random() - 0.5) / (self.height - 1)
            ray = self.camera.make_ray(u_base + du, v_base + dv)

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


    def render_all_pixels(self) -> Tuple[List[Tuple[int, int, int]], int, int]:
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