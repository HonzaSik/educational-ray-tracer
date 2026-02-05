from dataclasses import dataclass
import math
from src.material.material.material import MaterialSample
from src.material.material.phong_material import PhongMaterial

@dataclass
class CheckerMaterial(PhongMaterial):
    scale: float = 1.0

    def sample(self, hit):
        s = hit.point.x * self.scale
        t = hit.point.z * self.scale

        if (math.floor(s) + math.floor(t)) % 2 == 0:
            col = self.base_color
        else:
            col = self.base_color * 0.2

        return MaterialSample(
            base_color=col,
            spec_color=self.spec_color,
            shininess=self.shininess,
            reflectivity=self.reflectivity,
            ior=self.ior,
            opacity=1.0
        )
