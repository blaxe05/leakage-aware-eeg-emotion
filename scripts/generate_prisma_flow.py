from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "07_meta_analysis" / "statistics_summary_20260704.json"
OUT_DIRS = [
    ROOT / "10_figures_nature_style",
    ROOT / "10_figures_revised",
]


def configure() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "font.family": "DejaVu Sans",
            "font.size": 7.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


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
        "qualitative_rows": int(data["qualitative_result_rows"]),
        "meta_eligible": int(data["meta_eligible_studies"]),
        "meta_rows": int(data["meta_eligible_result_rows"]),
    }


def box(ax, x: float, y: float, w: float, h: float, text: str, face: str = "#FFFFFF", edge: str = "#2F3A45") -> None:
    rect = patches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.010,rounding_size=0.010",
        linewidth=0.9,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=6.8, color="#111827", linespacing=1.13)


def arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(arrowstyle="-|>", lw=0.85, color="#4B5563", shrinkA=2, shrinkB=2),
    )


def label_band(ax, y0: float, y1: float, text: str) -> None:
    ax.text(0.055, (y0 + y1) / 2, text, ha="center", va="center", rotation=90, fontsize=7.7, color="#374151")
    ax.plot([0.085, 0.085], [y0, y1], color="#CBD5E1", lw=1.0)


def draw() -> plt.Figure:
    counts = load_counts()
    fig, ax = plt.subplots(figsize=(7.2, 7.35))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0.055, 1)

    ax.text(0.5, 0.965, "PRISMA 2020 flow diagram", ha="center", va="top", fontsize=8.8, color="#111827")
    ax.text(0.5, 0.936, "Verified full-text evidence corpus for cross-subject EEG emotion recognition", ha="center", va="top", fontsize=7.0, color="#4B5563")

    left_x, right_x = 0.14, 0.63
    w_left, w_right = 0.43, 0.31
    h = 0.095
    y_ident, y_screen, y_report, y_qual, y_meta = 0.79, 0.62, 0.45, 0.28, 0.13

    label_band(ax, 0.74, 0.90, "Identification")
    label_band(ax, 0.39, 0.69, "Screening")
    label_band(ax, 0.08, 0.34, "Included")

    box(
        ax,
        left_x,
        y_ident,
        w_left,
        h,
        f"Records identified from databases\n(n = {counts['raw_database_records']:,})\nIEEE Xplore: 251; WoS: 656\nScopus: 616; PubMed: 141",
        face="#F8FAFC",
    )
    box(
        ax,
        right_x,
        y_ident,
        w_right,
        h,
        f"Records removed before screening\nDuplicates removed\n(n = {counts['duplicates_removed']:,})",
        face="#F8FAFC",
    )
    box(ax, left_x, y_screen, w_left, h, f"Records screened\n(n = {counts['unique_records_screened']:,})", face="#FFFFFF")
    box(ax, right_x, y_screen, w_right, h, f"Records excluded\n(n = {counts['screening_excluded']:,})", face="#FFFFFF")
    box(ax, left_x, y_report, w_left, h, f"Reports assessed for eligibility\n(n = {counts['reports_assessed']:,})", face="#FFFFFF")
    box(
        ax,
        right_x,
        y_report,
        w_right,
        h,
        f"Reports excluded, unobtainable,\nor queued after full text\n(n = {counts['reports_excluded']:,})",
        face="#FFFFFF",
    )
    box(
        ax,
        left_x,
        y_qual,
        w_left,
        h,
        f"Studies included in\nqualitative synthesis\n(n = {counts['qualitative_included']:,}; result rows = {counts['qualitative_rows']:,})",
        face="#F0FDF4",
        edge="#527A57",
    )
    box(
        ax,
        left_x,
        y_meta,
        w_left,
        h,
        f"Studies included in\nquantitative synthesis\n(n = {counts['meta_eligible']:,}; meta rows = {counts['meta_rows']:,})",
        face="#EFF6FF",
        edge="#3B6E8F",
    )

    arrow(ax, (left_x + w_left, y_ident + h / 2), (right_x, y_ident + h / 2))
    arrow(ax, (left_x + w_left / 2, y_ident), (left_x + w_left / 2, y_screen + h))
    arrow(ax, (left_x + w_left, y_screen + h / 2), (right_x, y_screen + h / 2))
    arrow(ax, (left_x + w_left / 2, y_screen), (left_x + w_left / 2, y_report + h))
    arrow(ax, (left_x + w_left, y_report + h / 2), (right_x, y_report + h / 2))
    arrow(ax, (left_x + w_left / 2, y_report), (left_x + w_left / 2, y_qual + h))
    arrow(ax, (left_x + w_left / 2, y_qual), (left_x + w_left / 2, y_meta + h))

    return fig


def main() -> None:
    configure()
    fig = draw()
    for out in OUT_DIRS:
        out.mkdir(parents=True, exist_ok=True)
        for name in ("fig1_prisma_flow", "fig1_prisma_flow_common_prisma", "fig1_prisma_flow_prisma_wrapped"):
            fig.savefig(out / f"{name}.png", bbox_inches="tight", pad_inches=0.02)
            fig.savefig(out / f"{name}.pdf", bbox_inches="tight", pad_inches=0.02)
            fig.savefig(out / f"{name}.svg", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


if __name__ == "__main__":
    main()
