# This module provides helper functions defined in educational notebooks

from typing import Tuple, List
from src import Color

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