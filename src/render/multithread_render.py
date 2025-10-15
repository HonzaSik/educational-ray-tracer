import multiprocessing as mp
from src.material.color import Color, to_u8
from src.render.helpers import ray_color
from src.shading import BlinnPhongShader

# shared globals for worker processes
_STATE = {}


def _init(camera, world, lights, shader, spp, max_depth, skybox, width, height):
    _STATE["cam"] = camera
    _STATE["world"] = world
    _STATE["lights"] = lights
    _STATE["shader"] = shader
    _STATE["spp"] = spp
    _STATE["max_depth"] = max_depth
    _STATE["skybox"] = skybox
    _STATE["width"] = width
    _STATE["height"] = height


def _render_row(j: int):
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
    # prepare row buffer
    row = [None] * width
    # compute v coordinate for this row
    v_base = ((height - 1 - j) * height_inv) - 0.5

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


def render_multithreaded(camera, world, lights, samples_per_pixel=4, max_depth=3, skybox: str | None = None , shading_model=None):
    """
    Multithreaded rendering using multiprocessing.
    :param camera: Camera instance
    :param world: World instance
    :param lights: List of Light instances
    :param samples_per_pixel: Samples per pixel for anti-aliasing
    :param max_depth: Max recursion depth for ray tracing
    :param skybox: path to an HDR image
    :param shading_model: Shading model to use (default is Blinn-Phong)
    :return: list of pixel colors as (R, G, B) tuples, image width, image height
    """
    #select shader
    shader = shading_model or BlinnPhongShader()
    #gets image dimensions for faster access
    width, height = camera.resolution

    #setup multiprocessing
    ctx = mp.get_context("spawn")

    #print how many cores will be used
    print(f"------------------------------------------------------------")
    print(f"Using {ctx.cpu_count()} CPU cores for rendering.")
    print(f"------------------------------------------------------------")

    # use a pool of workers to render rows in parallel
    with ctx.Pool(processes=ctx.cpu_count(), initializer=_init, initargs=(camera, world, lights, shader, samples_per_pixel, max_depth, skybox, width, height)) as pool:
        results = pool.map(_render_row, range(height))

    #sort rows by their original index by default pool.map returns in arbitrary order
    rows_sorted = sorted(results, key=lambda x: x[0])
    pixels = [pix for _, row in rows_sorted for pix in row]

    return pixels, width, height