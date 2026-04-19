from dataclasses import dataclass
import math
from src.material.material.phong_material import PhongMaterial, PhongMaterialSample


@dataclass
class CheckerMaterial(PhongMaterial):
    """
    Checkerboard pattern material. Alternates between the base color and a darker version of it based on the position of the hit point.
    """
    scale: float = 1.0

    def phong_sample(self, hit):
        s = hit.point.x * self.scale
        t = hit.point.z * self.scale

        if (math.floor(s) + math.floor(t)) % 2 == 0:
            col = self.base_color
        else:
            col = self.base_color * 0.2

        return PhongMaterialSample(
            base_color=col,
            spec_color=self.spec_color,
            shininess=self.shininess,
            reflectivity=self.reflectivity,
            ior=self.ior,
            transparency=self.transparency,
        )
