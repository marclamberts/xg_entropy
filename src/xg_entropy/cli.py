import argparse
import numpy as np

from .config import EntropyConfig, FoxInBoxConfig
from .io import load_shots
from .pipeline import compute_player_table, add_fox_in_box_flag, team_summary
from .export import export_excel
from .plotting import ft_table_png, bar_xg_adj, stacked_core_flexible

def main():
    p = argparse.ArgumentParser(prog="xg-entropy")
    p.add_argument("--root", required=True, help="Root folder containing Wyscout JSON files")
    p.add_argument("--out-xlsx", required=True, help="Output Excel path")
    p.add_argument("--out-dir", default=None, help="Optional directory for PNG charts")
    p.add_argument("--min-shots", type=int, default=250, help="Min shots for ranked table/plots")
    p.add_argument("--no-exclude-pens", action="store_true", help="Do not exclude penalties")

    # Entropy grid
    p.add_argument("--grid-x", type=int, default=6)
    p.add_argument("--grid-y", type=int, default=4)

    args = p.parse_args()

    cfg = EntropyConfig(
        grid_x=args.grid_x,
        grid_y=args.grid_y,
        exclude_penalties=not args.no_exclude_pens,
    )
    fox = FoxInBoxConfig()

    shots, bad = load_shots(args.root, exclude_penalties=cfg.exclude_penalties)
    players = compute_player_table(shots, cfg)
    players = add_fox_in_box_flag(players, fox)

    # ranks + filtered view
    players = players.sort_values(["xg_adj", "xg"], ascending=[False, False]).reset_index(drop=True)
    players.insert(0, "Rank", np.arange(1, len(players) + 1))
    players_min = players[players["shots"] >= args.min_shots].copy()

    teams = team_summary(shots)

    export_excel(shots, players, teams, bad, args.out_xlsx)

    if args.out_dir:
        # plots use the >=min-shots view by default
        ft_table_png(
            players_min[["Rank","player","teams","shots","xg","xg_adj","xg_adj_pct","stability","goals","g_minus_xg","fox_in_box_flag"]],
            out_png=f"{args.out_dir.rstrip('/')}/ft_table_{args.min_shots}plus.png",
            top_n=25,
            title=f"Entropy-adjusted xG (unscaled) — shots ≥ {args.min_shots}"
        )
        bar_xg_adj(players_min, f"{args.out_dir.rstrip('/')}/bar_xg_adj_{args.min_shots}plus.png", top_n=20)
        stacked_core_flexible(players_min, f"{args.out_dir.rstrip('/')}/stacked_core_flexible_{args.min_shots}plus.png", top_n=15)
