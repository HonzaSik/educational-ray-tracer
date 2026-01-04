#geometry package
from .geometry import Plane, Sphere, Triangle, Square
# helpers and math
from .math import Vertex, Vector
# io package
from .io import ColorLibrary, LightLibrary, MaterialLibrary, PickleManager, Resolution, ipynb_display_images
# material
from .material import Material, Color
# scene setting
from .scene import Scene, Camera, AmbientLight, PointLight, RenderMethod, ShadingModel, QualityPreset

from .shading import  BlinnPhongShader, DepthShader, NormalShader, DiffShader, CurvatureShader

__all__ = [
    "Plane", "Sphere", "Square", "Triangle",
    "Vertex", "Vector",
    "ColorLibrary", "LightLibrary", "MaterialLibrary", "PickleManager", "ipynb_display_images",
    "Material", "Color",
    "Scene", "Camera", "AmbientLight", "PointLight", "Resolution", "RenderMethod", "ShadingModel", "QualityPreset",
    "BlinnPhongShader", "DepthShader", "NormalShader", "DiffShader", "CurvatureShader"
]