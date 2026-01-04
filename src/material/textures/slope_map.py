# src/material/textures/slope_map.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List
from src.math import Vector


@dataclass
class SlopeMapPoint:
    position: float
    slope: Vector


@dataclass
class SlopeMap:
    points: List[SlopeMapPoint]

    def __post_init__(self) -> None:
        if not self.points:
            return

        for p in self.points:
            if p.position < 0.0:
                p.position = 0.0
            elif p.position > 1.0:
                p.position = 1.0

        self.points.sort(key=lambda p: p.position)

    @classmethod
    def flat(cls, slope: Vector | None = None) -> SlopeMap:
        if slope is None:
            slope = Vector(0.0, 0.0, 0.0)
        return cls(points=[SlopeMapPoint(position=0.0, slope=slope),
                           SlopeMapPoint(position=1.0, slope=slope)])

    @classmethod
    def from_pairs(cls, pairs: Iterable[tuple[float, Vector]]) -> SlopeMap:
        return cls(points=[SlopeMapPoint(pos, vec) for pos, vec in pairs])


    def sample(self, t: float) -> Vector:
        if not self.points:
            return Vector(0.0, 0.0, 0.0)

        if t <= self.points[0].position:
            return self.points[0].slope
        if t >= self.points[-1].position:
            return self.points[-1].slope

        pts = self.points
        for i in range(len(pts) - 1):
            a = pts[i]
            b = pts[i + 1]
            if a.position <= t <= b.position:
                if b.position == a.position:
                    return a.slope
                ratio = (t - a.position) / (b.position - a.position)
                return a.slope * (1.0 - ratio) + b.slope * ratio

        return self.points[-1].slope

    def sample_scalar_length(self, t: float) -> float:
        return self.sample(t).length()
