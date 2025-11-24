import multiprocessing as mp
from typing import List, Tuple, Optional
from src.material.color import Color, to_u8
from src.render.helpers import ray_color
from .progress import PreviewConfig
from .linear_ray_caster import RenderLoop
from src.shading.shading_model import ShadingModel
from src.render.render_config import RenderConfig
from src.scene.scene import Scene

# shared globals for worker processes
_STATE = {}


def _init_worker(camera, world, lights, shader, spp, max_depth, skybox, width, height):
    _STATE["cam"] = camera
    _STATE["world"] = world
    _STATE["lights"] = lights
    _STATE["shader"] = shader
    _STATE["spp"] = spp
    _STATE["max_depth"] = max_depth
    _STATE["skybox"] = skybox
    _STATE["width"] = width
    _STATE["height"] = height


def _render_row_worker(j: int):
    camera = _STATE["cam"]
    world = _STATE["world"]
    lights = _STATE["lights"]
    shader = _STATE["shader"]
    spp = _STATE["spp"]
    max_depth = _STATE["max_depth"]
    skybox = _STATE["skybox"]
    width = _STATE["width"]
    height = _STATE["height"]

    width_inv = 1.0 / (width - 1) if width > 1 else 1.0
    height_inv = 1.0 / (height - 1) if height > 1 else 1.0

    # 2x2 jitter pattern for 4 samples per pixel
    jitter = ((-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25))
    # compute v coordinate for this row
    v_base = ((height - 1 - j) * height_inv) - 0.5

    # initialize row pixel list
    row: List[Tuple[int, int, int]] = [None] * width

    # iterate over each pixel in the row and compute color
    for i in range(width):
        # compute u coordinate for this pixel
        u_base = (i * width_inv) - 0.5
        # initialize color accumulator for later averaging
        acc = Color.custom_rgb(0, 0, 0)
        for s in range(spp):
            # get jitter offsets
            ju, jv = jitter[s & 3]
            # create ray through pixel with jitter
            ray = camera.make_ray(u_base + ju * width_inv, v_base + jv * height_inv)
            acc += ray_color(ray, world, lights, depth=max_depth, shader=shader, skybox=skybox)
        # average accumulated color and convert to 0-255 range for PPM output
        col = acc * (1.0 / spp)
        row[i] = (to_u8(col.x), to_u8(col.y), to_u8(col.z))
    return j, row

class MultiProcessRowRenderLoop(RenderLoop):
    """
    A multiprocess ray tracing render loop that processes the image row by row using multiple CPU cores.
    Inherits from the abstract RenderLoop class and implements the render logic.
    """

    # todo duplicate code because of worker uses his own pixel function (need rework)
    def render_pixel(self, i: int, j: int) -> Tuple[int, int, int]:
        width, height = self.width, self.height
        width_inv  = 1.0 / (width - 1) if width > 1 else 1.0
        height_inv = 1.0 / (height - 1) if height > 1 else 1.0
        jitter = ((-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25))

        u_base = (i * width_inv) - 0.5
        v_base = ((height - 1 - j) * height_inv) - 0.5

        acc = Color.custom_rgb(0, 0, 0)
        for s in range(self.spp):
            ju, jv = jitter[s & 3]
            ray = self.camera.make_ray(u_base + ju * width_inv, v_base + jv * height_inv)
            acc += ray_color(ray, self.world, self.lights, depth=self.max_depth,
                             shader=self.shader, skybox=self.skybox)
        col = acc * (1.0 / self.spp)
        return (to_u8(col.x), to_u8(col.y), to_u8(col.z))

    def render_all_pixels(self) -> Tuple[List[Tuple[int,int,int]], int, int]:
        width, height = self.width, self.height
        # Use 'spawn' on macOS to avoid fork-with-threads issues in IPython/Jupyter.
        ctx = mp.get_context("spawn")
        print("------------------------------------------------------------")
        print(f"Using {ctx.cpu_count()} CPU cores for rendering.")
        print("------------------------------------------------------------")

        pixels_u8: List[Tuple[int,int,int]] = [None] * (width * height)  # type: ignore

        with ctx.Pool(
            processes=ctx.cpu_count(),
            initializer=_init_worker,
            initargs=(self.camera, self.world, self.lights, self.shader,
                      self.spp, self.max_depth, self.skybox,
                      width, height)
        ) as pool:
            num_workers = ctx.cpu_count()
            chunksize = max(1, height // (num_workers * 4))

            for j, row in pool.imap_unordered(_render_row_worker, range(height), chunksize=chunksize):
                # place row into final buffer
                base = j * width
                pixels_u8[base:base+width] = row
                # preview/progress hook on main process

                if j % 10 == 0 or j == height - 1:
                    self.on_row_end_update_preview(j, pixels_u8)

        return pixels_u8, width, height