from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.colors import LinearSegmentedColormap

import generate_revised_figures as base
import generate_prisma_flow


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "10_figures_nature_style"
SUMMARY = ROOT / "07_meta_analysis" / "statistics_summary_20260704.json"

COL = {
    "blue": "#3B6E8F",
    "orange": "#D1903F",
    "green": "#5D8B61",
    "purple": "#7A6DA8",
    "red": "#B55A5C",
    "gray": "#6B7280",
    "dark": "#111827",
    "grid": "#D9DEE7",
    "pale": "#F5F7FA",
}

PROTO = OrderedDict(
    [
        ("Inductive / no target", COL["blue"]),
        ("Transductive / UDA", COL["orange"]),
        ("Few-shot / labels", COL["green"]),
        ("Cross-dataset", COL["purple"]),
        ("Ambiguous / suspect", COL["red"]),
        ("Leakage / invalid", COL["red"]),
        ("Other / unclear", COL["gray"]),
    ]
)


def configure() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 170,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "font.family": "DejaVu Sans",
            "font.size": 7.5,
            "axes.titlesize": 8.2,
            "axes.titleweight": "normal",
            "axes.labelsize": 7.5,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "legend.fontsize": 6.8,
            "axes.linewidth": 0.55,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def savefig(fig: plt.Figure, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.025)
    plt.close(fig)


def clean_axes(ax: plt.Axes, grid_axis: str | None = None) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, color=COL["grid"], lw=0.45, zorder=0)
        ax.set_axisbelow(True)


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(-0.08, 1.04, label, transform=ax.transAxes, ha="left", va="top", weight="bold", fontsize=9.0)


def pooled_meta(meta: pd.DataFrame) -> pd.DataFrame:
    d = meta[pd.to_numeric(meta["DL_mean"], errors="coerce").notna()].copy()
    for col in ["DL_mean", "DL_ci_lo", "DL_ci_hi", "k", "I2"]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    return d


def load_counts() -> dict[str, int]:
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    return {
        "raw_database_records": int(data["raw_database_records"]),
        "duplicates_removed": int(data["duplicates_removed"]),
        "unique_records_screened": int(data["unique_records_screened"]),
        "screening_excluded": int(data["screening_excluded_after_adjudication"]),
        "reports_assessed": int(data["reports_assessed_or_sought_after_adjudication"]),
        "reports_excluded": int(data["reports_excluded_unobtainable_or_queued_after_fulltext"]),
        "qualitative_included": int(data["qualitative_included_studies"]),
        "meta_eligible": int(data["meta_eligible_studies"]),
    }


def fig1_prisma(extraction: pd.DataFrame) -> None:
    counts = load_counts()
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    stages = [
        ("Identified", counts["raw_database_records"], "database records"),
        ("Unique", counts["unique_records_screened"], "after deduplication"),
        ("Screened in", counts["reports_assessed"], "reports assessed"),
        ("Included", counts["qualitative_included"], "full-text verified"),
        ("Pooled", counts["meta_eligible"], "meta-eligible studies"),
    ]
    xs = np.linspace(0.08, 0.92, len(stages))
    y = 0.62
    for i, (name, n, sub) in enumerate(stages):
        ax.scatter(xs[i], y, s=1450, color="white", edgecolor=COL["blue"], lw=1.4, zorder=3)
        ax.text(xs[i], y + 0.018, f"{n:,}", ha="center", va="center", color=COL["dark"], weight="bold", fontsize=11.0)
        ax.text(xs[i], 0.38, name, ha="center", va="center", color=COL["blue"], weight="bold", fontsize=7.4)
        ax.text(xs[i], 0.30, sub, ha="center", va="top", color=COL["gray"], fontsize=6.7)
        if i < len(stages) - 1:
            ax.annotate("", xy=(xs[i + 1] - 0.055, y), xytext=(xs[i] + 0.055, y),
                        arrowprops=dict(arrowstyle="-|>", color="#8B95A3", lw=1.0))

    drop = [
        (0.29, f"{counts['duplicates_removed']:,} duplicates\nremoved"),
        (0.50, f"{counts['screening_excluded']:,} excluded or\nout of scope"),
        (0.71, f"{counts['reports_excluded']:,} excluded,\npaywalled, queued"),
        (0.86, f"{counts['qualitative_included'] - counts['meta_eligible']:,} narrative-only\nor nonpoolable"),
    ]
    for x, text in drop:
        ax.text(x, 0.18, text, ha="center", va="center", fontsize=6.5, color=COL["gray"])

    ax.text(0.02, 0.94, "PRISMA-style verified evidence flow", ha="left", va="top", fontsize=8.2, color=COL["dark"])
    ax.text(
        0.02,
        0.08,
        "Full-text verification is the unit of credibility; nonpoolable rows are retained narratively rather than guessed.",
        ha="left",
        va="bottom",
        fontsize=7.0,
        color=COL["dark"],
    )
    savefig(fig, "fig1_prisma_flow")


