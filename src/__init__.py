# Usage: from src import *  # Import all public classes and functions from the src package
# For internal use, you can also import
# src.internals to access additional utilities and classes that are not part of the public API but can be useful for experimentation and extending the library for educational purposes.

# Geometry primitives
from .geometry import (
    Sphere, Plane, Box, Cylinder, Torus, Triangle, Square, Primitive,
)

# Math
from .math import (
    Vertex,   # 3-D point
    Vector,   # 3-D direction
)

# Scene & animation setup
from .scene import (
    Scene, Camera, Object, PinholeCamera,
    AmbientLight, PointLight, SpotLight, DirectionalLight, PointLightFalloff,
    Animator, AnimationSetup, EaseType, Easing, linear, ease_in_out,
)

# Materials, procedural textures, and noise functions
from .material import (
    Color, PhongMaterial, RockMaterial, CheckerMaterial, MarbleMaterial,
    # noise types
    PerlinNoise, SimplexNoise, FBMNoise, TurbulenceNoise, VoronoiNoise,
    # procedural textures
)

# Shaders for rendering, debugging, and educational purposes
from .shading import (
    BlinnPhongShader,
    # other shaders for debugging and education
    DepthShader, NormalShader, DiffShader, DotProductShader, MaskMethod,
)

# Rendering algorithms and utilities for rendering and post-processing
from .render import (
    LinearRenderLoop, RecursiveIntegrator, MultiProcessRowRenderLoop,
    # configs and utilities for rendering and post-processing
    RenderConfig, PreviewConfig, PostProcessConfig, ProgressDisplay
)

# Input/output utilities, including resolution handling and Jupyter notebook display functions PickleManager for saving/loading scenes, and libraries for colors, materials, and lights
from .io import (
    Resolution,
    ipynb_display_images, ipynb_display_multiple_images_in_row,
    ColorLibrary, MaterialLibrary, LightLibrary, PickleManager,
)

__all__ = [
    # Geometry primitive classes
    "Sphere", "Plane", "Box", "Torus", "Triangle", "Square", "Primitive", "Cylinder",
    # Math
    "Vertex", "Vector",
    # Scene & animation
    "Scene", "Camera", "Object", "PinholeCamera",
    "AmbientLight", "PointLight", "SpotLight", "DirectionalLight", "PointLightFalloff",
    "Animator", "AnimationSetup", "EaseType", "Easing", "linear", "ease_in_out",
    # Materials & textures
    "Color", "PhongMaterial", "RockMaterial", "CheckerMaterial", "MarbleMaterial",
    "PerlinNoise", "SimplexNoise", "FBMNoise", "TurbulenceNoise", "VoronoiNoise",
    # Shading
    "BlinnPhongShader",
    "DepthShader", "NormalShader", "DiffShader", "DotProductShader", "MaskMethod",
    # Rendering
    "LinearRenderLoop", "RecursiveIntegrator", "MultiProcessRowRenderLoop",
    "RenderConfig", "PreviewConfig", "PostProcessConfig", "ProgressDisplay",
    # IO & resolution
    "Resolution",
    "ipynb_display_images", "ipynb_display_multiple_images_in_row",
    "ColorLibrary", "MaterialLibrary", "LightLibrary", "PickleManager",
]