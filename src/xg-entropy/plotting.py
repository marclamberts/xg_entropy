import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def ft_table_png(df: pd.DataFrame, out_png: str, top_n: int = 25, title: str = "Entropy-adjusted xG (unscaled)"):
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    d = df.head(top_n).copy()

    # Format for display
    disp = d.copy()
    int_cols = [c for c in ["Rank", "shots", "goals"] if c in disp.columns]
    for c in int_cols:
        disp[c] = disp[c].map(lambda x: f"{int(x):,}")

    for c in ["xg", "xg_adj", "xg_adj_pct", "stability", "g_minus_xg"]:
        if c in disp.columns:
            disp[c] = disp[c].map(lambda x: "" if pd.isna(x) else f"{x:,.2f}")

    if "fox_in_box_flag" in disp.columns:
        disp["fox_in_box_flag"] = disp["fox_in_box_flag"].map(lambda x: "FOX" if x else "")

    plt.rcParams["font.family"] = "serif"
    fig_h = 0.35 * (len(d) + 2)
    fig, ax = plt.subplots(figsize=(16, fig_h))
    ax.axis("off")

    tbl = ax.table(
        cellText=disp.values,
        colLabels=disp.columns,
        loc="center",
        cellLoc="right",
        colLoc="left",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.4)

    text_cols = [c for c in ["player", "teams", "fox_in_box_flag"] if c in disp.columns]
    text_idx = [list(disp.columns).index(c) for c in text_cols]

    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_text_props(weight="bold")
            cell.set_linewidth(1.5)
            cell.visible_edges = "B"
        else:
            cell.set_linewidth(0.5)
            cell.visible_edges = "B"
        if c in text_idx:
            cell._loc = "left"
            cell.set_text_props(ha="left")
        else:
            cell.set_text_props(ha="right")

    ax.set_title(title, fontsize=14, pad=18)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close(fig)

def bar_xg_adj(df: pd.DataFrame, out_png: str, top_n: int = 20, title: str = "Top xG adjusted (unscaled)"):
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    d = df.head(top_n).copy()

    fig, ax = plt.subplots(figsize=(10, 0.45 * len(d) + 2))
    ax.barh(d["player"][::-1], d["xg_adj"][::-1])
    ax.set_xlabel("xG adjusted")
    ax.set_title(title)
    ax.grid(axis="x", linestyle="--", linewidth=0.5, alpha=0.5)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close(fig)

def stacked_core_flexible(df: pd.DataFrame, out_png: str, top_n: int = 15, title: str = "Trusted vs Flexible xG"):
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    d = df.head(top_n).copy()
    core = d["xg_adj"]
    flex = d["xg"] - d["xg_adj"]

    fig, ax = plt.subplots(figsize=(10, 0.45 * len(d) + 2))
    ax.barh(d["player"][::-1], core[::-1], label="Trusted/Core xG")
    ax.barh(d["player"][::-1], flex[::-1], left=core[::-1], label="Flexible/Context xG")
    ax.set_xlabel("xG")
    ax.set_title(title)
    ax.legend(loc="lower right")
    ax.grid(axis="x", linestyle="--", linewidth=0.5, alpha=0.5)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close(fig)