def fig2_taxonomy() -> None:
    fig, ax = plt.subplots(figsize=(3.45, 1.92))
    fig.subplots_adjust(left=0.025, right=0.99, top=0.985, bottom=0.025)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    labels = [
        ("1", "No target data", "Inductive LOSO; domain generalization;\nsource-only transfer", COL["blue"]),
        ("2", "Unlabeled target", "Transductive UDA; source-free DA;\ntest-time adaptation", COL["orange"]),
        ("3", "Labeled target", "Few-shot calibration; semi-supervised labels;\npersonalization", COL["green"]),
        ("4", "Invalid / ambiguous", "Subject-mixed CV; trial/window leakage;\nunreported target access", COL["red"]),
    ]
    top = 0.935
    row_h = 0.198
    x0, x1 = 0.02, 0.98
    ax.plot([x0, x1], [top + 0.040, top + 0.040], color=COL["dark"], lw=0.55)
    ax.text(0.075, top + 0.011, "Rung", ha="center", va="center", fontsize=5.2, color=COL["dark"], weight="bold")
    ax.text(0.17, top + 0.011, "Target access and examples", ha="left", va="center", fontsize=5.2, color=COL["dark"], weight="bold")
    ax.plot([x0, x1], [top - 0.010, top - 0.010], color="#9AA3AF", lw=0.42)

    for i, (num, access, examples, color) in enumerate(labels):
        y = top - 0.108 - i * row_h
        if i == 3:
            ax.add_patch(patches.Rectangle((x0, y - 0.085), x1 - x0, 0.150, facecolor="#F8E8E8", edgecolor="none", zorder=0))
        ax.plot([x0, x1], [y - 0.094, y - 0.094], color="#D5DAE2", lw=0.35, zorder=1)
        ax.scatter(0.075, y + 0.005, s=54, color=color, edgecolor="white", lw=0.6, zorder=3)
        ax.text(0.075, y + 0.005, num, ha="center", va="center", color="white", weight="bold", fontsize=5.1)
        ax.text(0.15, y + 0.048, access, ha="left", va="top", color=color, weight="semibold", fontsize=5.55)
        ax.text(0.15, y - 0.004, examples, ha="left", va="top", color=COL["dark"], fontsize=5.10, linespacing=1.02)

    savefig(fig, "fig2_protocol_taxonomy")


def fig3_risk(extraction: pd.DataFrame) -> None:
    d = extraction[
        extraction["metric"].str.contains("acc|accuracy|f1", case=False, regex=True, na=False)
        & extraction["mean_pct"].between(0, 105, inclusive="both")
    ].copy()
    d = d[d["primary_result"].str.lower().ne("no")]
    order = ["Low / low-some", "Some concerns", "High / unclear"]
    colors = [COL["blue"], COL["orange"], COL["red"]]
    data = [d[d["risk_bucket"].eq(name)]["mean_pct"].dropna().to_numpy() for name in order]
    positions = np.arange(len(order))

    fig, ax = plt.subplots(figsize=(3.45, 3.12))

    ax.axvspan(90, 103, color="#F8E8E8", zorder=0)
    violins = ax.violinplot(data, positions=positions, vert=False, widths=0.62, showextrema=False)
    for body, color in zip(violins["bodies"], colors):
        body.set_facecolor(color)
        body.set_edgecolor("none")
        body.set_alpha(0.18)

    rng = np.random.default_rng(12)
    for yi, vals, color, label in zip(positions, data, colors, order):
        jitter = yi + rng.normal(0, 0.055, len(vals))
        marker = "x" if "High" in label else "o"
        scatter_kw = dict(s=15, color=color, alpha=0.42, marker=marker, zorder=2)
        if marker != "x":
            scatter_kw["edgecolor"] = "none"
        ax.scatter(vals, jitter, **scatter_kw)
        q1, med, q3 = np.percentile(vals, [25, 50, 75])
        lo, hi = np.percentile(vals, [5, 95])
        ax.plot([lo, hi], [yi, yi], color=color, lw=1.0, zorder=3)
        ax.plot([q1, q3], [yi, yi], color=color, lw=5.0, solid_capstyle="round", zorder=4)
        ax.scatter(med, yi, s=42, color="white", edgecolor=color, lw=1.1, zorder=5)
        near = int(np.sum(vals >= 90))
        share = 100 * near / len(vals) if len(vals) else 0
        ax.text(106.0, yi, f"n={len(vals)}\nmed {med:.1f}\n>=90 {share:.0f}%", ha="right", va="center", fontsize=5.05, color=COL["dark"])

    ax.set_yticks(positions)
    ax.set_yticklabels(order, fontsize=5.45)
    ax.tick_params(axis="x", labelsize=5.35, pad=2)
    ax.set_xlabel("reported classification performance (%)", labelpad=3, fontsize=5.65)
    ax.set_xlim(35, 107)
    ax.set_ylim(-0.55, len(order) - 0.45)
    ax.text(90.8, len(order) - 0.50, "near-ceiling\nzone", color=COL["red"], fontsize=5.15, va="top")
    ax.set_title("Accuracy vs. evaluation risk", loc="left", pad=6, fontsize=6.1)
    clean_axes(ax, "x")
    fig.subplots_adjust(left=0.29, right=0.98, top=0.88, bottom=0.18)
    savefig(fig, "fig3_accuracy_vs_risk")


def fig4_coverage(extraction: pd.DataFrame) -> None:
    rows = []
    for dataset in base.DATASETS:
        m = base.dataset_mask(extraction["dataset_name"], dataset)
        rows.append(
            (
                dataset,
                extraction[m & extraction["include_narrative"].str.lower().eq("yes")]["paper_id"].nunique(),
                extraction[m & extraction["include_meta"].str.lower().eq("yes")]["paper_id"].nunique(),
            )
        )
    totals = pd.DataFrame(rows, columns=["dataset", "included", "meta"])
    totals = totals[totals["included"].gt(0)].sort_values("included", ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(7.2, 4.15))
    y = np.arange(len(totals))
    max_count = float(totals["included"].max())
    label_offset = max_count * 0.018

    ax.barh(y + 0.16, totals["included"], color="#DCE3EA", height=0.30, label="included studies")
    ax.barh(y - 0.16, totals["meta"], color=COL["blue"], height=0.30, label="meta-eligible studies")

    for yi, inc, met in zip(y, totals["included"], totals["meta"]):
        ax.text(inc + label_offset, yi + 0.16, f"{int(inc)}", va="center", ha="left", fontsize=6.5, color=COL["dark"])
        if met > 0:
            ax.text(met + label_offset, yi - 0.16, f"{int(met)}", va="center", ha="left", fontsize=6.3, color=COL["blue"])

    seed_family = totals[totals["dataset"].isin(["SEED", "SEED-IV"])][["included", "meta"]].sum()
    ax.text(
        0.98,
        0.08,
        f"SEED + SEED-IV: {int(seed_family['included'])} included, {int(seed_family['meta'])} meta-eligible",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.0,
        color=COL["dark"],
    )

    ax.set_yticks(y)
    ax.set_yticklabels(totals["dataset"])
    ax.set_xlabel("unique studies with dataset-specific results")
    ax.set_xlim(0, max_count * 1.18)
    ax.set_title("Dataset coverage is dominated by SEED-family benchmarks", loc="left", pad=8)
    ax.grid(axis="x", color=COL["grid"], lw=0.45)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower right", bbox_to_anchor=(1.0, 0.14), fontsize=6.8)
    clean_axes(ax, None)
    fig.subplots_adjust(left=0.17, right=0.98, top=0.88, bottom=0.14)
    savefig(fig, "fig4_dataset_coverage")


