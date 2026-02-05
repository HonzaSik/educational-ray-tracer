from __future__ import annotations
from typing import Tuple, List
from random import random
from src.material.color import Color, to_u8
from .render_loop import RenderLoop
from src.render.helpers import cast_ray
from dataclasses import dataclass


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

            acc += cast_ray(
                ray=ray,
                lights=self.lights,
                depth=self.max_depth,
                shader=self.shader,
                skybox=self.skybox,
                scene=self.scene,
            )

        col = acc / self.spp
        return to_u8(col.r), to_u8(col.g), to_u8(col.b)  # todo color xyz to rgb

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
