from __future__ import annotations

import json
import math
import re
import textwrap
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.colors import LinearSegmentedColormap


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "10_figures_revised"
EXTRACTION = ROOT / "04_extraction" / "extraction_master.csv"
QUALITY = ROOT / "06_quality" / "risk_of_bias_scoring.csv"
META = ROOT / "07_meta_analysis" / "meta_results.csv"
MOD = ROOT / "07_meta_analysis" / "moderator_analysis.csv"
SUMMARY = ROOT / "07_meta_analysis" / "statistics_summary_20260704.json"


PALETTE = {
    "inductive": "#2C6B8E",
    "transductive": "#D9822B",
    "fewshot": "#4B8B3B",
    "crossdataset": "#7E5AA6",
    "leakage": "#B23A48",
    "unclear": "#6B7280",
    "neutral": "#374151",
    "light": "#F3F4F6",
    "grid": "#D1D5DB",
    "text": "#111827",
}


DATASETS = OrderedDict(
    [
        ("SEED", r"(?<![-A-Z])SEED(?![-A-Z])"),
        ("SEED-IV", r"SEED[- ]?IV"),
        ("SEED-V", r"SEED[- ]?V(?!I)"),
        ("SEED-VII", r"SEED[- ]?VII"),
        ("DEAP", r"DEAP"),
        ("DREAMER", r"DREAMER"),
        ("MAHNOB-HCI", r"MAHNOB"),
        ("AMIGOS", r"AMIGOS"),
        ("FACED", r"FACED"),
        ("MPED", r"MPED"),
        ("GAMEEMO", r"GAMEEMO"),
    ]
)


def configure() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 450,
            "savefig.bbox": "tight",
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.titlesize": 10,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.5,
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def savefig(fig: plt.Figure, name: str, vector: bool = True) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png")
    if vector:
        fig.savefig(OUT / f"{name}.pdf")
        fig.savefig(OUT / f"{name}.svg")
    plt.close(fig)