def fig5_timeline(extraction: pd.DataFrame, meta: pd.DataFrame) -> None:
    d = extraction[
        base.dataset_mask(extraction["dataset_name"], "SEED")
        & extraction["metric"].str.contains("acc|accuracy", case=False, regex=True, na=False)
        & extraction["mean_pct"].between(35, 103, inclusive="both")
    ].copy()
    d["year_num"] = pd.to_numeric(d["year"], errors="coerce")
    d = d[d["year_num"].between(2010, 2026)]
    d = d[d["primary_result"].str.lower().ne("no")]

    def period(year: float) -> str:
        if year <= 2018:
            return "2010-2018"
        if year <= 2022:
            return "2019-2022"
        return "2023-2026"

    d["period"] = d["year_num"].apply(period)
    period_order = ["2010-2018", "2019-2022", "2023-2026"]
    groups = [
        ("Inductive\n(no target)", ["Inductive / no target"], COL["blue"], "inductive/no-target"),
        ("Transductive\n(UDA)", ["Transductive / UDA"], COL["orange"], "transductive-UDA"),
        ("Few-shot\n(labels)", ["Few-shot / labels"], COL["green"], "few-shot/target-label"),
        ("Ambiguous /\ninvalid", ["Ambiguous / suspect", "Leakage / invalid"], COL["red"], None),
    ]

    fig = plt.figure(figsize=(7.2, 4.0))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.65, 1.05], wspace=0.32)
    ax = fig.add_subplot(gs[0, 0])
    ax_pool = fig.add_subplot(gs[0, 1])

    for yi, (label, buckets, color, _) in enumerate(groups):
        for xi, per in enumerate(period_order):
            g = d[d["period"].eq(per) & d["protocol_bucket"].isin(buckets)]
            if g.empty:
                continue
            median = float(g["mean_pct"].median())
            n = int(len(g))
            size = 70 + 31 * np.sqrt(n)
            ax.scatter(xi, yi, s=size, color=color, alpha=0.78, edgecolor="white", lw=0.9, zorder=3)
            ax.text(xi, yi, f"{median:.0f}\n({n})", ha="center", va="center", fontsize=6.5, color=COL["dark"], zorder=4)

    ax.set_xticks(np.arange(len(period_order)))
    ax.set_xticklabels(period_order)
    ax.set_yticks(np.arange(len(groups)))
    ax.set_yticklabels([g[0] for g in groups])
    ax.set_xlim(-0.55, len(period_order) - 0.45)
    ax.set_ylim(len(groups) - 0.5, -0.5)
    ax.set_title("Reported SEED accuracy by period", loc="left", pad=8)
    ax.text(
        -0.50,
        len(groups) - 0.03,
        "Cell value: median accuracy; parentheses: result rows; bubble area scales with rows.",
        fontsize=6.1,
        color=COL["gray"],
        ha="left",
        va="top",
    )
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(period_order), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(groups), 1), minor=True)
    ax.grid(which="minor", color=COL["grid"], lw=0.45)
    ax.tick_params(axis="both", length=0)

    ax_pool.axvspan(90, 96.5, color="#F8E8E8", zorder=0)
    for yi, (label, _, color, stratum) in enumerate(groups[:3]):
        row = meta[(meta["task"].eq("SEED | 3-class")) & (meta["stratum"].eq(stratum))]
        if row.empty or pd.isna(row.iloc[0]["DL_mean"]):
            continue
        mean = float(row.iloc[0]["DL_mean"])
        lo = float(row.iloc[0]["DL_ci_lo"])
        hi = float(row.iloc[0]["DL_ci_hi"])
        k = int(float(row.iloc[0]["k"]))
        ax_pool.plot([lo, hi], [yi, yi], color=color, lw=2.0)
        ax_pool.scatter(mean, yi, s=80, color=color, edgecolor="white", lw=0.8, zorder=3)
        ax_pool.text(96.0, yi, f"{mean:.1f}\nk={k}", va="center", ha="left", fontsize=6.2, color=color)
    ax_pool.axvline(90, color=COL["red"], lw=0.7, ls=":")
    ax_pool.text(90.2, 3.15, ">=90%", color=COL["red"], fontsize=6.2, ha="left", va="center")
    ax_pool.set_yticks(np.arange(len(groups)))
    ax_pool.set_yticklabels([])
    ax_pool.set_ylim(len(groups) - 0.5, -0.5)
    ax_pool.set_xlim(82, 99)
    ax_pool.set_xlabel("accuracy (%)")
    ax_pool.set_title("Pooled SEED\n3-class estimate", loc="left", pad=8)
    clean_axes(ax_pool, "x")

    fig.suptitle("SEED evidence by target access and publication period", y=0.985, fontsize=8.2)
    fig.subplots_adjust(left=0.16, right=0.97, top=0.82, bottom=0.20)
    savefig(fig, "fig5_seed_year_protocol")


