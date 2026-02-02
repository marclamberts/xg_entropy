import numpy as np
import pandas as pd

# Assumes Wyscout-like 0..100 coordinates, goal at (100, 50)
def approx_distance_to_goal(x, y):
    if x is None or y is None:
        return np.nan
    return float(np.sqrt((100 - x)**2 + (50 - y)**2))

def inside_box(x, y):
    if x is None or y is None:
        return False
    # Rough penalty area proxy (tune if needed)
    return (x >= 83) and (21 <= y <= 79)

def central_box(x, y):
    if x is None or y is None:
        return False
    return (x >= 83) and (35 <= y <= 65)

def add_location_features(shots: pd.DataFrame) -> pd.DataFrame:
    df = shots.copy()
    df["dist_to_goal"] = df.apply(lambda r: approx_distance_to_goal(r.get("x"), r.get("y")), axis=1)
    df["inside_box"] = df.apply(lambda r: inside_box(r.get("x"), r.get("y")), axis=1)
    df["central_box"] = df.apply(lambda r: central_box(r.get("x"), r.get("y")), axis=1)
    return df