def num(value) -> float:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    s = str(value).strip()
    if not s or s.lower() in {"na", "n/a", "none", "not reported", "not captured", "unclear"}:
        return np.nan
    s = s.replace("%", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return np.nan
    v = float(m.group(0))
    if 0 < v <= 1.5:
        v *= 100
    return v


def dataset_mask(series: pd.Series, dataset: str) -> pd.Series:
    pat = DATASETS[dataset]
    return series.fillna("").str.contains(pat, flags=re.IGNORECASE, regex=True)


def risk_bucket(value: str) -> str:
    s = str(value).lower()
    if s in {"low", "low-some"} or "low" in s and "some" not in s:
        return "Low / low-some"
    if "some" in s:
        return "Some concerns"
    if "high" in s or "unclear" in s:
        return "High / unclear"
    return "Not classified"


def protocol_bucket(row: pd.Series) -> str:
    txt = " ".join(
        str(row.get(c, "")).lower()
        for c in [
            "protocol_category",
            "split_type",
            "cross_setting",
            "adaptation_method",
            "leakage_categories",
            "ambiguity_notes",
        ]
    )
    labels = str(row.get("target_labels_used", "")).lower()
    target = str(row.get("target_data_used", "")).lower()
    if any(x in txt for x in ["subject-dependent", "subject mixed", "subject-mixed", "pseudo-cross", "leakage"]):
        return "Leakage / invalid"
    if any(x in txt for x in ["ambiguous", "suspect", "unclear"]):
        return "Ambiguous / suspect"
    if any(x in txt for x in ["few-shot", "target-calibration", "semi-supervised", " target labels", "f-like"]) or labels == "yes":
        return "Few-shot / labels"
    if "cross-dataset" in txt or re.search(r"\be\b", txt):
        return "Cross-dataset"
    if any(x in txt for x in ["transductive", "uda", "domain adaptation", "adversarial-da", "source-free"]) or target == "yes":
        return "Transductive / UDA"
    if any(x in txt for x in ["inductive", "no target", "domain generalization", "loso", "dg"]):
        return "Inductive / no target"
    return "Other / unclear"


def protocol_color(bucket: str) -> str:
    return {
        "Inductive / no target": PALETTE["inductive"],
        "Transductive / UDA": PALETTE["transductive"],
        "Few-shot / labels": PALETTE["fewshot"],
        "Cross-dataset": PALETTE["crossdataset"],
        "Leakage / invalid": PALETTE["leakage"],
        "Ambiguous / suspect": PALETTE["leakage"],
        "Other / unclear": PALETTE["unclear"],
    }.get(bucket, PALETTE["unclear"])


def parse_studies(cell: str) -> list[tuple[str, float, float]]:
    out: list[tuple[str, float, float]] = []
    if not isinstance(cell, str):
        return out
    for part in cell.split(";"):
        m = re.match(r"\s*(EEG-\d+)\(([-.\d]+)(?:/([-.0-9]+))?\)", part.strip())
        if not m:
            continue
        out.append((m.group(1), float(m.group(2)), float(m.group(3)) if m.group(3) else np.nan))
    return out


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    extraction = pd.read_csv(EXTRACTION, dtype=str).fillna("")
    quality = pd.read_csv(QUALITY, dtype=str).fillna("")
    meta = pd.read_csv(META, dtype=str).fillna("")
    mod = pd.read_csv(MOD, dtype=str).fillna("")
    extraction["mean_pct"] = extraction["result_mean"].map(num)
    extraction["sd_pct"] = extraction["result_sd"].map(num)
    extraction["protocol_bucket"] = extraction.apply(protocol_bucket, axis=1)
    extraction["risk_bucket"] = extraction["risk_rating"].map(risk_bucket)
    quality_small = quality[["paper_id", "quality_band", "fatal_flag", "percent"]].drop_duplicates("paper_id")
    extraction = extraction.merge(quality_small, on="paper_id", how="left", suffixes=("", "_quality"))
    return extraction, quality, meta, mod


def load_counts() -> dict[str, int]:
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    return {
        "raw_database_records": int(data["raw_database_records"]),
        "duplicates_removed": int(data["duplicates_removed"]),
        "unique_records_screened": int(data["unique_records_screened"]),
        "reports_assessed": int(data["reports_assessed_or_sought_after_adjudication"]),
        "screening_excluded": int(data["screening_excluded_after_adjudication"]),
        "qualitative_included": int(data["qualitative_included_studies"]),
        "qualitative_rows": int(data["qualitative_result_rows"]),
        "meta_eligible": int(data["meta_eligible_studies"]),
        "meta_rows": int(data["meta_eligible_result_rows"]),
    }


def draw_card(
    ax,
    xy,
    wh,
    title,
    body,
    edge="#9CA3AF",
    face="#FFFFFF",
    title_color=None,
    lw=1.0,
    title_font=8.2,
    body_font=7.6,
):
    x, y = xy
    w, h = wh
    box = patches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=lw,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(box)
    ax.text(
        x + w / 2,
        y + h - min(0.028, h * 0.18),
        title,
        ha="center",
        va="top",
        color=title_color or edge,
        weight="bold",
        fontsize=title_font,
    )
    ax.text(
        x + w / 2,
        y + h * 0.43,
        body,
        ha="center",
        va="center",
        color=PALETTE["text"],
        fontsize=body_font,
        linespacing=1.18,
    )


def fig1_prisma(extraction: pd.DataFrame):
    counts = load_counts()
    fig, ax = plt.subplots(figsize=(7.2, 7.8))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    title = "PRISMA 2020 Flow for the Verified Evidence Corpus"
    ax.text(0.5, 0.975, title, ha="center", va="top", fontsize=12, weight="bold", color=PALETTE["text"])

    boxes = [
        (0.08, 0.82, 0.84, 0.105, "Identification", f"{counts['raw_database_records']:,} database records\nIEEE Xplore 251 | WoS 656 | Scopus 616 | PubMed 141", PALETTE["inductive"]),
        (0.08, 0.68, 0.84, 0.105, "Deduplication", f"{counts['duplicates_removed']:,} duplicate records removed\n{counts['unique_records_screened']:,} unique records screened", PALETTE["neutral"]),
        (0.08, 0.54, 0.84, 0.105, "Title / Abstract Screening", f"{counts['reports_assessed']:,} reports assessed or sought\n{counts['screening_excluded']:,} records excluded", PALETTE["transductive"]),
        (0.08, 0.39, 0.84, 0.115, "Full-Text Verification", f"{counts['qualitative_included']:,} active included studies verified from primary full text\n{counts['qualitative_rows']:,} extracted result rows", PALETTE["fewshot"]),
        (0.08, 0.235, 0.84, 0.115, "Quantitative Synthesis", f"{counts['meta_eligible']:,} meta-eligible studies | {counts['meta_rows']:,} strict meta rows\nHigh-risk, ambiguous, and no-dispersion rows kept narrative-only", PALETTE["crossdataset"]),
    ]
    for i, (x, y, w, h, head, body, color) in enumerate(boxes):
        draw_card(ax, (x, y), (w, h), head, body, edge=color, face="#FFFFFF", title_color=color, lw=1.3)
        if i < len(boxes) - 1:
            ax.annotate(
                "",
                xy=(0.5, boxes[i + 1][1] + boxes[i + 1][3] + 0.01),
                xytext=(0.5, y - 0.01),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#6B7280"),
            )
    draw_card(
        ax,
        (0.08, 0.085),
        (0.84, 0.105),
        "Scope Note",
        "Verified full-text evidence sample, not a guaranteed exhaustive census.\nQueued/unobtainable reports are excluded from pooling, not guessed.",
        edge=PALETTE["leakage"],
        face="#FFF7F7",
        title_color=PALETTE["leakage"],
        lw=1.2,
    )
    savefig(fig, "fig1_prisma_flow")


def fig2_taxonomy():
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.5, 0.96, "Target-Access Protocol Taxonomy", ha="center", va="top", fontsize=12, weight="bold")
    levels = [
        ("No target data", "Inductive LOSO; domain generalization; source-only cross-dataset", PALETTE["inductive"]),
        ("Unlabeled target", "Transductive UDA; source-free DA; test-time adaptation", PALETTE["transductive"]),
        ("Labeled target", "Few-shot calibration; semi-supervised labels; personalization", PALETTE["fewshot"]),
        ("Invalid / ambiguous", "Subject-mixed CV; trial/window leakage; unreported target access", PALETTE["leakage"]),
    ]
    x, w, h = 0.12, 0.76, 0.105
    ys = [0.77, 0.59, 0.41, 0.23]
    for i, (head, body, color) in enumerate(levels):
        box = patches.FancyBboxPatch(
            (x, ys[i]),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            linewidth=1.25,
            edgecolor=color,
            facecolor="#FFFFFF",
        )
        ax.add_patch(box)
        ax.text(x + 0.15, ys[i] + h / 2, head, ha="center", va="center", color=color, weight="bold", fontsize=8.7)
        ax.text(x + 0.34, ys[i] + h / 2, body, ha="left", va="center", color=PALETTE["text"], fontsize=7.6)
        if i < len(levels) - 1:
            ax.annotate("", xy=(0.5, ys[i + 1] + h + 0.018), xytext=(0.5, ys[i] - 0.018),
                        arrowprops=dict(arrowstyle="-|>", color="#6B7280", lw=1.0))
    ax.text(0.16, 0.135, "Interpretation rule", color=PALETTE["text"], weight="bold", fontsize=8.5, ha="left")
    ax.text(
        0.16,
        0.085,
        "Compare results only within a rung. Accuracy generally rises as target access becomes easier,\n"
        "but that does not mean subject-independent generalization improved.",
        color=PALETTE["text"],
        fontsize=7.8,
        ha="left",
        va="top",
    )
    ax.text(0.50, 0.19, "harder generalization -> easier or invalid claims", color="#6B7280", fontsize=7.6, ha="center")
    savefig(fig, "fig2_protocol_taxonomy")


