from typing import List, Tuple
from PIL import Image
import numpy as np
from src.render.post_process.post_process_config import PostProcessConfig


def post_process_pipeline(config: PostProcessConfig, pixels: List[Tuple[int, int, int]], width: int, height: int) -> \
Tuple[
    List[Tuple[int, int, int]], int, int]:
    """
    Applies post-processing steps to the rendered image based on the configuration.
    """
    if config.enabled is False:
        return pixels, width, height

    if config.scale_factor > 1:
        pixels, width, height = _upscale_image(
            pixels,
            width,
            height,
            config.scale_factor,
        )

    return pixels, width, height


def _upscale_image(
        pixels: List[Tuple[int, int, int]],
        width: int,
        height: int,
        scale_factor: int,
) -> Tuple[List[Tuple[int, int, int]], int, int]:
    """
    Upscale an image represented as a flat list of RGB tuples.

    :param pixels: flat list [(r, g, b), ...]
    :param width: original width
    :param height: original height
    :param scale_factor: upscale factor
    :return: (new_pixels_list, new_width, new_height)
    """

    # conver to np array and PIL image
    arr = np.array(pixels, dtype=np.uint8).reshape((height, width, 3))
    img = Image.fromarray(arr, mode="RGB")

    # Resampling.NEAREST,
    # Resampling.BILINEAR,
    # Resampling.BICUBIC,
    # Resampling.LANCZOS,
    # Resampling.BOX,
    # Resampling.HAMMING,
    scaled_pixels = img.resize((scale_factor * width, scale_factor * height), resample=Image.BICUBIC)

    # convert back
    scaled_array = np.asarray(scaled_pixels, dtype=np.uint8)
    scaled_pixels = [tuple(px) for row in scaled_array for px in row]

    return scaled_pixels, scale_factor * width, scale_factor * height
