import os, json, glob
from typing import Any, Dict, List, Tuple
import pandas as pd
from tqdm import tqdm

def iter_json_files(root_dir: str) -> List[str]:
    files = glob.glob(os.path.join(root_dir, "**", "*.json"), recursive=True)
    files += glob.glob(os.path.join(root_dir, "**", "*.JSON"), recursive=True)
    return sorted(set(files))

def safe_get(d: Dict[str, Any], path: str, default=None):
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def to_float(x):
    try:
        return float(x)
    except Exception:
        return None

def infer_is_penalty(shot: dict) -> bool:
    if not isinstance(shot, dict):
        return False
    for key in ["isPenalty", "penalty", "fromPenalty", "is_penalty"]:
        val = shot.get(key, None)
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)) and val in (0, 1):
            return bool(val)
        if isinstance(val, str) and val.lower() in ("true", "false"):
            return val.lower() == "true"
    st = shot.get("type", None)
    return isinstance(st, str) and "pen" in st.lower()

def infer_is_goal(shot: dict) -> bool:
    if not isinstance(shot, dict):
        return False
    for key in ["isGoal", "goal"]:
        val = shot.get(key, None)
        if val is not None:
            return bool(val)
    res = shot.get("result", None)
    return isinstance(res, str) and res.lower() == "goal"

def extract_shots_from_file(filepath: str, root_for_relpath: str) -> List[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for ev in data.get("events", []):
        shot = ev.get("shot")
        if not isinstance(shot, dict):
            continue

        xg = to_float(shot.get("xg", None))
        if xg is None:
            continue

        rows.append({
            "source_file": os.path.relpath(filepath, root_for_relpath),

            "matchId": ev.get("matchId"),
            "eventId": ev.get("id"),
            "period": ev.get("matchPeriod"),
            "minute": ev.get("minute"),
            "second": ev.get("second"),
            "timestamp": ev.get("matchTimestamp"),

            "teamId": safe_get(ev, "team.id"),
            "team": safe_get(ev, "team.name"),
            "opponentId": safe_get(ev, "opponentTeam.id"),
            "opponent": safe_get(ev, "opponentTeam.name"),

            "playerId": safe_get(ev, "player.id"),
            "player": safe_get(ev, "player.name"),
            "playerPos": safe_get(ev, "player.position"),

            "x": safe_get(ev, "location.x"),
            "y": safe_get(ev, "location.y"),

            "shotType": shot.get("type", None),
            "bodyPart": shot.get("bodyPart", None),

            "isGoal": infer_is_goal(shot),
            "isPenalty": infer_is_penalty(shot),
            "xg": xg
        })
    return rows

def load_shots(root_dir: str, exclude_penalties: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    files = iter_json_files(root_dir)
    all_rows: List[dict] = []
    bad_files: List[Tuple[str, str]] = []

    for fp in tqdm(files, desc="Loading JSON"):
        try:
            all_rows.extend(extract_shots_from_file(fp, root_dir))
        except Exception as e:
            bad_files.append((fp, str(e)))

    shots = pd.DataFrame(all_rows)
    if shots.empty:
        raise RuntimeError("No shots with shot.xg found under root_dir.")

    shots["xg"] = pd.to_numeric(shots["xg"], errors="coerce")
    shots = shots.dropna(subset=["xg"]).reset_index(drop=True)
    shots["isGoal"] = shots["isGoal"].fillna(False).astype(bool)
    shots["isPenalty"] = shots["isPenalty"].fillna(False).astype(bool)

    if exclude_penalties:
        shots = shots[~shots["isPenalty"]].reset_index(drop=True)

    bad_df = pd.DataFrame(bad_files, columns=["file", "error"])
    return shots, bad_df
