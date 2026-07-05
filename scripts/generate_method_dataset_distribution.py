from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
import re

import numpy as np
import pandas as pd

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import pdist


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "04_extraction" / "extraction_master.csv"
OUT = ROOT / "10_figures_nature_style"
SUMMARY = ROOT / "07_meta_analysis" / "method_dataset_distribution.csv"

DATASETS = [
    "SEED",
    "SEED-IV",
    "SEED-V",
    "SEED-VII",
    "DEAP",
    "DREAMER",
    "MAHNOB-HCI",
    "AMIGOS",
    "FACED",
    "MPED",
    "GAMEEMO",
]

FAMILY_ORDER = OrderedDict(
    [
        ("Transfer / UDA", "#D1903F"),
        ("Domain generalization / source-free", "#7A6DA8"),
        ("Few-shot / meta-learning", "#5D8B61"),
        ("Contrastive / self-supervised", "#4F8FBA"),
        ("Graph / GNN", "#3B6E8F"),
        ("Transformer / attention", "#8A6BBE"),
        ("CNN / RNN / capsule", "#6E7F80"),
        ("Traditional ML / handcrafted", "#A46A3F"),
        ("Multimodal / fusion", "#B55A5C"),
        ("Other / unclear", "#6B7280"),
    ]
)


def configure() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 170,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "font.family": "DejaVu Sans",
            "font.size": 7.4,
            "axes.titlesize": 8.5,
            "axes.labelsize": 7.5,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "axes.linewidth": 0.55,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def normalize_datasets(value: object) -> list[str]:
    text = str(value or "").upper()
    found: list[str] = []
    for name in DATASETS:
        token = name.upper()
        if token in text:
            found.append(name)
    # Avoid counting SEED inside SEED-IV / SEED-V / SEED-VII unless SEED appears as a standalone token.
    if "SEED" in found:
        standalone_seed = re.search(r"(^|[^A-Z0-9])SEED([^A-Z0-9]|$)", text) is not None
        if not standalone_seed:
            found.remove("SEED")
    return found


def coarse_family(row: pd.Series) -> str:
    text = " ".join(
        str(row.get(col, ""))
        for col in ["model_family", "feature_type", "adaptation_method", "protocol_category"]
    ).lower()

    if any(k in text for k in ["few-shot", "few shot", "meta-transfer", "meta learning", "meta-learning"]):
        return "Few-shot / meta-learning"
    if any(k in text for k in ["domain generalization", "source-free", "source free", "dg-no-target", " k (domain", "source-only"]):
        return "Domain generalization / source-free"
    if any(k in text for k in ["uda", "domain adaptation", "domain-adaptation", "domain-adversarial", "adversarial da", "mmd", "coral", "tca", "subdomain", "prototype", "pseudo-label", "transfer learning", "transductive"]):
        return "Transfer / UDA"
    if any(k in text for k in ["contrastive", "self-supervised", "self supervised", "ssl"]):
        return "Contrastive / self-supervised"
    if any(k in text for k in ["multimodal", "multi-modal", "fusion", "eeg+eye", "eeg+other", "eeg+peripheral"]):
        return "Multimodal / fusion"
    if any(k in text for k in ["graph", "gnn", "gcn", "gat", "topological", "brain-network"]):
        return "Graph / GNN"
    if any(k in text for k in ["transformer", "attention", "vit", "mamba"]):
        return "Transformer / attention"
    if any(k in text for k in ["cnn", "rnn", "lstm", "gru", "capsule", "conv", "temporal"]):
        return "CNN / RNN / capsule"
    if any(k in text for k in ["svm", "traditional", "knn", "random forest", "elm", "manifold", "riemannian", "dictionary", "feature selection", "handcrafted", "psd", "differential entropy", "de features"]):
        return "Traditional ML / handcrafted"
    return "Other / unclear"


def clustered_order(mat: pd.DataFrame, axis: int) -> list[str]:
    data = mat.to_numpy(dtype=float)
    labels = list(mat.index if axis == 0 else mat.columns)
    arr = data if axis == 0 else data.T
    keep = arr.sum(axis=1) > 0
    if keep.sum() <= 2:
        return labels
    # Correlation is unstable for sparse all-zero-like vectors; cosine works better for usage profiles.
    dist = pdist(arr[keep], metric="cosine")
    dist = np.nan_to_num(dist, nan=1.0, posinf=1.0, neginf=1.0)
    z = linkage(dist, method="average")
    ordered_kept = [np.array(labels)[keep][i] for i in leaves_list(z)]
    ordered_empty = [label for label, ok in zip(labels, keep) if not ok]
    return ordered_kept + ordered_empty


