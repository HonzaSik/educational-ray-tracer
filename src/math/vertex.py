from .vec3 import Vec3


class Vertex(Vec3):
    """
    Vertex inheriting from Vec3, with vertex-specific methods.
    """

    # aliases for vector components
    @property
    def i(self) -> float:
        return self.x

    @property
    def j(self) -> float:
        return self.y

    @property
    def k(self) -> float:
        return self.z

    @i.setter
    def i(self, value: float) -> None:
        self.x = value

    @j.setter
    def j(self, value: float) -> None:
        self.y = value

    @k.setter
    def k(self, value: float) -> None:
        self.z = value
