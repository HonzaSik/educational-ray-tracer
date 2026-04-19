from __future__ import annotations
from typing import Tuple, List
from random import random
from src.material.color import Color, to_u8
from .render_loop import RenderLoop
from dataclasses import dataclass

@dataclass
class LinearRenderLoop(RenderLoop):
    """
    A basic single-threaded ray tracing render loop that processes the image line by line.
    Inherits from the abstract RenderLoop class and implements the render logic.
    """

    def render_pixel(self, i: int, j: int) -> Tuple[int, int, int]:
        u = (i + 0.5) / self.width * 2 - 1
        v = 1 - (j + 0.5) / self.height * 2

        acc = Color.custom_rgb(0, 0, 0)

        for _ in range(self.spp):
            du = (random() - 0.5) * 2 / self.width
            dv = (random() - 0.5) * 2 / self.height

            ray = self.camera.make_ray(u + du, v + dv)

            acc += self.integrator.cast_ray(ray=ray, depth=self.max_depth)

        col = acc / self.spp
        return to_u8(col.r), to_u8(col.g), to_u8(col.b)

    def render_all_pixels(self) -> Tuple[List[Tuple[int, int, int]], int, int]:
        pixels: List[Tuple[int, int, int]] = []
        total = self.width * self.height

        self.ui.start(total)

        for row in range(self.height):
            for i in range(self.width):
                rgb = self.render_pixel(i, row)
                pixels.append(rgb)

            self.on_row_end_update_preview(row, pixels)
            self.ui.update_pixel(self.width)

        self.ui.update_end(pixels)
        return pixels, self.width, self.height