def build_distribution() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(DATA)
    df = df[df["include_narrative"].astype(str).str.lower().eq("yes")].copy()
    df = df[df["primary_result"].astype(str).str.lower().eq("yes")].copy()

    records = []
    for _, row in df.iterrows():
        datasets = normalize_datasets(row.get("dataset_name", ""))
        if not datasets:
            continue
        family = coarse_family(row)
        for dataset in datasets:
            records.append(
                {
                    "paper_id": row["paper_id"],
                    "dataset": dataset,
                    "method_family": family,
                    "year": row.get("year", np.nan),
                    "include_meta": row.get("include_meta", "no"),
                }
            )

    long = pd.DataFrame(records).drop_duplicates(["paper_id", "dataset", "method_family"])
    counts = (
        long.groupby(["method_family", "dataset"], as_index=False)
        .agg(n_study_dataset_uses=("paper_id", "nunique"))
        .sort_values(["method_family", "dataset"])
    )
    counts.to_csv(SUMMARY, index=False)

    mat = counts.pivot(index="method_family", columns="dataset", values="n_study_dataset_uses").fillna(0).astype(int)
    for fam in FAMILY_ORDER:
        if fam not in mat.index:
            mat.loc[fam] = 0
    for dataset in DATASETS:
        if dataset not in mat.columns:
            mat[dataset] = 0
    mat = mat.loc[list(FAMILY_ORDER), DATASETS]
    return mat, long


def plot(mat: pd.DataFrame) -> None:
    row_order = clustered_order(mat, axis=0)
    col_order = clustered_order(mat, axis=1)
    mat = mat.loc[row_order, col_order]

    max_count = max(1, int(mat.to_numpy().max()))
    fig = plt.figure(figsize=(7.15, 4.25))
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[0.92, 0.08],
        height_ratios=[0.18, 0.82],
        wspace=0.04,
        hspace=0.13,
    )
    ax_top = fig.add_subplot(gs[0, 0])
    ax = fig.add_subplot(gs[1, 0])
    ax_cbar = fig.add_subplot(gs[1, 1])

    col_totals = mat.sum(axis=0)
    x = np.arange(len(mat.columns))
    ax_top.bar(x, col_totals.values, color="#D9DEE7", edgecolor="#6B7280", linewidth=0.45)
    ax_top.set_xlim(-0.5, len(mat.columns) - 0.5)
    ax_top.set_xticks([])
    ax_top.set_ylabel("uses", labelpad=2)
    ax_top.spines[["top", "right"]].set_visible(False)
    ax_top.spines[["bottom"]].set_visible(False)
    ax_top.tick_params(axis="y", labelsize=6.5, length=2)
    ax_top.grid(axis="y", color="#E6EAF0", lw=0.45)
    ax_top.set_axisbelow(True)

    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "family_count", ["#F6F8FB", "#DDE8F0", "#A9C4D6", "#5F92B3", "#2D5C7A"]
    )
    norm = LogNorm(vmin=1, vmax=max_count)
    size_min, size_max = 20, 500
    for yi, fam in enumerate(mat.index):
        for xi, dataset in enumerate(mat.columns):
            val = int(mat.loc[fam, dataset])
            if val == 0:
                ax.scatter(xi, yi, s=9, color="#E5E7EB", marker="s", linewidths=0, zorder=1)
                continue
            scaled = np.log1p(val) / np.log1p(max_count)
            area = size_min + scaled * (size_max - size_min)
            ax.scatter(
                xi,
                yi,
                s=area,
                color=cmap(norm(val)),
                edgecolor="#1F2937",
                linewidth=0.35,
                zorder=3,
            )
            if val >= 3:
                ax.text(
                    xi,
                    yi,
                    str(val),
                    ha="center",
                    va="center",
                    fontsize=6.2,
                    color="#111827" if val < max_count * 0.50 else "white",
                    zorder=4,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(mat.columns, rotation=35, ha="right", rotation_mode="anchor")
    ax.set_yticks(np.arange(len(mat.index)))
    ax.set_yticklabels(mat.index)
    ax.invert_yaxis()
    ax.set_xlim(-0.5, len(mat.columns) - 0.5)
    ax.set_ylim(len(mat.index) - 0.5, -0.5)
    ax.set_xlabel("Public benchmark dataset")
    ax.grid(color="#E6EAF0", lw=0.45)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)

    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(sm, cax=ax_cbar)
    cbar.set_label("unique study-dataset uses", rotation=90, labelpad=6)
    ticks = [1, 3, 10, 30, 100]
    ticks = [t for t in ticks if t <= max_count]
    if max_count not in ticks:
        ticks.append(max_count)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([str(t) for t in ticks])
    cbar.ax.tick_params(labelsize=6.5, length=2)
    cbar.outline.set_linewidth(0.45)

    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"fig_method_dataset_distribution.{ext}", bbox_inches="tight", pad_inches=0.025)
    plt.close(fig)


def main() -> None:
    configure()
    mat, long = build_distribution()
    plot(mat)
    print(f"Saved {SUMMARY}")
    print(f"Saved {OUT / 'fig_method_dataset_distribution.png'}")
    print(f"Unique paper-dataset-family uses: {len(long)}")
    print("Top cells:")
    print(
        mat.stack()
        .sort_values(ascending=False)
        .head(12)
        .rename("count")
        .reset_index()
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
