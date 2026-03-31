from abc import ABC, abstractmethod
from src.material.material import PhongMaterialSample


class ProceduralMaterial(ABC):
    @abstractmethod
    def phong_sample(self, hit: "SurfaceInteraction") -> PhongMaterialSample:
        """Get the PhongMaterialSample for a given surface interaction.
        :param hit: SurfaceInteraction containing hit details
        :return: PhongMaterialSample with material properties at the hit point
        """
        pass