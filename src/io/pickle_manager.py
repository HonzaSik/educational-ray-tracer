from pathlib import Path
from pickle import dump, load
from pprint import pprint
from typing import Any
from dataclasses import dataclass, field

# type imports
from src.light.light import Light
from src.material.material import Material
from src.io.object_libraries import ColorLibrary, LightLibrary, MaterialLibrary

class PickleManager:
    """
    Manages saving and loading objects using pickle in a specified directory. Supports optional verbose mode (prints actions) and object validation. Can save/load lists or libraries (dicts) of Lights, Materials, and Colors.
    """

    def __init__(self, directory: str | Path = "./", verbose: bool = False):
        self.directory: Path = Path(directory)
        self.verbose: bool = verbose
        self.__post_init__()

    def __post_init__(self):
        self.directory.mkdir(parents=True, exist_ok=True)

    def set_verbose(self, verbose: bool) -> None:
        self.verbose = verbose

    def save(self, data: Any, filename: str | Path) -> Path:
        path = self.directory / Path(str(filename))
        with open(path, "wb") as f:
            dump(data, f)
        if self.verbose:
            print(f"Saved object to {path}")
            pprint(data)
        return path

    def load(self, filename: str | Path) -> Any:
        path = self.directory / Path(str(filename))
        with open(path, "rb") as f:
            obj = load(f)
        if self.verbose:
            print(f"Loaded object from {path}")
            pprint(obj)
        return obj

    def save_color_library(self, color_lib: ColorLibrary) -> None:
        self.save(color_lib.colors, "colors.pkl")

    def load_color_library(self) -> ColorLibrary:
        colors = self.load("colors.pkl")
        return ColorLibrary(colors)

    def save_light_library(self, light_lib: LightLibrary) -> None:
        self.save(light_lib.lights, "lights.pkl")

    def load_light_library(self) -> LightLibrary:
        lights = self.load("lights.pkl")
        return LightLibrary(lights)

    def save_material_library(self, material_lib: MaterialLibrary) -> None:
        self.save(material_lib.materials, "materials.pkl")

    def load_material_library(self) -> MaterialLibrary:
        materials = self.load("materials.pkl")
        return MaterialLibrary(materials)