def fig3_risk_scatter(extraction: pd.DataFrame):
    d = extraction.copy()
    metric_mask = d["metric"].str.contains("acc|accuracy|f1", case=False, regex=True, na=False)
    d = d[metric_mask & d["mean_pct"].between(0, 105, inclusive="both")].copy()
    d = d[d["primary_result"].str.lower().ne("no")]
    order = ["Low / low-some", "Some concerns", "High / unclear", "Not classified"]
    d["risk_y"] = d["risk_bucket"].map({v: i for i, v in enumerate(order)})
    rng = np.random.default_rng(13)
    d["jitter"] = d["risk_y"] + rng.normal(0, 0.065, len(d))
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.axvspan(90, 105, color="#FEE2E2", alpha=0.75, zorder=0)
    for bucket, g in d.groupby("protocol_bucket"):
        pooled = g["include_meta"].str.lower().eq("yes")
        ax.scatter(
            g.loc[pooled, "mean_pct"],
            g.loc[pooled, "jitter"],
            s=22,
            c=protocol_color(bucket),
            alpha=0.72,
            edgecolors="white",
            linewidths=0.35,
            label=bucket,
        )
        ax.scatter(
            g.loc[~pooled, "mean_pct"],
            g.loc[~pooled, "jitter"],
            s=20,
            c=protocol_color(bucket),
            alpha=0.35,
            marker="x" if bucket in {"Leakage / invalid", "Ambiguous / suspect"} else "o",
            linewidths=0.75,
        )
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order)
    ax.set_xlim(35, 103)
    ax.set_xlabel("Reported classification performance (%)")
    ax.set_title("Reported Performance by Leakage Risk")
    ax.grid(axis="x", color=PALETTE["grid"], lw=0.5)
    ax.text(90.5, 3.15, "near-ceiling\nclaim zone", color=PALETTE["leakage"], fontsize=7.5, ha="left", va="top")
    handles, labels = ax.get_legend_handles_labels()
    uniq = OrderedDict()
    for h, l in zip(handles, labels):
        if l not in uniq:
            uniq[l] = h
    fig.subplots_adjust(bottom=0.28)
    ax.legend(
        uniq.values(),
        uniq.keys(),
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=3,
        frameon=False,
        handletextpad=0.25,
        columnspacing=0.75,
    )
    ax.spines[["top", "right"]].set_visible(False)
    savefig(fig, "fig3_accuracy_vs_risk")


