from __future__ import annotations

from pathlib import Path
import csv

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.path import Path as MplPath


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "10_figures_nature_style"
VERIFY = ROOT / "04_extraction" / "dataset_electrode_source_verification_20260628.csv"

COL = {
    "dark": "#1F2933",
    "text": "#303843",
    "muted": "#5F6C7B",
    "grid": "#D6DCE5",
    "blue": "#2F6685",
    "orange": "#C7832D",
    "green": "#4F8056",
    "pale": "#F8FAFC",
    "outline": "#1554C8",
    "frontal": "#DDE6FF",
    "central": "#FFFFFF",
    "temporal": "#BEE8D2",
    "parietal": "#F7B8BC",
    "occipital": "#FFE2AE",
}


def configure() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 180,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "font.family": "DejaVu Sans",
            "font.size": 7.0,
            "axes.titlesize": 7.6,
            "axes.titleweight": "normal",
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def row(labels: list[str], y: float, width: float) -> dict[str, tuple[float, float]]:
    if len(labels) == 1:
        return {labels[0]: (0.0, y)}
    xs = [(-width / 2.0) + (width * i / (len(labels) - 1)) for i in range(len(labels))]
    return {lab: (x, y) for lab, x in zip(labels, xs)}


def montage_62() -> dict[str, tuple[float, float]]:
    pts: dict[str, tuple[float, float]] = {}
    pts.update(row(["FP1", "FPZ", "FP2"], 0.88, 0.70))
    pts.update(row(["AF3", "AF4"], 0.73, 0.50))
    pts.update(row(["F7", "F5", "F3", "F1", "FZ", "F2", "F4", "F6", "F8"], 0.56, 1.60))
    pts.update(row(["FT7", "FC5", "FC3", "FC1", "FCZ", "FC2", "FC4", "FC6", "FT8"], 0.32, 1.76))
    pts.update(row(["T7", "C5", "C3", "C1", "CZ", "C2", "C4", "C6", "T8"], 0.05, 1.88))
    pts.update(row(["TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "CP4", "CP6", "TP8"], -0.22, 1.76))
    pts.update(row(["P7", "P5", "P3", "P1", "PZ", "P2", "P4", "P6", "P8"], -0.49, 1.58))
    pts.update(row(["PO7", "PO5", "PO3", "POZ", "PO4", "PO6", "PO8"], -0.72, 1.18))
    pts.update(row(["CB1", "O1", "OZ", "O2", "CB2"], -0.90, 0.82))
    return pts


def montage_32() -> dict[str, tuple[float, float]]:
    base = montage_62()
    labels = [
        "FP1",
        "AF3",
        "F3",
        "F7",
        "FC5",
        "FC1",
        "C3",
        "T7",
        "CP5",
        "CP1",
        "P3",
        "P7",
        "PO3",
        "O1",
        "OZ",
        "PZ",
        "FP2",
        "AF4",
        "FZ",
        "F4",
        "F8",
        "FC6",
        "FC2",
        "CZ",
        "C4",
        "T8",
        "CP6",
        "CP2",
        "P4",
        "P8",
        "PO4",
        "O2",
    ]
    return {lab: base[lab] for lab in labels}


def montage_14() -> dict[str, tuple[float, float]]:
    base = montage_62()
    labels = ["AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"]
    return {lab: base[lab] for lab in labels}


def draw_head(
    ax: plt.Axes,
    pts: dict[str, tuple[float, float]],
    color: str,
    panel: str,
    title: str,
    label_mode: str,
) -> None:
    ax.set_aspect("equal")
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.18, 1.17)
    ax.axis("off")
    ax.add_patch(patches.Circle((0, 0), 1.02, facecolor="white", edgecolor=COL["dark"], lw=0.72))
    ax.add_patch(
        patches.Polygon(
            [(-0.09, 1.00), (0, 1.12), (0.09, 1.00)],
            closed=False,
            fill=False,
            edgecolor=COL["dark"],
            lw=0.72,
            joinstyle="miter",
        )
    )
    ax.add_patch(patches.Arc((-1.045, 0), 0.15, 0.30, theta1=270, theta2=90, edgecolor=COL["dark"], lw=0.62))
    ax.add_patch(patches.Arc((1.045, 0), 0.15, 0.30, theta1=90, theta2=270, edgecolor=COL["dark"], lw=0.62))
    for radius in (0.35, 0.67):
        ax.add_patch(patches.Circle((0, 0), radius, fill=False, edgecolor=COL["grid"], lw=0.30, ls=(0, (1.2, 2.2))))
    ax.plot([0, 0], [-0.98, 0.98], color=COL["grid"], lw=0.30, ls=(0, (1.2, 2.2)))
    ax.plot([-0.98, 0.98], [0, 0], color=COL["grid"], lw=0.30, ls=(0, (1.2, 2.2)))

    xs = [v[0] for v in pts.values()]
    ys = [v[1] for v in pts.values()]
    size = 12 if len(pts) > 40 else 20 if len(pts) > 14 else 24
    ax.scatter(xs, ys, s=size, color=color, edgecolor="white", linewidth=0.45, zorder=3)

    landmarks = {"FP1", "FPZ", "FP2", "AF3", "AF4", "F7", "FZ", "F8", "T7", "CZ", "T8", "P7", "PZ", "P8", "O1", "OZ", "O2"}
    for lab, (x, y) in pts.items():
        if label_mode == "all" or (label_mode == "landmarks" and lab in landmarks):
            if label_mode == "landmarks" and lab not in landmarks:
                continue
            fs = 4.45 if len(pts) > 40 else 5.55 if len(pts) > 14 else 6.2
            radius = max((x * x + y * y) ** 0.5, 0.20)
            offset = 0.065 if len(pts) > 40 else 0.075
            ox = offset * x / radius
            oy = offset * y / radius
            if lab in {"FP1", "FPZ", "FP2"}:
                oy = 0.075
            ax.text(x + ox, y + oy, lab, ha="center", va="center", fontsize=fs, color=COL["text"])

    ax.text(-1.06, 1.16, panel, ha="left", va="bottom", fontsize=8.5, fontweight="bold", color=COL["dark"])
    ax.text(-0.92, 1.16, title, ha="left", va="bottom", fontsize=7.8, color=COL["dark"])


def electrode_region(label: str) -> str:
    if label.startswith(("FP", "AF", "F", "FC")):
        return COL["frontal"]
    if label.startswith(("FT", "T", "TP")):
        return COL["temporal"]
    if label.startswith(("P", "CP", "PO")):
        return COL["parietal"]
    if label.startswith(("O", "CB")):
        return COL["occipital"]
    return COL["central"]


def draw_schematic_head(
    ax: plt.Axes,
    pts: dict[str, tuple[float, float]],
    panel: str,
    title: str,
    label_mode: str,
) -> None:
    ax.set_aspect("equal")
    ax.set_xlim(-1.30, 1.30)
    ax.set_ylim(-1.20, 1.18)
    ax.axis("off")

    head_fill = patches.Circle((0, 0), 1.02, facecolor="white", edgecolor="none", lw=0, zorder=0)
    ax.add_patch(head_fill)

    # A soft frontal band echoes clinical montage diagrams while remaining schematic.
    band_x = [-0.88, -0.70, -0.45, -0.20, 0.0, 0.20, 0.45, 0.70, 0.88, 0.95, 0.72, 0.43, 0.17, 0.0, -0.17, -0.43, -0.72, -0.95]
    band_y = [0.52, 0.72, 0.87, 0.97, 1.02, 0.97, 0.87, 0.72, 0.52, 0.28, 0.30, 0.34, 0.42, 0.32, 0.42, 0.34, 0.30, 0.28]
    band = ax.fill(band_x, band_y, color="#DCE6FF", alpha=0.68, zorder=1, linewidth=0)[0]
    band.set_clip_path(head_fill)

    ax.add_patch(patches.Circle((0, 0), 1.02, fill=False, edgecolor="#111827", lw=0.95, zorder=3))
    ax.add_patch(
        patches.Polygon(
            [(-0.10, 1.00), (0, 1.14), (0.10, 1.00)],
            closed=False,
            fill=False,
            edgecolor="#111827",
            lw=0.95,
            joinstyle="miter",
            zorder=4,
        )
    )
    ax.add_patch(patches.Circle((-1.08, 0.0), 0.12, fill=False, edgecolor="#AEB6C2", lw=0.85, ls="--", zorder=1))
    ax.add_patch(patches.Circle((1.08, 0.0), 0.12, fill=False, edgecolor="#AEB6C2", lw=0.85, ls="--", zorder=1))
    ax.text(-1.08, 0.0, "A1", ha="center", va="center", fontsize=5.4, color=COL["muted"])
    ax.text(1.08, 0.0, "A2", ha="center", va="center", fontsize=5.4, color=COL["muted"])
    ax.add_patch(patches.Circle((0, 0), 0.78, fill=False, edgecolor="#9FA6B2", lw=0.75, ls=(0, (4, 4)), zorder=1))
    ax.plot([0, 0], [-0.96, 1.02], color="#9FA6B2", lw=0.75, ls=(0, (4, 4)), zorder=1)
    ax.plot([-1.04, 1.04], [0, 0], color="#9FA6B2", lw=0.75, ls=(0, (4, 4)), zorder=1)

    if len(pts) > 40:
        size, font = 68, 4.4
    elif len(pts) > 14:
        size, font = 105, 6.0
    else:
        size, font = 142, 6.8

    landmarks = {"FP1", "FPZ", "FP2", "AF3", "AF4", "F7", "FZ", "F8", "T7", "CZ", "T8", "P7", "PZ", "P8", "O1", "OZ", "O2"}
    for lab, (x, y) in pts.items():
        show_label = label_mode == "all" or lab in landmarks
        ax.scatter(
            [x],
            [y],
            s=size,
            facecolor=electrode_region(lab),
            edgecolor=COL["outline"],
            linewidth=0.78 if len(pts) <= 32 else 0.55,
            zorder=4,
        )
        if show_label:
            ax.text(x, y, lab, ha="center", va="center", fontsize=font, color="#111827", zorder=5)

    ax.text(-1.18, 1.15, panel, ha="left", va="bottom", fontsize=8.2, fontweight="bold", color=COL["dark"])
    ax.text(-1.00, 1.15, title, ha="left", va="bottom", fontsize=7.3, color=COL["dark"])


def add_blob(ax: plt.Axes, coords: list[tuple[float, float]], color: str, clip: patches.Circle, alpha: float = 0.42) -> None:
    verts = coords + [coords[0]]
    codes = [MplPath.MOVETO] + [MplPath.CURVE3] * (len(coords) - 1) + [MplPath.CURVE3]
    patch = patches.PathPatch(MplPath(verts, codes), facecolor=color, edgecolor="none", alpha=alpha, zorder=1)
    patch.set_clip_path(clip)
    ax.add_patch(patch)


def draw_publication_head(
    ax: plt.Axes,
    pts: dict[str, tuple[float, float]],
    panel: str,
    title: str,
    count: str,
    label_mode: str,
    accent: str,
) -> None:
    ax.set_aspect("equal")
    ax.set_xlim(-1.24, 1.24)
    ax.set_ylim(-1.20, 1.17)
    ax.axis("off")

    head_clip = patches.Circle((0, 0), 1.02, facecolor="white", edgecolor="none")
    ax.add_patch(head_clip)
    add_blob(
        ax,
        [(-0.97, 0.33), (-0.78, 0.74), (-0.30, 0.98), (0.0, 1.03), (0.30, 0.98), (0.78, 0.74), (0.97, 0.33), (0.48, 0.37), (0.10, 0.46), (0.0, 0.34), (-0.10, 0.46), (-0.48, 0.37)],
        "#EAF0FF",
        head_clip,
        0.78,
    )
    add_blob(
        ax,
        [(-0.98, 0.18), (-0.80, -0.05), (-0.82, -0.42), (-0.58, -0.54), (-0.42, -0.18), (-0.50, 0.15)],
        "#E3F5EA",
        head_clip,
        0.62,
    )
    add_blob(
        ax,
        [(0.98, 0.18), (0.80, -0.05), (0.82, -0.42), (0.58, -0.54), (0.42, -0.18), (0.50, 0.15)],
        "#E3F5EA",
        head_clip,
        0.62,
    )
    add_blob(
        ax,
        [(-0.72, -0.30), (-0.48, -0.70), (0.0, -0.78), (0.48, -0.70), (0.72, -0.30), (0.30, -0.18), (0.0, -0.25), (-0.30, -0.18)],
        "#FBE5E8",
        head_clip,
        0.62,
    )
    add_blob(
        ax,
        [(-0.46, -0.76), (-0.25, -0.99), (0.0, -1.03), (0.25, -0.99), (0.46, -0.76), (0.20, -0.66), (0.0, -0.68), (-0.20, -0.66)],
        "#FFF0C9",
        head_clip,
        0.74,
    )

    ax.add_patch(patches.Circle((0, 0), 1.02, fill=False, edgecolor="#17202B", lw=0.82, zorder=4))
    ax.add_patch(patches.Polygon([(-0.09, 1.00), (0, 1.12), (0.09, 1.00)], closed=False, fill=False, edgecolor="#17202B", lw=0.82, zorder=4))
    ax.plot([0, 0], [-0.98, 1.00], color="#AEB6C2", lw=0.55, ls=(0, (4, 4)), zorder=2)
    ax.plot([-1.00, 1.00], [0, 0], color="#AEB6C2", lw=0.55, ls=(0, (4, 4)), zorder=2)
    ax.add_patch(patches.Circle((0, 0), 0.76, fill=False, edgecolor="#AEB6C2", lw=0.52, ls=(0, (4, 4)), zorder=2))

    if len(pts) > 40:
        marker_size = 18
    elif len(pts) > 14:
        marker_size = 31
    else:
        marker_size = 43
    label_size = 5.7

    landmarks = {"FP1", "FPZ", "FP2", "AF3", "AF4", "F7", "FZ", "F8", "T7", "CZ", "T8", "P7", "PZ", "P8", "O1", "OZ", "O2"}
    for lab, (x, y) in pts.items():
        ax.scatter([x], [y], s=marker_size, facecolor="white", edgecolor=accent, linewidth=0.78, zorder=5)
        show = label_mode == "all" or lab in landmarks
        if show:
            radius = max((x * x + y * y) ** 0.5, 0.2)
            offset = 0.066 if len(pts) > 40 else 0.075
            tx = x + offset * x / radius
            ty = y + offset * y / radius
            if lab in {"CZ", "FZ", "PZ", "OZ", "FPZ"}:
                tx = x
                ty = y + (0.07 if lab != "OZ" else -0.07)
            ax.text(tx, ty, lab, ha="center", va="center", fontsize=label_size, color="#1E2936", zorder=6)

    ax.text(-1.13, 1.12, panel, ha="left", va="bottom", fontsize=8.2, fontweight="bold", color=COL["dark"])
    ax.text(-0.98, 1.12, title, ha="left", va="bottom", fontsize=7.2, color=COL["dark"])
    ax.text(0.99, 1.12, count, ha="right", va="bottom", fontsize=6.4, color=COL["muted"])


def write_verification() -> None:
    rows = [
        {
            "map_family": "62-channel ESI NeuroScan / 10-20",
            "datasets_in_review": "SEED; SEED-IV; SEED-V; SEED-VII; MPED",
            "source_confirmation": "BCMI SEED/SEED-IV/SEED-V/SEED-VII pages confirm 62-channel ESI NeuroScan or channel_62_pos.locs; MPED source/paper confirms 62-channel EEG.",
            "figure_decision": "single 62-channel panel; safe for SEED-family and MPED count/layout family",
            "source_urls": "https://bcmi.sjtu.edu.cn/home/seed/seed.html | https://bcmi.sjtu.edu.cn/home/seed/seed-iv.html | https://bcmi.sjtu.edu.cn/home/seed/seed-v.html | https://bcmi.sjtu.edu.cn/home/seed/seed-vii.html | https://github.com/Tengfei000/MPED",
        },
        {
            "map_family": "32-channel 10-20/10-20-like",
            "datasets_in_review": "DEAP; MAHNOB-HCI; FACED",
            "source_confirmation": "DEAP official page was unreachable in this pass; primary DEAP records confirm 32 EEG channels. MAHNOB manual confirms BioSemi EEG 32 channels. FACED source paper confirms 32 wet electrodes according to international 10-20.",
            "figure_decision": "one representative 32-channel panel, caption notes exact electrode names can differ across DEAP/MAHNOB/FACED",
            "source_urls": "https://infoscience.epfl.ch/entities/publication/9027bd04-c2c9-4cca-a8b3-a83787aed75a | https://mahnob-db.eu/hci-tagging/media/uploads/manual.pdf | https://www.nature.com/articles/s41597-023-02650-w",
        },
        {
            "map_family": "14-channel Emotiv EPOC/EPOC+",
            "datasets_in_review": "DREAMER; AMIGOS; GAMEEMO",
            "source_confirmation": "DREAMER source page confirms Emotiv EPOC; AMIGOS source text lists 14 channels and names; GAMEEMO Mendeley page confirms 14-channel Emotiv EPOC+.",
            "figure_decision": "single 14-channel Emotiv panel with exact channel names",
            "source_urls": "https://zenodo.org/records/546113 | https://bio-protocol.org/exchange/minidetail?id=8294376&type=30 | https://data.mendeley.com/datasets/b3pn4kwpmn/3",
        },
        {
            "map_family": "custom / varies / subset",
            "datasets_in_review": "custom datasets; multimodal rows; reduced-channel/best-channel subsets",
            "source_confirmation": "Extraction file contains rows marked varies, not verified, 2 best-channel, or few subset.",
            "figure_decision": "not drawn as a montage to avoid implying a common electrode layout",
            "source_urls": "04_extraction/extraction_master.csv",
        },
    ]
    VERIFY.parent.mkdir(parents=True, exist_ok=True)
    with VERIFY.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_figure() -> None:
    configure()
    OUT.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(7.1, 2.42))
    gs = fig.add_gridspec(1, 3, left=0.015, right=0.995, bottom=0.02, top=0.93, wspace=0.12)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    draw_head(
        axes[0],
        montage_62(),
        COL["blue"],
        "A",
        "62-channel NeuroScan",
        label_mode="all",
    )
    draw_head(
        axes[1],
        montage_32(),
        COL["orange"],
        "B",
        "32-channel 10-20-like",
        label_mode="all",
    )
    draw_head(
        axes[2],
        montage_14(),
        COL["green"],
        "C",
        "14-channel Emotiv",
        label_mode="all",
    )
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"fig_electrode_montage_ieee.{ext}", bbox_inches="tight", pad_inches=0.02)
        fig.savefig(OUT / f"fig_electrode_montage_verified.{ext}", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)

    schematic = plt.figure(figsize=(7.1, 2.72))
    gs2 = schematic.add_gridspec(1, 3, left=0.015, right=0.995, bottom=0.02, top=0.92, wspace=0.11)
    saxes = [schematic.add_subplot(gs2[0, i]) for i in range(3)]
    draw_schematic_head(saxes[0], montage_62(), "A", "62-channel NeuroScan", label_mode="landmarks")
    draw_schematic_head(saxes[1], montage_32(), "B", "32-channel 10-20-like", label_mode="all")
    draw_schematic_head(saxes[2], montage_14(), "C", "14-channel Emotiv", label_mode="all")
    for ext in ("png", "pdf", "svg"):
        schematic.savefig(OUT / f"fig_electrode_montage_schematic_ieee.{ext}", bbox_inches="tight", pad_inches=0.02)
    plt.close(schematic)

    pub = plt.figure(figsize=(7.1, 2.58))
    gs3 = pub.add_gridspec(1, 3, left=0.015, right=0.995, bottom=0.02, top=0.91, wspace=0.12)
    paxes = [pub.add_subplot(gs3[0, i]) for i in range(3)]
    draw_publication_head(paxes[0], montage_62(), "A", "NeuroScan montage", "62 channels", "landmarks", COL["blue"])
    draw_publication_head(paxes[1], montage_32(), "B", "10-20-like montage", "32 channels", "all", COL["orange"])
    draw_publication_head(paxes[2], montage_14(), "C", "Emotiv montage", "14 channels", "all", COL["green"])
    for ext in ("png", "pdf", "svg"):
        pub.savefig(OUT / f"fig_electrode_montage_publication_ieee.{ext}", bbox_inches="tight", pad_inches=0.02)
    plt.close(pub)


if __name__ == "__main__":
    write_verification()
    make_figure()