def fig6_bubble_heatmap(meta: pd.DataFrame) -> None:
    d = pooled_meta(meta)
    task_order = [
        "SEED | 3-class",
        "SEED-IV | 4-class",
        "SEED-V | 5-class",
        "DEAP | valence (binary)",
        "DEAP | arousal (binary)",
        "DREAMER | valence (binary)",
        "DREAMER | arousal (binary)",
    ]
    task_labels = [
        "SEED\n3-class",
        "SEED-IV\n4-class",
        "SEED-V\n5-class",
        "DEAP\nvalence",
        "DEAP\narousal",
        "DREAMER\nvalence",
        "DREAMER\narousal",
    ]
    strata = [
        ("inductive/no-target", "Inductive", COL["blue"], -0.20),
        ("transductive-UDA", "Transductive", COL["orange"], 0.00),
        ("few-shot/target-label", "Few-shot", COL["green"], 0.20),
    ]

    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.axvspan(90, 97, color="#F8E8E8", zorder=0)

    y = np.arange(len(task_order))
    for i, task in enumerate(task_order):
        for strat, _, color, offset in strata:
            r = d[(d["task"].eq(task)) & (d["stratum"].eq(strat))]
            if r.empty or pd.isna(r.iloc[0]["DL_mean"]):
                continue
            row = r.iloc[0]
            yi = i + offset
            mean = float(row["DL_mean"])
            lo = float(row["DL_ci_lo"])
            hi = float(row["DL_ci_hi"])
            k = int(float(row["k"]))
            ax.plot([lo, hi], [yi, yi], color=color, lw=1.7, alpha=0.86)
            ax.scatter(mean, yi, s=36 + 15 * np.sqrt(k), color=color, edgecolor="white", lw=0.8, zorder=3)
            if k >= 10:
                ax.text(min(hi + 0.65, 96.0), yi, f"k={k}", va="center", ha="left", fontsize=6.0, color=color)

    handles = [
        mpl.lines.Line2D([0], [0], marker="o", color=color, label=label, markerfacecolor=color, markeredgecolor="white", lw=1.4, markersize=5.3)
        for _, label, color, _ in strata
    ]
    ax.legend(handles=handles, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3, handletextpad=0.35, columnspacing=1.2)
    ax.set_yticks(y)
    ax.set_yticklabels(task_labels)
    ax.set_xlim(58, 97)
    ax.set_ylim(len(task_order) - 0.55, -0.55)
    ax.set_xlabel("pooled accuracy (%)")
    ax.set_title("Poolable evidence is sparse outside SEED-family tasks", loc="left", pad=8)
    ax.text(90.4, len(task_order) - 0.80, ">=90%", fontsize=6.3, color=COL["red"], va="center")
    ax.text(58.2, len(task_order) - 0.05, "No marker = narrative-only or non-poolable cell; marker area scales with k.", fontsize=6.3, color=COL["gray"], va="top")
    clean_axes(ax, "x")
    fig.subplots_adjust(left=0.16, right=0.98, top=0.86, bottom=0.25)
    savefig(fig, "fig6_evidence_heatmap")


def fig7_seed_forest(meta: pd.DataFrame) -> None:
    rowset = meta[meta["task"].eq("SEED | 3-class")].copy()
    order = ["inductive/no-target", "transductive-UDA", "few-shot/target-label"]
    names = ["Inductive\n(no target)", "Transductive\n(UDA)", "Few-shot\n(labels)"]
    colors = [COL["blue"], COL["orange"], COL["green"]]

    fig, ax = plt.subplots(figsize=(7.2, 2.35))
    rng = np.random.default_rng(4)
    for yi, (strat, name, color) in enumerate(zip(order, names, colors)):
        row = rowset[rowset["stratum"].eq(strat)]
        if row.empty:
            continue
        studies = base.parse_studies(row.iloc[0]["studies"])
        vals = [v for _, v, _ in studies]
        ax.scatter(vals, yi + rng.normal(0, 0.045, len(vals)), s=14, color="#9AA3AF", alpha=0.55, lw=0)
        mean = float(row.iloc[0]["DL_mean"])
        lo = float(row.iloc[0]["DL_ci_lo"])
        hi = float(row.iloc[0]["DL_ci_hi"])
        ax.plot([lo, hi], [yi, yi], color=color, lw=2.0)
        ax.scatter(mean, yi, s=95, color=color, edgecolor="white", lw=0.8, zorder=3)
        ax.text(96.5, yi, f"{mean:.1f}% [{lo:.1f}, {hi:.1f}], k={int(float(row.iloc[0]['k']))}", va="center", fontsize=8.1)
    ax.axvspan(90, 100, color="#F8E8E8", zorder=0)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(names, fontsize=8.2)
    ax.tick_params(axis="x", labelsize=8.0)
    ax.set_xlabel("accuracy (%)", fontsize=8.4)
    ax.set_xlim(60, 104)
    ax.set_ylim(-0.35, len(order) - 0.65)
    ax.set_title("SEED 3-class: study results and pooled estimates", pad=5, fontsize=8.8)
    clean_axes(ax, "x")
    fig.subplots_adjust(left=0.12, right=0.98, top=0.82, bottom=0.22)
    savefig(fig, "fig7a_forest_SEED_3class")