def fig4_coverage(extraction: pd.DataFrame):
    rows = []
    for dataset in DATASETS:
        m = dataset_mask(extraction["dataset_name"], dataset)
        incl = extraction[m & extraction["include_narrative"].str.lower().eq("yes")]["paper_id"].nunique()
        meta = extraction[m & extraction["include_meta"].str.lower().eq("yes")]["paper_id"].nunique()
        rows.append((dataset, incl, meta))
    cov = pd.DataFrame(rows, columns=["dataset", "included", "meta"]).sort_values("included", ascending=True)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    y = np.arange(len(cov))
    ax.barh(y, cov["included"], color="#DBEAFE", edgecolor=PALETTE["inductive"], height=0.68, label="narrative included")
    ax.barh(y, cov["meta"], color=PALETTE["inductive"], height=0.36, label="meta-eligible")
    for yi, inc, met in zip(y, cov["included"], cov["meta"]):
        ax.text(inc + max(cov["included"]) * 0.012, yi, f"{inc}", va="center", fontsize=7.5, color=PALETTE["text"])
        if met > 0:
            ax.text(met + max(cov["included"]) * 0.012, yi - 0.18, f"{met}", va="center", fontsize=7, color=PALETTE["inductive"])
    ax.set_yticks(y)
    ax.set_yticklabels(cov["dataset"])
    ax.set_xlabel("Unique studies with dataset-specific result")
    ax.set_title("Dataset Coverage: Breadth vs Poolable Evidence")
    ax.grid(axis="x", color=PALETTE["grid"], lw=0.5)
    ax.legend(frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    savefig(fig, "fig4_dataset_coverage")


def fig5_timeline(extraction: pd.DataFrame, meta: pd.DataFrame):
    d = extraction[
        dataset_mask(extraction["dataset_name"], "SEED")
        & extraction["metric"].str.contains("acc|accuracy", case=False, regex=True, na=False)
        & extraction["mean_pct"].between(35, 103, inclusive="both")
    ].copy()
    d["year_num"] = pd.to_numeric(d["year"], errors="coerce")
    d = d[d["year_num"].between(2010, 2026)]
    d = d[d["primary_result"].str.lower().ne("no")]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.axhspan(90, 103, color="#FEE2E2", alpha=0.65, zorder=0)
    for bucket, g in d.groupby("protocol_bucket"):
        ax.scatter(
            g["year_num"],
            g["mean_pct"],
            s=np.where(g["include_meta"].str.lower().eq("yes"), 26, 18),
            c=protocol_color(bucket),
            alpha=np.where(g["include_meta"].str.lower().eq("yes"), 0.75, 0.35),
            edgecolors="white",
            linewidths=0.35,
            label=bucket,
        )
    for stratum, color in [("inductive/no-target", PALETTE["inductive"]), ("transductive-UDA", PALETTE["transductive"])]:
        row = meta[(meta["task"].eq("SEED | 3-class")) & (meta["stratum"].eq(stratum))]
        if not row.empty and row.iloc[0]["DL_mean"]:
            y = float(row.iloc[0]["DL_mean"])
            ax.axhline(y, color=color, lw=1.15, ls="--")
            ax.text(2026.35, y, f"{stratum.split('/')[0]} {y:.1f}%", color=color, fontsize=7.2, va="center")
    ax.text(2010.5, 101.0, "near-ceiling claim zone", color=PALETTE["leakage"], fontsize=7.5, va="top")
    ax.set_xlim(2010, 2027.8)
    ax.set_ylim(45, 103)
    ax.set_xlabel("Publication year")
    ax.set_ylabel("SEED reported accuracy (%)")
    ax.set_title("SEED Accuracy Over Time, Stratified by Protocol")
    ax.grid(True, color=PALETTE["grid"], lw=0.45, alpha=0.9)
    handles, labels = ax.get_legend_handles_labels()
    uniq = OrderedDict()
    for h, l in zip(handles, labels):
        if l not in uniq:
            uniq[l] = h
    ax.legend(uniq.values(), uniq.keys(), loc="lower left", ncol=2, frameon=False, handletextpad=0.25, columnspacing=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    savefig(fig, "fig5_seed_year_protocol")


def fig6_heatmap(meta: pd.DataFrame):
    pooled = meta[pd.to_numeric(meta["DL_mean"], errors="coerce").notna()].copy()
    pooled["mean"] = pooled["DL_mean"].astype(float)
    pooled["k_num"] = pooled["k"].astype(int)
    task_order = [
        "SEED | 3-class",
        "SEED-IV | 4-class",
        "SEED-V | 5-class",
        "DEAP | valence (binary)",
        "DEAP | arousal (binary)",
        "DREAMER | valence (binary)",
        "DREAMER | arousal (binary)",
    ]
    strat_order = ["inductive/no-target", "transductive-UDA", "few-shot/target-label"]
    mat = pd.DataFrame(np.nan, index=task_order, columns=strat_order)
    lab = pd.DataFrame("", index=task_order, columns=strat_order)
    for _, r in pooled.iterrows():
        if r["task"] in mat.index and r["stratum"] in mat.columns:
            mat.loc[r["task"], r["stratum"]] = r["mean"]
            lab.loc[r["task"], r["stratum"]] = f"{r['mean']:.1f}\nk={int(r['k_num'])}"
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    cmap = LinearSegmentedColormap.from_list("eeg", ["#F8FAFC", "#D8E9F3", "#8BBAD0", "#2C6B8E"])
    masked = np.ma.masked_invalid(mat.values.astype(float))
    im = ax.imshow(masked, cmap=cmap, vmin=55, vmax=92, aspect="auto")
    ax.set_xticks(np.arange(len(strat_order)))
    ax.set_xticklabels(["Inductive\n(no target)", "Transductive\n(unlabeled target)", "Few-shot\n(target labels)"])
    ax.set_yticks(np.arange(len(task_order)))
    ax.set_yticklabels([t.replace(" | ", "\n") for t in task_order])
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if lab.iloc[i, j]:
                ax.text(j, i, lab.iloc[i, j], ha="center", va="center", fontsize=7.5, color=PALETTE["text"])
            else:
                ax.text(j, i, "narr.", ha="center", va="center", fontsize=7, color="#9CA3AF")
    ax.set_title("Poolable Evidence by Dataset, Task, and Target Access")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(strat_order), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(task_order), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.4)
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cbar.set_label("Pooled accuracy (%)")
    savefig(fig, "fig6_evidence_heatmap")


def fig7_pooled_forest(meta: pd.DataFrame):
    pooled = meta[pd.to_numeric(meta["DL_mean"], errors="coerce").notna()].copy()
    pooled["mean"] = pooled["DL_mean"].astype(float)
    pooled["lo"] = pooled["DL_ci_lo"].astype(float)
    pooled["hi"] = pooled["DL_ci_hi"].astype(float)
    pooled["k_num"] = pooled["k"].astype(int)
    keep = pooled[pooled["k_num"].ge(3)].copy()
    keep["label"] = keep["task"].str.replace(" | ", " - ", regex=False) + " - " + keep["stratum"].str.replace("-", " ")
    order_tasks = ["SEED | 3-class", "SEED-IV | 4-class", "SEED-V | 5-class", "DEAP | valence (binary)", "DEAP | arousal (binary)", "DREAMER | valence (binary)", "DREAMER | arousal (binary)"]
    order_strat = {"inductive/no-target": 0, "transductive-UDA": 1, "few-shot/target-label": 2}
    keep["task_order"] = keep["task"].map({t: i for i, t in enumerate(order_tasks)}).fillna(99)
    keep["strat_order"] = keep["stratum"].map(order_strat).fillna(99)
    keep = keep.sort_values(["task_order", "strat_order"], ascending=[False, False]).reset_index(drop=True)
    fig_h = max(5.2, 0.38 * len(keep) + 1.2)
    fig, ax = plt.subplots(figsize=(7.6, fig_h))
    y = np.arange(len(keep))
    colors = keep["stratum"].map({
        "inductive/no-target": PALETTE["inductive"],
        "transductive-UDA": PALETTE["transductive"],
        "few-shot/target-label": PALETTE["fewshot"],
    }).fillna(PALETTE["unclear"])
    for yi, (_, r), c in zip(y, keep.iterrows(), colors):
        ax.plot([r["lo"], r["hi"]], [yi, yi], color=c, lw=1.4)
        ax.scatter(r["mean"], yi, s=42 + 2.2 * r["k_num"], color=c, edgecolor="white", linewidth=0.5, zorder=3)
        ax.text(100.7, yi, f"{r['mean']:.1f} [{r['lo']:.1f}, {r['hi']:.1f}]   k={r['k_num']}, I2={r['I2']}%", va="center", fontsize=7.2)
    ax.axvline(50, color="#9CA3AF", lw=0.7, ls=":")
    ax.axvspan(90, 100, color="#FEE2E2", alpha=0.45, zorder=0)
    ax.set_yticks(y)
    ax.set_yticklabels(keep["label"])
    ax.set_xlim(45, 122)
    ax.set_xlabel("Pooled accuracy (%) with display CI")
    ax.set_title("Primary Pooled Strata: Protocol-Normalized Forest")
    ax.grid(axis="x", color=PALETTE["grid"], lw=0.45)
    ax.text(118, len(keep) - 0.4, "Estimate [CI]   k, I2", ha="right", va="top", fontsize=7.3, color=PALETTE["neutral"])
    ax.text(99.2, len(keep) - 0.35, "near-ceiling\nclaim zone", color=PALETTE["leakage"], fontsize=7.1, ha="right", va="top")
    ax.spines[["top", "right", "left"]].set_visible(False)
    savefig(fig, "fig7a_forest_SEED_3class")


def fig7_dataset_forests(meta: pd.DataFrame, dataset_prefix: str, filename: str):
    pooled = meta[pd.to_numeric(meta["DL_mean"], errors="coerce").notna()].copy()
    pooled = pooled[pooled["task"].str.startswith(dataset_prefix)].copy()
    if pooled.empty:
        return
    pooled["mean"] = pooled["DL_mean"].astype(float)
    pooled["lo"] = pooled["DL_ci_lo"].astype(float)
    pooled["hi"] = pooled["DL_ci_hi"].astype(float)
    pooled["k_num"] = pooled["k"].astype(int)
    pooled = pooled.sort_values(["task", "stratum"], ascending=[False, False]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.2, max(2.8, 0.42 * len(pooled) + 1.1)))
    y = np.arange(len(pooled))
    colors = pooled["stratum"].map({
        "inductive/no-target": PALETTE["inductive"],
        "transductive-UDA": PALETTE["transductive"],
        "few-shot/target-label": PALETTE["fewshot"],
    }).fillna(PALETTE["unclear"])
    for yi, (_, r), c in zip(y, pooled.iterrows(), colors):
        ax.plot([r["lo"], r["hi"]], [yi, yi], color=c, lw=1.4)
        ax.scatter(r["mean"], yi, s=45 + 2 * r["k_num"], color=c, edgecolor="white", linewidth=0.5, zorder=3)
        ax.text(101, yi, f"{r['mean']:.1f} [{r['lo']:.1f}, {r['hi']:.1f}] k={r['k_num']}", va="center", fontsize=7.2)
    ax.set_yticks(y)
    ax.set_yticklabels((pooled["task"] + " - " + pooled["stratum"]).str.replace(" | ", " - ", regex=False))
    ax.set_xlim(45, 120)
    ax.set_xlabel("Pooled accuracy (%)")
    ax.set_title(f"{dataset_prefix} Pooled Strata")
    ax.grid(axis="x", color=PALETTE["grid"], lw=0.45)
    ax.spines[["top", "right", "left"]].set_visible(False)
    savefig(fig, filename)


