import os
import pandas as pd

def export_excel(
    shots: pd.DataFrame,
    players: pd.DataFrame,
    teams: pd.DataFrame,
    bad_files: pd.DataFrame,
    out_xlsx: str,
):
    os.makedirs(os.path.dirname(out_xlsx), exist_ok=True)
    with pd.ExcelWriter(out_xlsx, engine="xlsxwriter") as writer:
        shots.to_excel(writer, sheet_name="shots_raw", index=False)
        players.to_excel(writer, sheet_name="player_all", index=False)
        teams.to_excel(writer, sheet_name="team_summary", index=False)
        bad_files.to_excel(writer, sheet_name="bad_files", index=False)