def fig7_dataset_companion(meta: pd.DataFrame, prefix: str, filename: str) -> None:
    d = pooled_meta(meta)
    d = d[d["task"].str.startswith(prefix)].copy()
    if d.empty:
        return
    d["label"] = (d["task"] + " - " + d["stratum"]).str.replace(" | ", " - ", regex=False)
    d = d.sort_values(["task", "stratum"], ascending=[False, True]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.2, max(2.5, 0.42 * len(d) + 0.9)))
    y = np.arange(len(d))
    for yi, (_, r) in enumerate(d.iterrows()):
        color = {"inductive/no-target": COL["blue"], "transductive-UDA": COL["orange"], "few-shot/target-label": COL["green"]}.get(r["stratum"], COL["gray"])
        ax.plot([r["DL_ci_lo"], r["DL_ci_hi"]], [yi, yi], color=color, lw=1.5)
        ax.scatter(r["DL_mean"], yi, s=50 + 5 * r["k"], color=color, edgecolor="white", lw=0.7)
        ax.text(95, yi, f"{r['DL_mean']:.1f}% [{r['DL_ci_lo']:.1f}, {r['DL_ci_hi']:.1f}], k={int(r['k'])}", va="center", fontsize=6.7)
    ax.set_yticks(y)
    ax.set_yticklabels(d["label"])
    ax.set_xlim(45, 112)
    ax.set_xlabel("accuracy (%)")
    ax.set_title(f"{prefix} pooled strata")
    clean_axes(ax, "x")
    savefig(fig, filename)


def fig8_ladder(meta: pd.DataFrame) -> None:
    d = pooled_meta(meta)
    tasks = [
        ("SEED 3-class", "SEED | 3-class"),
        ("SEED-IV 4-class", "SEED-IV | 4-class"),
        ("DEAP valence", "DEAP | valence (binary)"),
    ]
    strata = [
        ("inductive/no-target", "Inductive", COL["blue"], -0.18),
        ("transductive-UDA", "Transductive", COL["orange"], 0.00),
        ("few-shot/target-label", "Few-shot", COL["green"], 0.18),
    ]

    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ax.axvspan(90, 98, color="#F8E8E8", zorder=0)
    y = np.arange(len(tasks))
    for i, (label, task) in enumerate(tasks):
        no_target = d[(d["task"].eq(task)) & (d["stratum"].eq("inductive/no-target"))]
        transductive = d[(d["task"].eq(task)) & (d["stratum"].eq("transductive-UDA"))]
        if not no_target.empty and not transductive.empty:
            delta = float(transductive.iloc[0]["DL_mean"]) - float(no_target.iloc[0]["DL_mean"])
            ax.text(62.0, i + 0.33, f"UDA shift {delta:+.1f} pp", fontsize=6.4, color=COL["gray"], ha="left", va="center")
        for strat, _, color, offset in strata:
            r = d[(d["task"].eq(task)) & (d["stratum"].eq(strat))]
            if r.empty or pd.isna(r.iloc[0]["DL_mean"]):
                continue
            row = r.iloc[0]
            yi = i + offset
            mean = float(row["DL_mean"])
            lo = float(row["DL_ci_lo"])
            hi = float(row["DL_ci_hi"])
            k = int(float(row["k"]))
            ax.plot([lo, hi], [yi, yi], color=color, lw=2.0, alpha=0.88)
            ax.scatter(mean, yi, s=48 + 12 * np.sqrt(k), color=color, edgecolor="white", lw=0.8, zorder=3)
            ax.text(min(hi + 0.45, 96.4), yi, f"{mean:.1f}", fontsize=6.0, color=color, va="center", ha="left")

    handles = [
        mpl.lines.Line2D([0], [0], marker="o", color=color, label=label, markerfacecolor=color, markeredgecolor="white", lw=1.6, markersize=5.2)
        for _, label, color, _ in strata
    ]
    ax.legend(handles=handles, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=3, handletextpad=0.35, columnspacing=1.2)
    ax.axvline(90, color=COL["red"], lw=0.7, ls=":")
    ax.text(97.0, len(tasks) - 0.67, ">=90%", color=COL["red"], fontsize=6.3, ha="right", va="center")
    ax.set_yticks(y)
    ax.set_yticklabels([label for label, _ in tasks])
    ax.set_xlim(60, 98)
    ax.set_ylim(len(tasks) - 0.55, -0.55)
    ax.set_xlabel("pooled accuracy (%)")
    ax.set_title("Protocol shifts are small and non-monotone within matched tasks", loc="left", pad=8)
    clean_axes(ax, "x")
    fig.subplots_adjust(left=0.16, right=0.98, top=0.84, bottom=0.28)
    savefig(fig, "fig8_protocol_ladder")


