import numpy as np
import pandas as pd

from .config import EntropyConfig, FoxInBoxConfig
from .metrics import shot_entropy, spatial_entropy_grid, type_entropy
from .features import add_location_features

def compute_player_table(shots: pd.DataFrame, cfg: EntropyConfig) -> pd.DataFrame:
    # Ensure location-derived features exist
    if "inside_box" not in shots.columns:
        shots = add_location_features(shots)

    player = (
        shots.groupby(["playerId", "player"], dropna=False)
        .apply(lambda g: pd.Series({
            "shots": len(g),
            "xg": g["xg"].sum(),
            "xg_per_shot": g["xg"].mean(),
            "goals": int(g["isGoal"].sum()),
            "g_minus_xg": float(g["isGoal"].sum() - g["xg"].sum()),

            "shot_entropy": shot_entropy(g),
            "spatial_entropy": spatial_entropy_grid(g, grid_x=cfg.grid_x, grid_y=cfg.grid_y),
            "type_entropy": type_entropy(g),

            "box_shot_share": float(g["inside_box"].mean()) if len(g) else np.nan,
            "central_box_share": float(g["central_box"].mean()) if "central_box" in g.columns else np.nan,
            "avg_dist_to_goal": float(np.nanmean(g["dist_to_goal"])) if "dist_to_goal" in g.columns else np.nan,

            "teams": ", ".join(sorted(set(g["team"].dropna().astype(str).tolist()))),
        }))
        .reset_index()
    )

    # UNSCALED stability (0..1). This is your "trusted xG share"
    player["type_entropy_fill"] = player["type_entropy"].fillna(0.5)

    player["stability"] = (
        cfg.w_shot_entropy   * (1 - player["shot_entropy"]) +
        cfg.w_spatial_entropy* (1 - player["spatial_entropy"]) +
        cfg.w_type_entropy   * (1 - player["type_entropy_fill"]) +
        cfg.w_box_share      * (player["box_shot_share"].fillna(0.0))
    ).clip(0, 1)

    player["xg_adj"] = player["xg"] * player["stability"]
    player["xg_adj_pct"] = 100 * player["stability"]  # literal percent share

    return player

def add_fox_in_box_flag(players: pd.DataFrame, fox: FoxInBoxConfig) -> pd.DataFrame:
    df = players.copy()
    df["fox_in_box_flag"] = (
        (df["spatial_entropy"] <= fox.max_spatial_entropy) &
        (df["box_shot_share"] >= fox.min_box_share) &
        (df["xg_per_shot"] >= fox.min_xg_per_shot) &
        (df["shots"] >= fox.min_shots)
    )
    return df

def team_summary(shots: pd.DataFrame) -> pd.DataFrame:
    if "inside_box" not in shots.columns:
        shots = add_location_features(shots)

    return (
        shots.groupby(["teamId", "team"], dropna=False)
        .agg(
            shots=("eventId", "count"),
            xg=("xg", "sum"),
            xg_per_shot=("xg", "mean"),
            goals=("isGoal", lambda s: int(pd.Series(s).sum())),
            box_share=("inside_box", "mean"),
        )
        .reset_index()
        .sort_values(["xg", "shots"], ascending=[False, False])
        .reset_index(drop=True)
    )
