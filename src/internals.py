# Usage:
#       from src.internals import * gets you access to all the public API of the library and internals tha can be used by users to experiment with library.

from .geometry import (
    Ray,
    GeometryHit,
)

from .math import (
    Vec3,
    reflect,
    refract,
)

from .scene import (
    SurfaceInteraction,
    Light,
    LightType,
)

from .material import (
    Material,
    Noise,
)

from .shading import (
    LocalShading,
    apply_noise_normal_perturbation,
)

from .render import (
    Integrator,
    RenderLoop,
    ImgFormat,
)

from .io import (
    write_ppm,
    image_to_ppm,
    convert_ppm_to_png,
    image_pipeline
)

from .visualizer import (
    Visualizer,
)

__all__ = [
    "Vec3",
    "SurfaceInteraction", "Light", "LightType",
    "Material", "Noise",
    "LocalShading", "apply_noise_normal_perturbation",
    "Integrator", "RenderLoop", "ImgFormat",
    "write_ppm", "image_to_ppm", "convert_ppm_to_png",
    "Ray", "GeometryHit",
    "reflect", "refract",
    "image_pipeline",
    "Visualizer",
]