def fig11_evidence_landscape_abcd(extraction: pd.DataFrame, meta: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.55))
    ax_a, ax_b, ax_c, ax_d = axes.ravel()

    def add_panel(ax: plt.Axes, letter: str) -> None:
        ax.text(-0.10, 1.08, letter, transform=ax.transAxes, ha="left", va="top", fontsize=10.0, weight="bold")

    # A. Dataset coverage, compressed with a long-tail aggregate.
    rows = []
    for dataset in base.DATASETS:
        m = base.dataset_mask(extraction["dataset_name"], dataset)
        rows.append(
            (
                dataset,
                extraction[m & extraction["include_narrative"].str.lower().eq("yes")]["paper_id"].nunique(),
                extraction[m & extraction["include_meta"].str.lower().eq("yes")]["paper_id"].nunique(),
            )
        )
    cov = pd.DataFrame(rows, columns=["dataset", "included", "meta"])
    cov = cov[cov["included"].gt(0)].sort_values("included", ascending=False).reset_index(drop=True)
    head = cov.head(6).copy()
    tail = cov.iloc[6:]
    if not tail.empty:
        head = pd.concat(
            [
                head,
                pd.DataFrame([{"dataset": "Long tail", "included": int(tail["included"].sum()), "meta": int(tail["meta"].sum())}]),
            ],
            ignore_index=True,
        )
    cov_panel = head.sort_values("included", ascending=True).reset_index(drop=True)
    y = np.arange(len(cov_panel))
    ax_a.barh(y + 0.14, cov_panel["included"], color="#DCE3EA", height=0.28, label="included")
    ax_a.barh(y - 0.14, cov_panel["meta"], color=COL["blue"], height=0.28, label="meta-eligible")
    for yi, inc, met in zip(y, cov_panel["included"], cov_panel["meta"]):
        ax_a.text(inc + 4, yi + 0.14, f"{int(inc)}", fontsize=5.7, va="center", color=COL["dark"])
        if met:
            ax_a.text(met + 4, yi - 0.14, f"{int(met)}", fontsize=5.5, va="center", color=COL["blue"])
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(cov_panel["dataset"], fontsize=6.2)
    ax_a.set_xlim(0, max(cov_panel["included"]) * 1.22)
    ax_a.set_title("Dataset coverage", loc="left", fontsize=8.2, pad=5)
    ax_a.set_xlabel("studies", fontsize=6.4)
    ax_a.legend(frameon=False, loc="lower right", fontsize=5.8, handlelength=1.1, handletextpad=0.35)
    clean_axes(ax_a, "x")
    add_panel(ax_a, "A")

    # B. SEED period summary.
    seed = extraction[
        base.dataset_mask(extraction["dataset_name"], "SEED")
        & extraction["metric"].str.contains("acc|accuracy", case=False, regex=True, na=False)
        & extraction["mean_pct"].between(35, 103, inclusive="both")
    ].copy()
    seed["year_num"] = pd.to_numeric(seed["year"], errors="coerce")
    seed = seed[seed["year_num"].between(2010, 2026)]
    seed = seed[seed["primary_result"].str.lower().ne("no")]

    def period(year: float) -> str:
        if year <= 2018:
            return "2010-2018"
        if year <= 2022:
            return "2019-2022"
        return "2023-2026"

    seed["period"] = seed["year_num"].apply(period)
    periods = ["2010-2018", "2019-2022", "2023-2026"]
    groups = [
        ("Inductive", ["Inductive / no target"], COL["blue"]),
        ("Transductive", ["Transductive / UDA"], COL["orange"]),
        ("Few-shot", ["Few-shot / labels"], COL["green"]),
        ("Ambig./\ninvalid", ["Ambiguous / suspect", "Leakage / invalid"], COL["red"]),
    ]
    for yi, (_, buckets, color) in enumerate(groups):
        for xi, per in enumerate(periods):
            g = seed[seed["period"].eq(per) & seed["protocol_bucket"].isin(buckets)]
            if g.empty:
                ax_b.text(
                    xi,
                    yi,
                    "n=0",
                    ha="center",
                    va="center",
                    fontsize=5.8,
                    color="#9AA3AF",
                )
                continue
            median = float(g["mean_pct"].median())
            n = int(len(g))
            ax_b.scatter(xi, yi, s=72 + 28 * np.sqrt(n), color=color, alpha=0.78, edgecolor="white", lw=0.8)
            ax_b.text(
                xi,
                yi,
                f"{median:.0f}\nn={n}",
                ha="center",
                va="center",
                fontsize=6.3,
                linespacing=0.88,
                color=COL["dark"],
                bbox=dict(boxstyle="round,pad=0.08", facecolor="white", edgecolor="none", alpha=0.74),
            )
    ax_b.set_xticks(np.arange(len(periods)))
    ax_b.set_xticklabels(["2010-\n2018", "2019-\n2022", "2023-\n2026"], fontsize=6.0)
    ax_b.set_yticks(np.arange(len(groups)))
    ax_b.set_yticklabels([g[0] for g in groups], fontsize=6.2)
    ax_b.set_xlim(-0.55, len(periods) - 0.45)
    ax_b.set_ylim(len(groups) - 0.5, -0.5)
    ax_b.set_title("SEED median accuracy", loc="left", fontsize=8.2, pad=5)
    ax_b.text(
        0.98,
        1.045,
        "cell = median %, n rows",
        transform=ax_b.transAxes,
        ha="right",
        va="bottom",
        fontsize=5.9,
        color=COL["gray"],
    )
    for spine in ax_b.spines.values():
        spine.set_visible(False)
    ax_b.set_xticks(np.arange(-0.5, len(periods), 1), minor=True)
    ax_b.set_yticks(np.arange(-0.5, len(groups), 1), minor=True)
    ax_b.grid(which="minor", color=COL["grid"], lw=0.4)
    ax_b.tick_params(axis="both", length=0)
    add_panel(ax_b, "B")

    # C. Poolable strata across datasets.
    pooled = pooled_meta(meta)

    def point_label(ax: plt.Axes, x: float, y: float, n: int, xmax: float, side: str | None = None) -> None:
        if side == "left" or (side is None and x > xmax - 4.2):
            dx, ha = -0.62, "right"
        else:
            dx, ha = 0.62, "left"
        ax.text(
            x + dx,
            y,
            f"{x:.1f} ({n})",
            ha=ha,
            va="center",
            fontsize=5.6,
            color=COL["dark"],
            bbox=dict(boxstyle="round,pad=0.08", facecolor="white", edgecolor="none", alpha=0.78),
            zorder=4,
        )

    task_order = [
        ("SEED\n3-class", "SEED | 3-class"),
        ("SEED-IV\n4-class", "SEED-IV | 4-class"),
        ("SEED-V\n5-class", "SEED-V | 5-class"),
        ("DEAP\nvalence", "DEAP | valence (binary)"),
        ("DEAP\narousal", "DEAP | arousal (binary)"),
        ("DREAMER\nvalence", "DREAMER | valence (binary)"),
        ("DREAMER\narousal", "DREAMER | arousal (binary)"),
    ]
    strata = [
        ("inductive/no-target", COL["blue"], -0.24),
        ("transductive-UDA", COL["orange"], 0.00),
        ("few-shot/target-label", COL["green"], 0.24),
    ]
    ax_c.axvspan(90, 97, color="#F8E8E8", zorder=0)
    for i, (_, task) in enumerate(task_order):
        for strat, color, offset in strata:
            r = pooled[(pooled["task"].eq(task)) & (pooled["stratum"].eq(strat))]
            if r.empty:
                continue
            row = r.iloc[0]
            yi = i + offset
            ax_c.plot([row["DL_ci_lo"], row["DL_ci_hi"]], [yi, yi], color=color, lw=1.1, alpha=0.86)
            ax_c.scatter(row["DL_mean"], yi, s=22 + 9 * np.sqrt(row["k"]), color=color, edgecolor="white", lw=0.6, zorder=3)
            side = "left" if task in {"SEED | 3-class", "SEED-IV | 4-class"} and strat != "inductive/no-target" else None
            point_label(ax_c, float(row["DL_mean"]), yi, int(row["k"]), 99, side=side)
    ax_c.set_yticks(np.arange(len(task_order)))
    ax_c.set_yticklabels([label for label, _ in task_order], fontsize=6.0)
    ax_c.set_xlim(57, 99)
    ax_c.set_ylim(len(task_order) - 0.55, -0.55)
    ax_c.set_title("Poolable strata", loc="left", fontsize=8.2, pad=5)
    ax_c.text(
        0.99,
        1.045,
        "whiskers = 95% CI",
        transform=ax_c.transAxes,
        ha="right",
        va="bottom",
        fontsize=5.9,
        color=COL["gray"],
    )
    ax_c.set_xlabel("pooled accuracy (%)", fontsize=6.4)
    clean_axes(ax_c, "x")
    add_panel(ax_c, "C")

    # D. Matched-task protocol comparison.
    tasks = [
        ("SEED 3-class", "SEED | 3-class"),
        ("SEED-IV 4-class", "SEED-IV | 4-class"),
        ("DEAP valence", "DEAP | valence (binary)"),
    ]
    ax_d.axvspan(90, 98, color="#F8E8E8", zorder=0)
    for i, (label, task) in enumerate(tasks):
        no_target = pooled[(pooled["task"].eq(task)) & (pooled["stratum"].eq("inductive/no-target"))]
        transductive = pooled[(pooled["task"].eq(task)) & (pooled["stratum"].eq("transductive-UDA"))]
        if not no_target.empty and not transductive.empty:
            delta = float(transductive.iloc[0]["DL_mean"]) - float(no_target.iloc[0]["DL_mean"])
            ax_d.text(61.0, i + 0.31, f"UDA {delta:+.1f}", fontsize=5.8, color=COL["gray"], ha="left", va="center")
        for strat, color, offset in strata:
            r = pooled[(pooled["task"].eq(task)) & (pooled["stratum"].eq(strat))]
            if r.empty:
                continue
            row = r.iloc[0]
            yi = i + offset
            ax_d.plot([row["DL_ci_lo"], row["DL_ci_hi"]], [yi, yi], color=color, lw=1.35, alpha=0.88)
            ax_d.scatter(row["DL_mean"], yi, s=28 + 9 * np.sqrt(row["k"]), color=color, edgecolor="white", lw=0.6, zorder=3)
            side = "left" if task == "SEED | 3-class" and strat != "inductive/no-target" else None
            point_label(ax_d, float(row["DL_mean"]), yi, int(row["k"]), 99, side=side)
    ax_d.set_yticks(np.arange(len(tasks)))
    ax_d.set_yticklabels([label for label, _ in tasks], fontsize=6.2)
    ax_d.set_xlim(60, 99)
    ax_d.set_ylim(len(tasks) - 0.55, -0.55)
    ax_d.set_title("Matched protocol shifts", loc="left", fontsize=8.2, pad=5)
    ax_d.text(
        0.99,
        1.045,
        "whiskers = 95% CI",
        transform=ax_d.transAxes,
        ha="right",
        va="bottom",
        fontsize=5.9,
        color=COL["gray"],
    )
    ax_d.set_xlabel("pooled accuracy (%)", fontsize=6.4)
    clean_axes(ax_d, "x")
    add_panel(ax_d, "D")

    handles = [
        mpl.lines.Line2D([0], [0], marker="o", color=COL["blue"], label="Inductive", markerfacecolor=COL["blue"], markeredgecolor="white", lw=1.3, markersize=4.2),
        mpl.lines.Line2D([0], [0], marker="o", color=COL["orange"], label="Transductive", markerfacecolor=COL["orange"], markeredgecolor="white", lw=1.3, markersize=4.2),
        mpl.lines.Line2D([0], [0], marker="o", color=COL["green"], label="Few-shot", markerfacecolor=COL["green"], markeredgecolor="white", lw=1.3, markersize=4.2),
    ]
    fig.legend(handles=handles, frameon=False, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.005), handletextpad=0.35, columnspacing=1.2, title="Protocol; line = 95% CI")
    fig.suptitle("Evidence landscape for cross-subject EEG emotion recognition", y=0.992, fontsize=8.2)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.91, bottom=0.09, hspace=0.52, wspace=0.42)
    savefig(fig, "fig11_evidence_landscape_ABCD")


