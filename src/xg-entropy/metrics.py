import numpy as np
import pandas as pd

def normalized_entropy(p: np.ndarray) -> float:
    p = p[p > 0]
    k = len(p)
    if k <= 1:
        return 0.0
    return float(-(p * np.log(p)).sum() / np.log(k))

def shot_entropy(g: pd.DataFrame) -> float:
    total = g["xg"].sum()
    if total <= 0 or len(g) <= 1:
        return 0.0
    return normalized_entropy((g["xg"] / total).to_numpy())

def spatial_entropy_grid(g: pd.DataFrame, grid_x: int = 6, grid_y: int = 4) -> float:
    d = g.dropna(subset=["x", "y"]).copy()
    if len(d) <= 1:
        return 0.0
    d["bx"] = pd.cut(d["x"], bins=grid_x, labels=False, include_lowest=True)
    d["by"] = pd.cut(d["y"], bins=grid_y, labels=False, include_lowest=True)
    xg_by_bin = d.groupby(["bx", "by"])["xg"].sum()
    total = xg_by_bin.sum()
    if total <= 0 or len(xg_by_bin) <= 1:
        return 0.0
    return normalized_entropy((xg_by_bin / total).to_numpy())

def type_entropy(g: pd.DataFrame) -> float:
    d = g.dropna(subset=["shotType"]).copy()
    if len(d) <= 1:
        return np.nan
    xg_by_type = d.groupby("shotType")["xg"].sum()
    total = xg_by_type.sum()
    if total <= 0 or len(xg_by_type) <= 1:
        return 0.0
    return normalized_entropy((xg_by_type / total).to_numpy())
