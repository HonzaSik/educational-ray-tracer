from pathlib import Path

from IPython.core.display_functions import display
from PIL import Image as PILImage
from IPython.display import Image

# helper functions for image processing

def convert_ppm_to_png(ppm_path, png_path):
    """
    Convert a PPM image to PNG format.
    :param ppm_path: path to the PPM file
    :param png_path: path to save the PNG file
    :return: None
    """
    with open(ppm_path, "rb") as ppm_file:
        img = PILImage.open(ppm_file)
        img.save(png_path, "PNG")


def write_ppm(filename, pixels, w, h):
    """
    Write a PPM image file.
    :param filename: Name of the file to write
    :param pixels: List of (r, g, b) tuples
    :param w: Width of the image
    :param h: Height of the image
    :return: None
    """
    with open(filename, "w", encoding="ascii") as f:
        f.write(f"P3\n{w} {h}\n255\n")
        for (r, g, b) in pixels:
            f.write(f"{r} {g} {b}\n")


def ipynb_display_images(path: str | list[str] | None = None) -> None:
    """
    Display the rendered image or images in a Jupyter notebook.
    :param path: Path to the image file or list of image file paths.
    :return: None
    """

    if isinstance(path, list):
        for p in path:
            display(Image(filename=p))

    else:
        if path is None:
            raise ValueError("No image path provided for display.")
        display(Image(filename=path))