def fig9_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(3.55, 2.18))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    border = patches.Rectangle((0.025, 0.035), 0.95, 0.91, facecolor="white", edgecolor="#B8C1CC", lw=0.72)
    ax.add_patch(border)
    ax.add_patch(patches.Rectangle((0.025, 0.865), 0.95, 0.08, facecolor="#EEF2F6", edgecolor="#B8C1CC", lw=0.72))
    ax.text(0.047, 0.905, "Algorithm 1.", ha="left", va="center", color=COL["dark"], fontsize=6.2)
    ax.text(
        0.205,
        0.905,
        "Leakage-safe benchmarking protocol",
        ha="left",
        va="center",
        color=COL["dark"],
        fontsize=6.2,
    )

    lines = [
        ("Input:", "D, subject/session IDs, labels y, target-access mode a"),
        ("Output:", "subject scores, 95% CI, and audit metadata"),
        ("1:", "define stratum = dataset x task x protocol x target-access"),
        ("2:", "split subjects into train/validation/test folds"),
        ("3:", "for each fold f do"),
        ("4:", "   fit preprocessing on training subjects only"),
        ("5:", "   tune model using validation subjects only"),
        ("6:", "   evaluate locked model on held-out subjects"),
        ("7:", "end for"),
        ("8:", "aggregate subject scores; report mean, 95% CI, class balance"),
        ("9:", "release code, seeds, fold IDs, exclusions, and target access"),
    ]

    y = 0.815
    for tag, text in lines:
        if tag in {"Input:", "Output:"}:
            ax.text(0.055, y, tag, ha="left", va="center", color=COL["dark"], fontsize=5.2)
            ax.text(0.160, y, text, ha="left", va="center", color=COL["gray"], fontsize=5.2)
            y -= 0.058
        else:
            ax.text(0.055, y, tag, ha="left", va="center", color=COL["blue"], fontsize=5.05, family="DejaVu Sans Mono")
            ax.text(0.112, y, text, ha="left", va="center", color=COL["dark"], fontsize=5.05, family="DejaVu Sans Mono")
            y -= 0.056

    ax.add_patch(patches.Rectangle((0.045, 0.065), 0.91, 0.09, facecolor="#F7F8FA", edgecolor="#D8DEE7", lw=0.5))
    ax.text(0.061, 0.112, "Audit checks:", ha="left", va="center", color=COL["dark"], fontsize=5.0)
    ax.text(
        0.215,
        0.112,
        "matched strata; no outside-fold normalization; no test-subject tuning",
        ha="left",
        va="center",
        color=COL["gray"],
        fontsize=4.85,
    )
    savefig(fig, "fig9_benchmark_pipeline")


