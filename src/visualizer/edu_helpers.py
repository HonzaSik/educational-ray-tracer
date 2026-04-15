# This module provides helper functions defined in educational notebooks
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List
from src import Color
import matplotlib.colors as mcol
import random
random.seed(42)  # for reproducibility

black = Color.linear_rgb(0.0, 0.0, 0.0)
white = Color.linear_rgb(1.0, 1.0, 1.0)
blue = Color.linear_rgb(0.0, 0.0, 1.0)
red = Color.linear_rgb(1.0, 0.0, 0.0)
green = Color.linear_rgb(0.0, 1.0, 0.0)
cyan = Color.linear_rgb(0.0, 1.0, 1.0)
magenta = Color.linear_rgb(1.0, 0.0, 1.0)
yellow = Color.linear_rgb(1.0, 1.0, 0.0)

Image = Tuple[List[Color], int, int]

def create_empty_image(width: int, height: int) -> Image:
    """
    Creates an empty image filled with black color. The image is represented as a tuple containing a list of pixel colors,
    the width, and the height. Each pixel color is initialized to black (0.0, 0.0, 0.0 in linear RGB).
    :param width: The width of the image in pixels
    :param height: The height of the image in pixels
    :return: Image - a tuple containing the list of pixel colors, width, and height
    """
    pixels = [black for _ in range(width * height)]
    return pixels, width, height

def set_pixel_color(image: Image, x: int, y: int, color: Color) -> None:
    """
    Sets the color of a specific pixel in the image. The (x, y) coordinates specify the pixel's position,
    and the color is a tuple representing the RGB values. The function checks if the coordinates are within the bounds of the image before setting the pixel color.
    :param image: The image represented as a tuple of (pixels, width, height)
    :param x: pixel's x-coordinate (horizontal position)
    :param y: pixel's y-coordinate (vertical position)
    :param color: color to set for the specified pixel, represented as a tuple of (R, G, B) values
    :return: None
    """
    pixels, width, height = image
    if 0 <= x < width and 0 <= y < height:
        pixels[y * width + x] = color


COL_MAP = mcol.LinearSegmentedColormap.from_list("noise", [
    (0.0, "#000000"),
    (0.25, "#0000ff"),
    (0.5, "#00ffff"),
    (0.75, "#ffff00"),
    (1.0, "#ff0000"),
])

# create a random permutation table for consistent noise generation
_perm_table = list(range(256))
random.shuffle(_perm_table)
# duplicate it to avoid overflow in permutation lookups
PERM = _perm_table + _perm_table

COLS = 10
ROWS = 8
RES = 100
SCALE = 0.45


def sample_grid(noise_fn):
    width, height = COLS * RES, ROWS * RES
    grid = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            grid[y, x] = noise_fn(x / RES, y / RES)
    return grid


def show(grid, title=""):
    """
    Simple visualization of a noise grid with optional gradient arrows.
    :param grid: 2D array of noise values to visualize
    :param title: Title for the plot
    :param vmin: Minimum value for color scaling (default -1)
    :param vmax: Maximum value for color scaling (default 1)
    :return: None
    """
    fig, ax = plt.subplots(figsize=(7, 7))

    img = ax.imshow(
        grid,
        origin="upper",
        extent=[0, COLS, ROWS, 0],
        cmap=COL_MAP,
        vmin=-1,
        vmax=1,
        interpolation="nearest",
        aspect="equal",
    )

    for x in range(COLS + 1):
        ax.axvline(x, color="blue", lw=1.2)
    for y in range(ROWS + 1):
        ax.axhline(y, color="blue", lw=1.2)

    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(0, COLS)
    ax.set_ylim(ROWS, 0)

    plt.colorbar(img, ax=ax, fraction=0.025)
    plt.tight_layout()
    plt.show()