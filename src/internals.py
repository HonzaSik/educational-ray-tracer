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
    PhongMaterialSample,
    MaterialSample,
)

from .shading import (
    LocalShading,
    apply_noise_normal_perturbation,
    light_dir_dist,
    in_shadow,
)

from .render import (
    Integrator,
    RenderLoop,
    ImgFormat,
    fresnel_schlick,
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

from .math import (
    clamp_float_01, interpolate, perlin_fade, lerp
)


__all__ = [
    "Vec3",
    "SurfaceInteraction", "Light", "LightType",
    "Material", "Noise", "PhongMaterialSample", "MaterialSample",
    "LocalShading", "apply_noise_normal_perturbation",
    "Integrator", "RenderLoop", "ImgFormat",
    "write_ppm", "image_to_ppm", "convert_ppm_to_png",
    "Ray", "GeometryHit",
    "reflect", "refract",
    "image_pipeline",
    "Visualizer",
    "light_dir_dist", "in_shadow",
    "fresnel_schlick",
    "clamp_float_01", "interpolate", "perlin_fade", "lerp"
]
