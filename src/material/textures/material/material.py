from abc import ABC, abstractmethod

from src.material.material.material import MaterialSample
from src.scene.surface_interaction import SurfaceInteraction

class ProceduralMaterial(ABC):
    @abstractmethod
    def sample(self, hit: SurfaceInteraction) -> MaterialSample:
        ...