def fig10_roadmap() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    items = [
        ("Benchmarking", "registered splits\nmulti-dataset leaderboards\nchance-normalized metrics", COL["blue"]),
        ("Statistics", "subject-level uncertainty\nmultilevel synthesis\noutlier diagnostics", COL["orange"]),
        ("Models", "source-only DG\nuncertainty-aware adaptation\nsubject-conditioned reps", COL["green"]),
        ("Reproducibility", "open code and folds\npreprocessing provenance\nleakage audit", COL["purple"]),
    ]
    coords = [(0.08, 0.53), (0.54, 0.53), (0.08, 0.18), (0.54, 0.18)]
    for (head, body, color), (x, y) in zip(items, coords):
        rect = patches.FancyBboxPatch((x, y), 0.38, 0.24, boxstyle="round,pad=0.012,rounding_size=0.012",
                                      linewidth=1.0, edgecolor=color, facecolor="white")
        ax.add_patch(rect)
        ax.text(x + 0.02, y + 0.18, head, ha="left", va="center", color=color, weight="bold", fontsize=8.4)
        ax.text(x + 0.02, y + 0.10, body, ha="left", va="center", color=COL["dark"], fontsize=7.0, linespacing=1.18)
    ax.text(0.5, 0.93, "Future agenda: make each reported number auditable", ha="center", va="top", fontsize=8.2)
    ax.text(0.5, 0.05, "Every claim should state the problem solved, target access used, and uncertainty around the estimate.",
            ha="center", va="bottom", fontsize=7.2, color=COL["dark"])
    savefig(fig, "fig10_research_roadmap")


def write_manifest(extraction: pd.DataFrame) -> None:
    included_mask = extraction["include_narrative"].str.lower().eq("yes")
    meta_mask = extraction["include_meta"].str.lower().eq("yes")
    included = extraction.loc[included_mask, "paper_id"].nunique()
    included_rows = int(included_mask.sum())
    strict_meta = extraction.loc[meta_mask, "paper_id"].nunique()
    strict_meta_rows = int(meta_mask.sum())
    text = f"""# Nature-Style Revised Figure Manifest

Generated by `scripts/generate_nature_style_figures.py`.

Data sources:

- `04_extraction/extraction_master.csv` ({included} included studies; {included_rows} active result rows; {strict_meta} strict meta-eligible studies; {strict_meta_rows} meta rows)
- `06_quality/risk_of_bias_scoring.csv`
- `07_meta_analysis/meta_results.csv`
- `07_meta_analysis/moderator_analysis.csv`

Use these figures by changing the manuscript graphics path to:

```tex
\\graphicspath{{../10_figures_nature_style/}}
```

Design notes:

- Minimal, Nature-inspired visual language: white background, thin axes, muted colorblind palette, panel-ready typography.
- Data-first replacements for the earlier boxed utility figures.
- Same base filenames as the manuscript figures, exported as PNG, PDF, and SVG.

Caption notes:

- Fig. 6 is an evidence map, not a universal few-shot > transductive > inductive ladder.
- Fig. 7a is a SEED 3-class protocol-normalized pooled-estimate figure with individual study points, not a traditional study-level CI forest.
"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "manifest.md").write_text(text, encoding="utf-8")


def main() -> None:
    configure()
    extraction, quality, meta, mod = base.load_data()
    fig1_prisma(extraction)
    fig2_taxonomy()
    fig3_risk(extraction)
    fig4_coverage(extraction)
    fig5_timeline(extraction, meta)
    fig6_bubble_heatmap(meta)
    fig7_seed_forest(meta)
    fig7_dataset_companion(meta, "SEED-IV", "fig7b_forest_SEEDIV_4class")
    fig7_dataset_companion(meta, "DEAP", "fig7c_forest_DEAP")
    fig8_ladder(meta)
    fig11_evidence_landscape_abcd(extraction, meta)
    fig9_pipeline()
    fig10_roadmap()
    write_manifest(extraction)
    generate_prisma_flow.main()


if __name__ == "__main__":
    main()