def fig8_ladder(mod: pd.DataFrame):
    subset = mod[mod["analysis"].isin(["SEED-3 by adaptation setting", "SEED-IV by adaptation setting"])].copy()
    subset = subset[subset["level"].isin(["inductive", "transductive", "few-shot"])]
    subset["pooled_num"] = pd.to_numeric(subset["pooled"], errors="coerce")
    subset["lo"] = pd.to_numeric(subset["ci_lo"], errors="coerce")
    subset["hi"] = pd.to_numeric(subset["ci_hi"], errors="coerce")
    order = ["inductive", "transductive", "few-shot"]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.axhspan(90, 103, color="#FEE2E2", alpha=0.55, zorder=0)
    x_base = np.arange(len(order))
    offsets = {"SEED-3 by adaptation setting": -0.08, "SEED-IV by adaptation setting": 0.08}
    labels = {"SEED-3 by adaptation setting": "SEED 3-class", "SEED-IV by adaptation setting": "SEED-IV 4-class"}
    colors = {"SEED-3 by adaptation setting": PALETTE["inductive"], "SEED-IV by adaptation setting": PALETTE["transductive"]}
    for analysis, g in subset.groupby("analysis"):
        xs, ys, lo, hi = [], [], [], []
        for i, lvl in enumerate(order):
            r = g[g["level"].eq(lvl)]
            if r.empty or pd.isna(r.iloc[0]["pooled_num"]):
                continue
            xs.append(i + offsets[analysis])
            y = r.iloc[0]["pooled_num"]
            ys.append(y)
            lo.append(max(0, y - r.iloc[0]["lo"]))
            hi.append(max(0, r.iloc[0]["hi"] - y))
        ax.errorbar(xs, ys, yerr=[lo, hi], fmt="o-", color=colors[analysis], lw=1.4, ms=5.2, capsize=3, label=labels[analysis])
    ax.set_xticks(x_base)
    ax.set_xticklabels(["Inductive\n(no target)", "Transductive\n(unlabeled target)", "Few-shot\n(target labels)"])
    ax.set_ylim(58, 101)
    ax.set_ylabel("Pooled accuracy (%)")
    ax.set_title("Target Access Changes the Task, Not Just the Model")
    ax.text(0.03, 0.94, "Near-ceiling zone: leakage / protocol ambiguity must be audited", transform=ax.transAxes,
            color=PALETTE["leakage"], fontsize=7.5, va="top")
    ax.grid(axis="y", color=PALETTE["grid"], lw=0.45)
    ax.legend(frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    savefig(fig, "fig8_protocol_ladder")


def fig9_pipeline():
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.5, 0.96, "Leakage-Safe Benchmarking Pipeline", ha="center", va="top", fontsize=12, weight="bold")
    steps = [
        ("1", "Split", "Subject/session/trial\ndisjointness first"),
        ("2", "Preprocess", "Fit scalers/PCA/features\ninside each CV fold"),
        ("3", "Target access", "No target vs unlabeled\nvs labeled target"),
        ("4", "Validation", "Validation subject/fold\nmust not be test"),
        ("5", "Statistics", "Mean + SD/CI,\nper-subject results"),
        ("6", "Code/splits", "Seeds, configs,\nfold definitions"),
    ]
    box_w = 0.22
    box_h = 0.22
    xs = [0.055, 0.39, 0.725]
    ys = [0.60, 0.29]
    positions = [(xs[i % 3], ys[i // 3]) for i in range(6)]
    for i, ((n, head, body), (x, y)) in enumerate(zip(steps, positions)):
        draw_card(
            ax,
            (x, y),
            (box_w, box_h),
            "",
            body,
            edge=PALETTE["inductive"],
            face="#FFFFFF",
            title_color=PALETTE["inductive"],
            lw=1.15,
            title_font=7.2,
            body_font=7.3,
        )
        circ = patches.Circle((x + 0.030, y + box_h - 0.045), 0.023, facecolor=PALETTE["inductive"], edgecolor="none")
        ax.add_patch(circ)
        ax.text(x + 0.030, y + box_h - 0.045, n, ha="center", va="center", color="white", weight="bold", fontsize=8)
        ax.text(
            x + 0.064,
            y + box_h - 0.043,
            head,
            ha="left",
            va="center",
            color=PALETTE["inductive"],
            weight="bold",
            fontsize=7.4,
        )
        if i not in [2, 5]:
            nx, ny = positions[i + 1]
            ax.annotate("", xy=(nx - 0.018, ny + box_h * 0.50), xytext=(x + box_w + 0.018, y + box_h * 0.50),
                        arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#6B7280"))
        elif i == 2:
            nx, ny = positions[3]
            ax.annotate("", xy=(nx + box_w * 0.50, ny + box_h + 0.015), xytext=(x + box_w * 0.50, y - 0.015),
                        arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#6B7280", connectionstyle="arc3,rad=-0.2"))
    ax.text(0.5, 0.08, "Minimum standard: compare only within matched dataset x task x protocol x target-access strata.",
            ha="center", va="center", fontsize=8.5, color=PALETTE["neutral"], weight="bold")
    savefig(fig, "fig9_benchmark_pipeline")


def fig10_roadmap():
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.5, 0.96, "Research Roadmap for Credible Cross-Subject EEG Affect Recognition", ha="center", va="top", fontsize=11.5, weight="bold")
    lanes = [
        ("Benchmarking", "registered splits; multi-dataset leaderboards; normalized metrics", PALETTE["inductive"]),
        ("Statistics", "subject-level uncertainty; multilevel synthesis; outlier diagnostics", PALETTE["transductive"]),
        ("Models", "source-only DG; uncertainty-aware adaptation; subject-conditioned reps", PALETTE["fewshot"]),
        ("Reproducibility", "open code/folds; preprocessing provenance; leakage audit", PALETTE["crossdataset"]),
    ]
    for i, (head, body, color) in enumerate(lanes):
        y = 0.72 - i * 0.16
        left = patches.FancyBboxPatch(
            (0.08, y),
            0.22,
            0.10,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            linewidth=1.15,
            edgecolor=color,
            facecolor="#FFFFFF",
        )
        right = patches.FancyBboxPatch(
            (0.36, y),
            0.56,
            0.10,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            linewidth=0.9,
            edgecolor="#6B7280",
            facecolor="#F9FAFB",
        )
        ax.add_patch(left)
        ax.add_patch(right)
        ax.text(0.19, y + 0.05, head, ha="center", va="center", color=color, weight="bold", fontsize=8.2)
        ax.annotate("", xy=(0.35, y + 0.05), xytext=(0.31, y + 0.05), arrowprops=dict(arrowstyle="-|>", color="#6B7280", lw=0.9))
        ax.text(0.385, y + 0.066, body, ha="left", va="center", color=PALETTE["text"], fontsize=7.15)
        ax.text(0.385, y + 0.034, "Claim must state split, target access, and uncertainty.", ha="left", va="center", color="#4B5563", fontsize=7.3, weight="bold")
    ax.text(0.5, 0.08, "Goal: a field where a reported number states the problem solved, the target access used, and the uncertainty around it.",
            ha="center", va="center", fontsize=8.4, color=PALETTE["neutral"], weight="bold")
    savefig(fig, "fig10_research_roadmap")


def write_manifest(extraction: pd.DataFrame, quality: pd.DataFrame, meta: pd.DataFrame):
    included_mask = extraction["include_narrative"].str.lower().eq("yes")
    meta_mask = extraction["include_meta"].str.lower().eq("yes")
    strict_meta = extraction.loc[meta_mask, "paper_id"].nunique()
    strict_meta_rows = int(meta_mask.sum())
    included = extraction.loc[included_mask, "paper_id"].nunique()
    rows = int(included_mask.sum())
    captions = f"""# Revised Figure Manifest

Generated by `scripts/generate_revised_figures.py` from:

- `04_extraction/extraction_master.csv` ({included} included studies; {rows} active result rows; {strict_meta} strict meta-eligible studies; {strict_meta_rows} meta rows)
- `06_quality/risk_of_bias_scoring.csv`
- `07_meta_analysis/meta_results.csv`
- `07_meta_analysis/moderator_analysis.csv`

Outputs are saved as PNG + PDF + SVG, using the same base filenames as the current manuscript figures.

## Recommended manuscript replacement

Change:

```tex
\\graphicspath{{../10_figures/}}
```

to:

```tex
\\graphicspath{{../10_figures_revised/}}
```

## Figures

1. `fig1_prisma_flow` - clean PRISMA flow using the current 1,664 -> 777 -> 647 -> 405 -> 99 counts.
2. `fig2_protocol_taxonomy` - target-access ladder, emphasizing that protocols should not be pooled across rungs.
3. `fig3_accuracy_vs_risk` - reported classification performance by risk rating and protocol bucket.
4. `fig4_dataset_coverage` - unique included versus meta-eligible studies per dataset.
5. `fig5_seed_year_protocol` - SEED accuracy over time with current pooled inductive/transductive reference lines.
6. `fig6_evidence_heatmap` - poolable dataset-task-protocol strata from `meta_results.csv`.
7. `fig7a_forest_SEED_3class` - revised as a compact pooled-strata forest rather than a massive individual-study forest. This is more appropriate for IEEE two-column layout.
8. `fig7b_forest_SEEDIV_4class` and `fig7c_forest_DEAP` - compact dataset-specific pooled forest companions.
9. `fig8_protocol_ladder` - target-access contrast for SEED and SEED-IV using moderator estimates.
10. `fig9_benchmark_pipeline` - leakage-safe benchmarking workflow.
11. `fig10_research_roadmap` - concise future-work roadmap.

## Caption note

The current manuscript caption for Fig. 6 says "Few-shot > transductive > inductive." The expanded corpus no longer supports a simple monotonic statement across datasets. Use a neutral caption such as:

> Pooled accuracy by dataset, task, and target-access protocol. Cells show pooled accuracy and k where a stratum is poolable; narrative-only cells are marked separately. The figure emphasizes sparse maturity and protocol dependence rather than a universal monotonic ladder.

For Fig. 7, update the caption because the revised figure is pooled-strata, not study-level:

> Protocol-normalized pooled-strata forest. Points show DerSimonian-Laird pooled accuracy with display CIs; marker size scales with k and labels report k and I2. High heterogeneity means estimates are descriptive rather than population effects.
"""
    (OUT / "captions.md").write_text(captions, encoding="utf-8")


def main():
    configure()
    extraction, quality, meta, mod = load_data()
    fig1_prisma(extraction)
    fig2_taxonomy()
    fig3_risk_scatter(extraction)
    fig4_coverage(extraction)
    fig5_timeline(extraction, meta)
    fig6_heatmap(meta)
    fig7_pooled_forest(meta)
    fig7_dataset_forests(meta, "SEED-IV", "fig7b_forest_SEEDIV_4class")
    fig7_dataset_forests(meta, "DEAP", "fig7c_forest_DEAP")
    fig8_ladder(mod)
    fig9_pipeline()
    fig10_roadmap()
    write_manifest(extraction, quality, meta)


if __name__ == "__main__":
    main()
