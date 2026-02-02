from dataclasses import dataclass

@dataclass(frozen=True)
class EntropyConfig:
    grid_x: int = 6
    grid_y: int = 4
    exclude_penalties: bool = True

    # UNSCALED stability weights (must sum <= 1.0 for clean interpretation)
    w_shot_entropy: float = 0.40
    w_spatial_entropy: float = 0.30
    w_type_entropy: float = 0.15
    w_box_share: float = 0.15

@dataclass(frozen=True)
class FoxInBoxConfig:
    max_spatial_entropy: float = 0.35
    min_box_share: float = 0.80
    min_xg_per_shot: float = 0.13
    min_shots: int = 50
