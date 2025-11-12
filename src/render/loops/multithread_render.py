import multiprocessing as mp
from typing import List, Tuple, Optional

from src.material.color import Color, to_u8
from src.render.helpers import ray_color
from src.shading import BlinnPhongShader
from .progress import ProgressDisplay, PreviewConfig
from .raytrace_loop import RenderLoop
from src.scene.camera import Camera
from src.geometry.world import World
from src.shading.shader_model import ShadingModel
from src.scene.light import Light

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
    Concrete RenderLoop that renders scanlines in parallel with multiprocessing.
    - Implements the abstract methods required by RenderLoop.
    - Uses module-level workers (picklable) with a shared state initializer.
    """

    def __init__(self,
                 cam: Camera,
                 world: World,
                 lights: List[Light],
                 shading_model: Optional[ShadingModel] = None,
                 progress: ProgressDisplay = ProgressDisplay.TQDM_IMAGE_PREVIEW,
                 preview_config: Optional[PreviewConfig] = None,
                 samples_per_pixel: int = 4,
                 max_depth: int = 3,
                 skybox: Optional[str] = None) -> None:

        super().__init__(cam, world, lights,
                         shading_model=shading_model or BlinnPhongShader(),
                         progress=progress,
                         preview_config=preview_config,
                         samples_per_pixel=samples_per_pixel,
                         max_depth=max_depth,
                         skybox=skybox)

    # todo duplicate code because of worker uses his own pixel function
    def render_pixel(self, i: int, j: int) -> Tuple[int, int, int]:
        width, height = self.width, self.height
        width_inv  = 1.0 / (width - 1) if width > 1 else 1.0
        height_inv = 1.0 / (height - 1) if height > 1 else 1.0
        jitter = ((-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25))

        u_base = (i * width_inv) - 0.5
        v_base = ((height - 1 - j) * height_inv) - 0.5

        acc = Color.custom_rgb(0, 0, 0)
        for s in range(self.samples_per_pixel):
            ju, jv = jitter[s & 3]
            ray = self.cam.make_ray(u_base + ju * width_inv, v_base + jv * height_inv)
            acc += ray_color(ray, self.world, self.lights, depth=self.max_depth,
                             shader=self.shader, skybox=self.skybox)
        col = acc * (1.0 / self.samples_per_pixel)
        return (to_u8(col.x), to_u8(col.y), to_u8(col.z))

    def render(self) -> Tuple[List[Tuple[int,int,int]], int, int]:
        width, height = self.width, self.height
        # Use 'spawn' on macOS to avoid fork-with-threads issues in IPython/Jupyter.
        ctx = mp.get_context("spawn")

        print("------------------------------------------------------------")
        print(f"Using {ctx.cpu_count()} CPU cores for rendering.")
        print("------------------------------------------------------------")

        pixels_u8: List[Tuple[int,int,int]] = [None] * (width * height)  # type: ignore

        # We want live previews as rows finish: use imap_unordered and update UI.
        with ctx.Pool(
            processes=ctx.cpu_count(),
            initializer=_init_worker,
            initargs=(self.cam, self.world, self.lights, self.shader,
                      self.samples_per_pixel, self.max_depth, self.skybox,
                      width, height)
        ) as pool:
            # schedule all rows
            for j, row in pool.imap_unordered(_render_row_worker, range(height), chunksize=1):
                # place row into final buffer
                base = j * width
                pixels_u8[base:base+width] = row
                # preview/progress hook on main process
                self.on_row_end_update_preview(j, pixels_u8)

        return pixels_u8, width, height