from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_revised_figures as base  # noqa: E402

OUT = ROOT / "10_figures_nature_style"
DIAG = ROOT / "07_meta_analysis" / "publication_bias_diagnostics.csv"

COL = {
    "blue": "#2E6F9E",
    "orange": "#C9792B",
    "blue_light": "#D8E7F1",
    "orange_light": "#F2E0C8",
    "grid": "#E5E9F0",
    "dark": "#1F2937",
    "panel": "#FBFCFE",
    "band99": "#F5F7FA",
    "band95": "#DDE7F0",
    "line99": "#B8C1CC",
    "line95": "#64748B",
}


def configure() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 170,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "font.family": "DejaVu Sans",
            "font.size": 7.2,
            "axes.titlesize": 8.0,
            "axes.titleweight": "normal",
            "axes.labelsize": 7.0,
            "xtick.labelsize": 6.4,
            "ytick.labelsize": 6.4,
            "axes.linewidth": 0.55,
            "axes.edgecolor": "#303846",
            "xtick.major.width": 0.45,
            "ytick.major.width": 0.45,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def numeric(series: pd.Series) -> pd.Series:
    return series.map(base.num)


def stratum_data(extraction: pd.DataFrame, dataset: str, bucket: str) -> pd.DataFrame:
    d = extraction[
        base.dataset_mask(extraction["dataset_name"], dataset)
        & extraction["include_meta"].str.lower().eq("yes")
        & extraction["protocol_bucket"].eq(bucket)
        & extraction["metric"].str.contains("acc|accuracy", case=False, regex=True, na=False)
    ].copy()
    d["effect"] = numeric(d["result_mean"])
    d["sd"] = numeric(d["result_sd"])
    d["n"] = numeric(d["n_subjects"])
    d = d[d["effect"].notna() & d["sd"].notna() & d["n"].notna() & d["n"].gt(1)]
    d["se"] = d["sd"] / np.sqrt(d["n"])
    d["precision"] = 1.0 / d["se"]
    d = d[d["se"].gt(0) & np.isfinite(d["precision"])]
    return d


