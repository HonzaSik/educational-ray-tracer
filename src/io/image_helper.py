from pathlib import Path
from typing import Tuple, List

from IPython.core.display_functions import display
from PIL import Image as PILImage
from IPython.display import Image

def convert_ppm_to_png(ppm_path: str, png_path: str) -> None:
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

def image_to_ppm(filename: str, image: tuple[list[tuple[float, float, float]], int, int]) -> Path:
    """
    Write a PPM (P3) image file.
    Colors are stored internally in <0,1> and converted to <0,255>.
    """
    pixels, w, h = image

    with open(filename, "w", encoding="ascii") as f:
        f.write(f"P3\n{w} {h}\n255\n")
        for r, g, b in pixels:
            f.write(
                f"{max(0, min(255, int(r * 255)))} "
                f"{max(0, min(255, int(g * 255)))} "
                f"{max(0, min(255, int(b * 255)))}\n"
            )

    return Path(filename)

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

def ipnb_display_multiple_images_in_row(paths: list[str], row_size: int = 3) -> None:
    """
    Display multiple images in a single row in a Jupyter notebook.
    :param row_size: Number of images per row.
    :param paths: List of image file paths.
    :return: None
    """
    from IPython.display import HTML

    img_tags = []
    for p in paths:
        img_tags.append(f'<img src="{p}" style="display:inline-block; margin:5px; max-height:200px;">')

    html_content = ""
    for i in range(0, len(img_tags), row_size):
        row_imgs = img_tags[i:i + row_size]
        html_content += '<div style="white-space: nowrap;">' + ''.join(row_imgs) + '</div>'

    display(HTML(html_content))

def image_pipeline(image, idx: int = 0) -> str:
    """
    Complete image processing pipeline: save as PPM, convert to PNG. With indexed filename.
    :param image:
    :param idx:
    :return:
    """
    ppm = f"./images/img_{idx}.ppm"
    png = f"./images/img_{idx}.png"
    image_to_ppm(ppm, image)
    convert_ppm_to_png(ppm, png)
    return png