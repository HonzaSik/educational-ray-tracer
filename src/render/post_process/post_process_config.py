from dataclasses import dataclass

@dataclass
class PostProcessConfig:
    enabled: bool = False
    scale_factor: int = 1