def egger_test(d: pd.DataFrame) -> dict[str, float]:
    # Egger regression: standard-normal deviate on study precision.
    x = d["precision"].to_numpy(dtype=float)
    y = (d["effect"] / d["se"]).to_numpy(dtype=float)
    n = len(d)
    X = np.column_stack([np.ones(n), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    df = n - 2
    sigma2 = float((resid @ resid) / df)
    cov = sigma2 * np.linalg.inv(X.T @ X)
    intercept = float(beta[0])
    intercept_se = float(np.sqrt(cov[0, 0]))
    t_stat = intercept / intercept_se if intercept_se > 0 else np.nan
    p_value = float(2 * stats.t.sf(abs(t_stat), df)) if df > 0 else np.nan
    return {
        "egger_intercept": intercept,
        "egger_intercept_se": intercept_se,
        "egger_t": float(t_stat),
        "egger_df": df,
        "egger_p": p_value,
    }


def savefig(fig: plt.Figure, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def main() -> None:
    configure()
    extraction, _, meta, _ = base.load_data()

    panels = [
        ("SEED", "Inductive / no target", "(A) SEED inductive", COL["blue"]),
        ("SEED", "Transductive / UDA", "(B) SEED transductive", COL["orange"]),
        ("SEED-IV", "Inductive / no target", "(C) SEED-IV inductive", COL["blue"]),
        ("SEED-IV", "Transductive / UDA", "(D) SEED-IV transductive", COL["orange"]),
    ]

    rows = []
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2), sharex=False, sharey=False)
    for ax, (dataset, bucket, title, color) in zip(axes.ravel(), panels):
        d = stratum_data(extraction, dataset, bucket)
        task = "SEED | 3-class" if dataset == "SEED" else "SEED-IV | 4-class"
        stratum = "inductive/no-target" if bucket.startswith("Inductive") else "transductive-UDA"
        pooled_row = meta[(meta["task"].eq(task)) & (meta["stratum"].eq(stratum))]
        pooled = float(pooled_row.iloc[0]["DL_mean"]) if not pooled_row.empty else float(d["effect"].mean())

        if len(d) >= 10:
            e = egger_test(d)
        else:
            e = {"egger_intercept": np.nan, "egger_intercept_se": np.nan, "egger_t": np.nan, "egger_df": np.nan, "egger_p": np.nan}

        rows.append(
            {
                "dataset": dataset,
                "stratum": stratum,
                "k": len(d),
                "pooled_mean": round(pooled, 2),
                "mean_se": round(float(d["se"].mean()), 3),
                "egger_intercept": round(e["egger_intercept"], 3) if np.isfinite(e["egger_intercept"]) else "",
                "egger_intercept_se": round(e["egger_intercept_se"], 3) if np.isfinite(e["egger_intercept_se"]) else "",
                "egger_t": round(e["egger_t"], 3) if np.isfinite(e["egger_t"]) else "",
                "egger_df": int(e["egger_df"]) if np.isfinite(e["egger_df"]) else "",
                "egger_p": round(e["egger_p"], 4) if np.isfinite(e["egger_p"]) else "",
                "interpretation": "exploratory asymmetry diagnostic; not publication-bias proof",
            }
        )

        ax.set_facecolor(COL["panel"])
        se_max = float(d["se"].max())
        x_min = min(float(d["effect"].min()), pooled - 2.58 * se_max)
        x_max = max(float(d["effect"].max()), pooled + 2.58 * se_max)
        x_pad = max(2.0, float(x_max - x_min) * 0.06)
        ax.set_xlim(max(0.0, float(x_min - x_pad)), min(100.0, float(x_max + x_pad)))
        ax.set_ylim(se_max * 1.08, 0)

        se_grid = np.linspace(0, se_max, 220)
        lower99, upper99 = pooled - 2.58 * se_grid, pooled + 2.58 * se_grid
        lower95, upper95 = pooled - 1.96 * se_grid, pooled + 1.96 * se_grid
        ax.fill_betweenx(se_grid, lower99, upper99, color=COL["band99"], alpha=0.95, zorder=0)
        ax.fill_betweenx(se_grid, lower95, upper95, color=COL["band95"], alpha=0.95, zorder=1)
        for mult, color_limit, lw, ls in [
            (2.58, COL["line99"], 0.55, (0, (3.2, 2.2))),
            (1.96, COL["line95"], 0.75, "-"),
        ]:
            ax.plot(pooled - mult * se_grid, se_grid, color=color_limit, lw=lw, ls=ls, zorder=2)
            ax.plot(pooled + mult * se_grid, se_grid, color=color_limit, lw=lw, ls=ls, zorder=2)

        ax.axvline(pooled, color=COL["dark"], lw=1.05, zorder=3)
        ax.scatter(
            d["effect"],
            d["se"],
            s=24,
            color=color,
            alpha=0.78,
            edgecolor="white",
            linewidth=0.45,
            zorder=4,
        )
        p_text = "p=n/a" if not np.isfinite(e["egger_p"]) else ("p<.001" if e["egger_p"] < 0.001 else f"p={e['egger_p']:.3f}")
        ax.text(
            0.025,
            0.955,
            f"k={len(d)}; Egger {p_text}",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=6.35,
            color=COL["dark"],
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "#D7DCE5", "linewidth": 0.35, "alpha": 0.92},
            zorder=5,
        )
        ax.set_title(title, loc="left", pad=4)
        ax.set_xlabel("reported accuracy (%)")
        ax.set_ylabel("standard error (pp)")
        ax.grid(axis="y", color=COL["grid"], lw=0.45)
        ax.grid(axis="x", color=COL["grid"], lw=0.35, alpha=0.75)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color("#303846")

    handles = [
        Line2D([0], [0], color=COL["line95"], lw=0.85, label="95% pseudo-limit"),
        Line2D([0], [0], color=COL["line99"], lw=0.65, ls=(0, (3.2, 2.2)), label="99% pseudo-limit"),
        Line2D([0], [0], color=COL["dark"], lw=1.05, label="pooled estimate"),
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.995),
        ncol=3,
        frameon=False,
        fontsize=6.4,
        handlelength=2.6,
        columnspacing=1.2,
    )
    fig.subplots_adjust(left=0.08, right=0.98, top=0.925, bottom=0.09, hspace=0.42, wspace=0.30)
    savefig(fig, "fig12_funnel_plots")
    pd.DataFrame(rows).to_csv(DIAG, index=False)
    print(f"wrote {DIAG}")
    print(f"wrote {OUT / 'fig12_funnel_plots.png'}")


if __name__ == "__main__":
    main()
