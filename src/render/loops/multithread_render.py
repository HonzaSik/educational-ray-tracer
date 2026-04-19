from __future__ import annotations
import multiprocessing as mp
from random import random
from typing import List, Tuple

from src.material.color import Color, to_u8
from .linear_render_loop import RenderLoop

# shared globals for worker processes
_STATE = {}


def _init_worker(integrator, spp, max_depth, width, height):
    _STATE["integrator"] = integrator
    _STATE["spp"]        = spp
    _STATE["max_depth"]  = max_depth
    _STATE["width"]      = width
    _STATE["height"]     = height


def _render_row_worker(j: int):
    integrator = _STATE["integrator"]
    spp        = _STATE["spp"]
    max_depth  = _STATE["max_depth"]
    width      = _STATE["width"]
    height     = _STATE["height"]

    row: List[Tuple[int, int, int]] = [None] * width

    for i in range(width):
        u = (i + 0.5) / width * 2 - 1
        v = 1 - (j + 0.5) / height * 2

        acc = Color.custom_rgb(0, 0, 0)
        for _ in range(spp):
            du = (random() - 0.5) * 2 / width
            dv = (random() - 0.5) * 2 / height
            ray = integrator.scene.camera.make_ray(u + du, v + dv)
            acc += integrator.cast_ray(ray=ray, depth=max_depth)

        col = acc / spp
        row[i] = (to_u8(col.r), to_u8(col.g), to_u8(col.b))

    return j, row


class MultiProcessRowRenderLoop(RenderLoop):
    """
    A multiprocess ray tracing render loop that processes the image row by row
    using multiple CPU cores. Pixel sampling is identical to LinearRayCaster.
    """

    def render_pixel(self, i: int, j: int) -> Tuple[int, int, int]:
        u = (i + 0.5) / self.width * 2 - 1
        v = 1 - (j + 0.5) / self.height * 2

        acc = Color.custom_rgb(0, 0, 0)
        for _ in range(self.spp):
            du = (random() - 0.5) * 2 / self.width
            dv = (random() - 0.5) * 2 / self.height
            ray = self.integrator.scene.camera.make_ray(u + du, v + dv)
            acc += self.integrator.cast_ray(ray=ray, depth=self.max_depth)

        col = acc / self.spp
        return (to_u8(col.r), to_u8(col.g), to_u8(col.b))

    def render_all_pixels(self) -> Tuple[List[Tuple[int, int, int]], int, int]:
        width, height = self.width, self.height

        # 'spawn' avoids fork-with-threads issues on macOS / in Jupyter
        ctx = mp.get_context("spawn")
        n_cores = ctx.cpu_count()
        print("------------------------------------------------------------")
        print(f"Using {n_cores} CPU cores for rendering.")
        print("------------------------------------------------------------")

        pixels_u8: List[Tuple[int, int, int]] = [None] * (width * height)  # type: ignore

        chunksize = max(1, height // (n_cores * 4))

        with ctx.Pool(
            processes=n_cores,
            initializer=_init_worker,
            initargs=(self.integrator, self.spp, self.max_depth, width, height),
        ) as pool:
            for j, row in pool.imap_unordered(_render_row_worker, range(height), chunksize=chunksize):
                base = j * width
                pixels_u8[base : base + width] = row

                if j % 10 == 0 or j == height - 1:
                    self.on_row_end_update_preview(j, pixels_u8)

        return pixels_u8, width, height