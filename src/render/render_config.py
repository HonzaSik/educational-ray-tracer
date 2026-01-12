from dataclasses import dataclass
from src.render.resolution import Resolution


@dataclass
class RenderConfig:
    """
    Configuration for rendering settings such as resolution, samples per pixel, max depth, and skybox.
    Attributes:
        resolution (Resolution): The output image resolution.
        samples_per_pixel (int): Number of samples per pixel for antialiasing.
        max_depth (int): Maximum recursion depth for ray tracing.
    """
    resolution: Resolution = Resolution.R360p
    samples_per_pixel: int = 1
    max_depth: int = 5

    def __post_init__(self):
        if self.samples_per_pixel <= 0:
            raise ValueError("Samples must be a positive integer.")
        if self.max_depth <= 0:
            raise ValueError("Max depth must be a positive integer.")

    def set_resolution(self, resolution: Resolution) -> None:
        self.resolution = resolution

    def set_samples_per_pixel(self, samples: int) -> None:
        if samples <= 0:
            raise ValueError("Samples must be a positive integer.")
        self.samples_per_pixel = samples

    def set_max_depth(self, depth: int) -> None:
        if depth <= 0:
            raise ValueError("Max depth must be a positive integer.")
        self.max_depth = depth
