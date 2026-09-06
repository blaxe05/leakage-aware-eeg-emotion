#!/usr/bin/env python3
"""Generate reviewer-requested descriptive analyses using CPU only."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if (ROOT / "04_extraction").exists():
    EXTRACTION = ROOT / "04_extraction"
    OUTPUT = ROOT / "07_meta_analysis"
else:
    EXTRACTION = ROOT / "03_extraction"
    OUTPUT = ROOT / "05_meta_analysis"
MATCHED_INPUT = EXTRACTION / "matched_target_access_extraction_20260906.csv"
MASTER = EXTRACTION / "extraction_master.csv"
DATASETS = {
    "SEED": r"(?<![-A-Z])SEED(?![-A-Z])",
    "SEED-IV": r"SEED[- ]?IV",
}


def num(value: object) -> float:
    text = str(value).strip()
    if not text or text.lower().startswith(("not ", "unclear", "no sd")):
        return math.nan
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace("%", ""))
    if not match:
        return math.nan
    result = float(match.group(0))
    return result * 100.0 if 0 < result <= 1.5 else result


def task_label(row: pd.Series) -> str:
    dataset = str(row.get("dataset_name", "")).upper()
    if re.search(DATASETS["SEED-IV"], dataset, flags=re.IGNORECASE):
        return "SEED-IV | 4-class"
    if re.search(DATASETS["SEED"], dataset, flags=re.IGNORECASE):
        return "SEED | 3-class"
    return "Other"


def subject_count(row: pd.Series) -> float:
    for column in ("n_subjects", "n_folds"):
        value = num(row.get(column, ""))
        if np.isfinite(value) and value > 1:
            return value
    return math.nan


def stratum_label(row: pd.Series) -> str:
    protocol = str(row.get("protocol_category", "")).lower()
    target = str(row.get("target_data_used", "")).lower()
    labels = str(row.get("target_labels_used", "")).lower()
    split = str(row.get("split_type", "")).lower()
    adapt = str(row.get("adaptation_method", "")).lower()
    combined = " ".join((protocol, target, labels, split, adapt))
    if (
        protocol.strip().startswith("f")
        or labels.startswith("yes")
        or "limited target label" in labels
        or "labeled+unlabeled target" in target
    ):
        return "few-shot/target-label"
    if (
        protocol.strip().startswith("b")
        or "transductive" in protocol
        or "uda" in protocol
        or "source-free" in protocol
        or "unlabeled target" in target
        or target.startswith("yes")
    ):
        return "transductive-UDA"
    if (
        protocol.strip().startswith("a")
        or "inductive" in protocol
        or "no-target" in protocol
        or "no target" in target
        or "domain generalization" in combined
        or "loso" in split
        or "subject-independent" in split
    ):
        return "inductive/no-target"
    return "unclear"


def method_family(row: pd.Series) -> str:
    text = " ".join(str(row.get(c, "")).lower() for c in ("model_family", "feature_type"))
    if any(token in text for token in ("graph", "gcn", "gat", "gnn", "topolog")):
        return "graph/GNN"
    if any(token in text for token in ("transformer", "attention", "vit")):
        return "transformer/attention"
    if any(token in text for token in ("cnn", "rnn", "lstm", "gru", "capsule", "capsnet", "mamba", "state-space")):
        return "CNN/RNN/state-space"
    if any(token in text for token in ("svm", "knn", "lda", "traditional", "dictionary", "riemann", "tangent")):
        return "classical/shallow"
    if any(token in text for token in ("mlp", "dnn", "autoencoder", "deep")):
        return "other deep"
    return "unspecified/hybrid"


def generalization_mechanism(row: pd.Series) -> str:
    text = " ".join(str(row.get(c, "")).lower() for c in ("model_family", "adaptation_method", "feature_type"))
    if any(token in text for token in ("few-shot", "semi-supervised", "calibration")):
        return "target-supervised calibration"
    if any(token in text for token in ("pretrain", "fine-tun", "foundation")):
        return "pretraining/fine-tuning"
    if any(token in text for token in ("domain general", "source-free")):
        return "domain generalization/source-free"
    if any(token in text for token in ("contrastive", "self-supervised", "ssl")):
        return "contrastive/self-supervised"
    if any(token in text for token in ("domain", "adaptation", "adversarial", "mmd", "coral", "transfer")):
        return "domain adaptation/discrepancy"
    return "source-only/other"


def confidence_label(k: int) -> str:
    if k < 3:
        return "insufficient"
    if k < 5:
        return "very low"
    if k < 10:
        return "low"
    return "low"


def matched_case_series() -> dict[str, object]:
    data = pd.read_csv(MATCHED_INPUT)
    numeric = ["target_access_accuracy", "no_target_accuracy", "difference_pp"]
    for column in numeric:
        data[column] = pd.to_numeric(data[column], errors="raise")

    recomputed = data["target_access_accuracy"] - data["no_target_accuracy"]
    if not np.allclose(recomputed, data["difference_pp"], atol=0.005):
        raise ValueError("A stored matched difference does not equal the two arm values")

    data.to_csv(OUTPUT / "matched_target_access_contrasts.csv", index=False)

    study_summary = (
        data.groupby(["paper_id", "citation_key", "study_title"], as_index=False)
        .agg(
            n_reported_contrasts=("difference_pp", "size"),
            mean_difference_pp=("difference_pp", "mean"),
            median_difference_pp=("difference_pp", "median"),
            min_difference_pp=("difference_pp", "min"),
            max_difference_pp=("difference_pp", "max"),
        )
    )
    for column in study_summary.columns[4:]:
        study_summary[column] = study_summary[column].round(2)
    study_summary.to_csv(OUTPUT / "matched_target_access_study_summary.csv", index=False)

    summary = {
        "analysis": "post-review matched descriptive case series",
        "eligible_studies": int(data["paper_id"].nunique()),
        "reported_contrasts": int(len(data)),
        "positive_contrasts": int((data["difference_pp"] > 0).sum()),
        "contrast_median_difference_pp": round(float(data["difference_pp"].median()), 2),
        "contrast_min_difference_pp": round(float(data["difference_pp"].min()), 2),
        "contrast_max_difference_pp": round(float(data["difference_pp"].max()), 2),
        "study_mean_min_pp": round(float(study_summary["mean_difference_pp"].min()), 2),
        "study_mean_max_pp": round(float(study_summary["mean_difference_pp"].max()), 2),
        "pooled_effect": None,
        "reason_not_pooled": (
            "Only two eligible studies were found; multiple contrasts within each study are dependent, "
            "and paired subject-level covariance was unavailable."
        ),
    }
    (OUTPUT / "matched_target_access_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def method_by_protocol() -> pd.DataFrame:
    master = pd.read_csv(MASTER, dtype=str, keep_default_na=False)
    meta = master[
        master["include_meta"].str.lower().eq("yes")
        & master["metric"].str.contains("acc|accuracy", case=False, regex=True, na=False)
    ].copy()
    meta["effect"] = meta["result_mean"].map(num)
    meta["sd"] = meta["result_sd"].map(num)
    meta["n"] = meta.apply(subject_count, axis=1)
    meta = meta[
        meta["effect"].notna()
        & meta["sd"].notna()
        & meta["sd"].gt(0)
        & meta["n"].notna()
        & meta["n"].gt(1)
    ].copy()
    meta["task"] = meta.apply(task_label, axis=1)
    meta["stratum"] = meta.apply(stratum_label, axis=1)
    meta["method_family_group"] = meta.apply(method_family, axis=1)
    meta["generalization_mechanism"] = meta.apply(generalization_mechanism, axis=1)
    selected = meta[meta["task"].isin(["SEED | 3-class", "SEED-IV | 4-class"])].copy()

    rows: list[dict[str, object]] = []
    for (task, protocol, family), group in selected.groupby(
        ["task", "stratum", "method_family_group"], dropna=False
    ):
        k = int(group["paper_id"].nunique())
        values = group.groupby("paper_id", as_index=False)["effect"].first()["effect"]
        rows.append(
            {
                "dataset_task": task,
                "target_access_protocol": protocol,
                "method_family": family,
                "k": k,
                "median_accuracy": round(float(values.median()), 2),
                "min_accuracy": round(float(values.min()), 2),
                "max_accuracy": round(float(values.max()), 2),
                "evidence_confidence": confidence_label(k),
                "interpretation": "descriptive coverage only; not a controlled architecture comparison",
            }
        )

    output = pd.DataFrame(rows).sort_values(
        ["dataset_task", "target_access_protocol", "method_family"]
    )
    output.to_csv(OUTPUT / "method_family_by_protocol.csv", index=False)

    mechanism_rows: list[dict[str, object]] = []
    for (task, protocol, mechanism), group in selected.groupby(
        ["task", "stratum", "generalization_mechanism"], dropna=False
    ):
        k = int(group["paper_id"].nunique())
        values = group.groupby("paper_id", as_index=False)["effect"].first()["effect"]
        mechanism_rows.append(
            {
                "dataset_task": task,
                "target_access_protocol": protocol,
                "generalization_mechanism": mechanism,
                "k": k,
                "median_accuracy": round(float(values.median()), 2),
                "min_accuracy": round(float(values.min()), 2),
                "max_accuracy": round(float(values.max()), 2),
                "evidence_confidence": confidence_label(k),
                "interpretation": "descriptive coverage only; mechanisms are not exchangeable interventions",
            }
        )
    pd.DataFrame(mechanism_rows).sort_values(
        ["dataset_task", "target_access_protocol", "generalization_mechanism"]
    ).to_csv(OUTPUT / "generalization_mechanism_by_protocol.csv", index=False)
    return output


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    matched = matched_case_series()
    method = method_by_protocol()
    manifest = {
        "matched_target_access": matched,
        "method_protocol_rows": int(len(method)),
        "method_protocol_output": (OUTPUT / "method_family_by_protocol.csv").relative_to(ROOT).as_posix(),
        "mechanism_protocol_output": (OUTPUT / "generalization_mechanism_by_protocol.csv").relative_to(ROOT).as_posix(),
    }
    (OUTPUT / "reviewer_revision_analysis_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
