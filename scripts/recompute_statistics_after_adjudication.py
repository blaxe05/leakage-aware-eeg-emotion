from __future__ import annotations

import json
import math
import re
from collections import Counter, OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
EXTRACTION = ROOT / "04_extraction" / "extraction_master.csv"
META_QUEUE = ROOT / "04_extraction" / "reviewer_meta_extraction_review" / "reviewer_meta_adjudication_queue_20260704.csv"
META_TEMPLATE = ROOT / "04_extraction" / "reviewer_meta_extraction_review" / "reviewer_meta_extraction_template_blinded.csv"
SCREEN_BASE = ROOT / "03_screening" / "reviewer_screening_777_records" / "reviewer_title_abstract_screening_blinded.csv"
SCREEN_H2 = ROOT / "03_screening" / "reviewer_screening_777_records" / "reviewer_screening_disagreements_for_adjudicator_20260704.csv"
SCREEN_CONSENSUS = ROOT / "03_screening" / "reviewer_screening_777_records" / "screening_consensus_after_adjudication_20260704.csv"

OUT = ROOT / "07_meta_analysis"
META_RESULTS = OUT / "meta_results.csv"
META_DIAG = OUT / "meta_diagnostics.csv"
META_MD = OUT / "meta_results.md"
MOD_RESULTS = OUT / "moderator_analysis.csv"
MOD_DIAG = OUT / "moderator_diagnostics.csv"
DATASET_COUNTS = OUT / "dataset_included_counts.csv"
SUMMARY_JSON = OUT / "statistics_summary_20260704.json"
APPLIED_AUDIT = OUT / "adjudicator_meta_decisions_applied_20260704.csv"


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


TASK_ORDER = [
    "AMIGOS | valence (binary)",
    "DEAP | arousal (binary)",
    "DEAP | binary",
    "DEAP | valence (binary)",
    "DREAMER | arousal (binary)",
    "DREAMER | binary",
    "DREAMER | valence (binary)",
    "FACED | multi",
    "GAMEEMO | binary",
    "MPED | 7-class",
    "SEED | 3-class",
    "SEED-IV | 4-class",
    "SEED-V | 5-class",
    "SEED-VII",
]

STRATUM_ORDER = [
    "inductive/no-target",
    "transductive-UDA",
    "few-shot/target-label",
    "cross-dataset",
    "unclear",
]


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")


def num(value: object) -> float:
    if value is None:
        return math.nan
    s = str(value).strip()
    low = s.lower()
    if not s or low in {"na", "n/a", "none", "not reported", "not verified", "unclear"}:
        return math.nan
    if low.startswith(("not reported", "not verified", "not separately", "unclear", "no sd", "not captured")):
        return math.nan
    s = s.replace("%", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return math.nan
    v = float(m.group(0))
    if 0 < v <= 1.5:
        v *= 100.0
    return v


def close_num(a: object, b: object, tol: float = 0.08) -> bool:
    aa, bb = num(a), num(b)
    return np.isfinite(aa) and np.isfinite(bb) and abs(aa - bb) <= tol


def yes_exact(value: object) -> bool:
    return str(value).strip().lower() == "yes"


def starts_yes(value: object) -> bool:
    return str(value).strip().lower().startswith("yes")


def risk_to_master(value: str) -> str:
    s = str(value).strip().lower()
    if s in {"low", "low-some"}:
        return s
    if s in {"moderate", "some concerns", "some-concerns"}:
        return "some-concerns"
    if s in {"high", "unclear"}:
        return s
    return str(value).strip() or "unclear"


def risk_bucket(value: object) -> str:
    s = str(value).strip().lower()
    if "high" in s or "unclear" in s:
        return "high/unclear"
    if "some" in s or "moderate" in s:
        return "some-concerns"
    if "low" in s:
        return "low/low-some"
    return "unclassified"


def dataset_mask(series: pd.Series, dataset: str) -> pd.Series:
    return series.fillna("").str.contains(DATASETS[dataset], flags=re.IGNORECASE, regex=True)


def as_int_subjects(row: pd.Series) -> float:
    for col in ("n_subjects", "n_folds"):
        v = num(row.get(col, ""))
        if np.isfinite(v) and v > 1:
            return v
    return math.nan


def normalize_class_text(row: pd.Series) -> str:
    return " ".join(str(row.get(c, "")) for c in ("dataset_name", "emotion_model", "class_labels")).lower()


def task_label(row: pd.Series) -> str:
    d = str(row.get("dataset_name", "")).upper()
    t = normalize_class_text(row)
    if re.search(DATASETS["SEED-IV"], d, flags=re.IGNORECASE):
        return "SEED-IV | 4-class"
    if re.search(DATASETS["SEED-VII"], d, flags=re.IGNORECASE):
        return "SEED-VII"
    if re.search(DATASETS["SEED-V"], d, flags=re.IGNORECASE):
        return "SEED-V | 5-class"
    if re.search(DATASETS["SEED"], d, flags=re.IGNORECASE):
        return "SEED | 3-class"
    if "DEAP" in d:
        if "arousal" in t:
            return "DEAP | arousal (binary)"
        if "valence" in t:
            return "DEAP | valence (binary)"
        return "DEAP | binary"
    if "DREAMER" in d:
        if "arousal" in t:
            return "DREAMER | arousal (binary)"
        if "valence" in t:
            return "DREAMER | valence (binary)"
        return "DREAMER | binary"
    if "AMIGOS" in d:
        if "arousal" in t:
            return "AMIGOS | arousal (binary)"
        if "valence" in t:
            return "AMIGOS | valence (binary)"
        return "AMIGOS | binary"
    if "FACED" in d:
        return "FACED | multi"
    if "MPED" in d:
        return "MPED | 7-class"
    if "GAMEEMO" in d:
        return "GAMEEMO | binary"
    if "MAHNOB" in d:
        if "arousal" in t:
            return "MAHNOB-HCI | arousal (binary)"
        if "valence" in t:
            return "MAHNOB-HCI | valence (binary)"
        return "MAHNOB-HCI | binary"
    return str(row.get("dataset_name", "")).strip() or "Other"


def stratum_label(row: pd.Series) -> str:
    text = " ".join(
        str(row.get(c, "")).lower()
        for c in (
            "protocol_category",
            "adaptation_method",
            "target_data_used",
            "target_labels_used",
            "leakage_categories",
            "ambiguity_notes",
            "split_type",
        )
    )
    labels = str(row.get("target_labels_used", "")).lower()
    target = str(row.get("target_data_used", "")).lower()
    protocol = str(row.get("protocol_category", "")).lower()
    adapt = str(row.get("adaptation_method", "")).lower()
    split = str(row.get("split_type", "")).lower()

    target_label_protocol = protocol.strip().startswith("f") or "few-shot/target-label" in protocol
    target_label_field = labels.startswith("yes") or "limited target label" in labels or "few-shot target" in labels
    target_label_data = "labeled+unlabeled target" in target or re.search(r"(?<!un)labeled target", target) is not None
    if target_label_field or target_label_data or target_label_protocol:
        return "few-shot/target-label"
    explicit_transductive = (
        protocol.strip().startswith("b")
        or "transductive" in protocol
        or "uda" in protocol
        or "source-free" in protocol
        or "test-time" in protocol
        or "unlabeled target" in target
        or target.startswith("yes")
    )
    if explicit_transductive:
        return "transductive-UDA"
    if "cross-dataset" in text:
        return "cross-dataset"
    explicit_inductive = (
        protocol.strip().startswith("a")
        or "inductive" in protocol
        or "no-target" in protocol
        or "no target" in target
        or "domain generalization" in text
        or "loso" in split
        or "subject-independent" in split
    )
    if explicit_inductive:
        return "inductive/no-target"
    if "domain adaptation" in adapt and "no domain adaptation" not in adapt:
        return "transductive-UDA"
    return "unclear"


def method_family(row: pd.Series) -> str:
    text = " ".join(str(row.get(c, "")).lower() for c in ("model_family", "adaptation_method", "feature_type"))
    if any(x in text for x in ("graph", "gcn", "gat", "gnn", "topolog")):
        return "graph/GNN"
    if any(x in text for x in ("domain", "adaptation", "adversarial", "mmd", "coral", "transfer")):
        return "domain-adversarial/DA"
    if any(x in text for x in ("contrastive", "self-supervised", "ssl")):
        return "contrastive/SSL"
    if any(x in text for x in ("transformer", "attention", "vit")):
        return "transformer/attn"
    if any(x in text for x in ("cnn", "rnn", "lstm", "gru", "capsule", "capsnet")):
        return "CNN/RNN/capsule"
    if any(x in text for x in ("svm", "knn", "lda", "traditional", "entropy", "dictionary", "tpt")):
        return "traditional ML"
    return "other/DL"


def add_note(existing: str, note: str) -> str:
    existing = str(existing).strip()
    note = str(note).strip()
    if not note:
        return existing
    if not existing:
        return note
    if note in existing:
        return existing
    return f"{existing}; {note}"


def template_to_master_row(template_row: pd.Series, base_row: pd.Series, columns: list[str]) -> dict[str, str]:
    row = {col: str(base_row.get(col, "")) if base_row is not None else "" for col in columns}
    direct = [
        "paper_id",
        "title",
        "dataset_name",
        "n_subjects",
        "n_sessions",
        "eeg_channels",
        "sampling_rate_hz",
        "emotion_model",
        "class_labels",
        "class_balance",
        "preproc_in_cv",
        "model_family",
        "adaptation_method",
        "target_data_used",
        "target_labels_used",
        "subject_independent",
        "split_type",
        "n_folds",
        "cross_setting",
        "train_val_test_separation",
        "model_selection_strategy",
        "metric",
        "result_mean",
        "result_sd",
        "result_ci",
        "per_subject_reported",
        "statistical_test",
        "mean_or_best",
        "protocol_category",
        "leakage_categories",
        "risk_rating",
        "risk_evidence",
        "ambiguity_notes",
        "include_meta",
        "primary_result",
        "verification_status",
        "source_checked",
    ]
    for col in direct:
        if col in row and col in template_row.index:
            row[col] = str(template_row.get(col, ""))
    if "include_narrative" in row:
        row["include_narrative"] = "yes"
    if row.get("dataset_name") == "SEED":
        row["dataset_link"] = "https://bcmi.sjtu.edu.cn/home/seed/seed.html"
        row["stimulus_type"] = "film clips"
        row["emotion_model"] = row.get("emotion_model") or "discrete-3class"
    elif row.get("dataset_name") == "SEED-IV":
        row["dataset_link"] = "https://weilongzheng.github.io/datasets/seed-iv/"
        row["stimulus_type"] = "movie clips"
        row["emotion_model"] = row.get("emotion_model") or "discrete-4class"
    row["source_checked"] = add_note(row.get("source_checked", ""), "row added from completed consensus adjudication queue 2026-07-04")
    return row


def choose_master_index(master: pd.DataFrame, decision: pd.Series) -> int | None:
    candidates = master[
        master["paper_id"].eq(decision["paper_id"])
        & master["dataset_name"].str.lower().eq(str(decision["dataset_name"]).lower())
    ].copy()
    if candidates.empty:
        return None

    def score(idx: int, row: pd.Series) -> tuple[int, int, int, int]:
        s_mean = int(close_num(row.get("result_mean", ""), decision.get("result_mean", "")) or close_num(row.get("result_mean", ""), decision.get("adjudicator_result_mean", "")))
        s_meta = int(starts_yes(row.get("include_meta", "")))
        h2_dec = str(decision.get("adjudicator_protocol_audit_decision", "")).lower()
        s_protocol = int(not ("cross-dataset" in str(row.get("protocol_category", "")).lower() and "cross-subject" in h2_dec))
        s_metric = int(str(row.get("metric", "")).lower().startswith(str(decision.get("metric", "")).lower()))
        return (s_mean, s_meta, s_protocol, s_metric)

    ranked = sorted(((score(idx, row), idx) for idx, row in candidates.iterrows()), reverse=True)
    return ranked[0][1]


def apply_adjudicator_meta(master: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    decisions = read_csv(META_QUEUE)
    template = read_csv(META_TEMPLATE)
    columns = list(master.columns)
    audit_rows: list[dict[str, str]] = []

    for _, dec in decisions.iterrows():
        idx = choose_master_index(master, dec)
        action = "updated"
        if idx is None:
            base_matches = master[master["paper_id"].eq(dec["paper_id"])]
            base_row = base_matches.iloc[0] if not base_matches.empty else pd.Series(dtype=str)
            template_matches = template[
                template["reviewer_row_id"].eq(dec["reviewer_row_id"])
                | (template["paper_id"].eq(dec["paper_id"]) & template["dataset_name"].eq(dec["dataset_name"]))
            ]
            template_row = template_matches.iloc[0] if not template_matches.empty else dec
            new_row = template_to_master_row(template_row, base_row, columns)
            master = pd.concat([master, pd.DataFrame([new_row], columns=columns)], ignore_index=True)
            idx = int(master.index[-1])
            action = "added"

        before = master.loc[idx].to_dict()
        h2_include = str(dec.get("adjudicator_include_meta", "")).strip().lower()
        h2_primary = str(dec.get("adjudicator_primary_result", "")).strip().lower()
        h2_decision = str(dec.get("adjudicator_protocol_audit_decision", "")).strip().lower()
        h2_target = str(dec.get("adjudicator_target_access_verified", "")).strip().lower()
        h2_risk = risk_to_master(dec.get("adjudicator_risk_rating", ""))
        h2_notes = str(dec.get("adjudicator_notes", "")).strip()
        h2_source = str(dec.get("adjudicator_source_location", "")).strip()

        master.at[idx, "result_mean"] = str(dec.get("adjudicator_result_mean", "") or dec.get("result_mean", "")).strip()
        master.at[idx, "result_sd"] = str(dec.get("adjudicator_result_sd", "") or dec.get("result_sd", "")).strip()
        master.at[idx, "include_meta"] = "yes" if h2_include == "yes" else "no"
        if h2_primary in {"yes", "no"}:
            master.at[idx, "primary_result"] = h2_primary
        if h2_risk:
            master.at[idx, "risk_rating"] = h2_risk
        master.at[idx, "risk_evidence"] = add_note(master.at[idx, "risk_evidence"], f"Adjudicator: {h2_source}")
        master.at[idx, "ambiguity_notes"] = add_note(master.at[idx, "ambiguity_notes"], f"Adjudicator decision={h2_decision}; {h2_notes}")
        master.at[idx, "source_checked"] = add_note(master.at[idx, "source_checked"], "adjudicator decision applied 2026-07-04")

        target_text = f"{h2_target} {h2_notes.lower()}"
        if "target-label" in target_text or "labeled target" in target_text or h2_decision == "reclassify":
            master.at[idx, "target_data_used"] = "labeled+unlabeled target (few-shot/target-label; adjudicated)"
            master.at[idx, "target_labels_used"] = "yes (limited target labels; adjudicated)"
            master.at[idx, "protocol_category"] = "F (few-shot/target-label; adjudicated)"
            master.at[idx, "leakage_categories"] = "none (target-label use disclosed)"
        elif "unlabeled" in target_text or h2_decision == "pool-with-cross-subject":
            master.at[idx, "target_data_used"] = "yes (unlabeled target data; adjudicated)"
            master.at[idx, "target_labels_used"] = "no (unlabeled target only; adjudicated)"
            master.at[idx, "protocol_category"] = "B (transductive-UDA; adjudicated)"
            master.at[idx, "leakage_categories"] = "none (transductive disclosed)"

        if h2_decision == "exclude-from-cross-subject-meta":
            master.at[idx, "include_meta"] = "no"
            if "duplicate" in h2_notes.lower() or "preprint" in h2_notes.lower():
                master.at[idx, "include_narrative"] = "no"
                master.at[idx, "protocol_category"] = add_note(master.at[idx, "protocol_category"], "duplicate-not-retained")
            else:
                master.at[idx, "include_narrative"] = "yes"
                if "validation" in h2_notes.lower() or h2_risk == "high":
                    master.at[idx, "target_data_used"] = "unclear (held-out target may influence validation/model selection)"
                    master.at[idx, "target_labels_used"] = "unclear (possible target-label/model-selection leakage)"
                    master.at[idx, "protocol_category"] = "ambiguous/high-risk semi-supervised LOSO"
                    master.at[idx, "leakage_categories"] = "possible target-label/model-selection leakage"
        elif h2_decision == "narrative-only":
            master.at[idx, "include_meta"] = "no"
            master.at[idx, "include_narrative"] = "yes"

        after = master.loc[idx].to_dict()
        audit_rows.append(
            {
                "action": action,
                "row_index": str(idx),
                "reviewer_row_id": dec.get("reviewer_row_id", ""),
                "paper_id": dec.get("paper_id", ""),
                "dataset_name": dec.get("dataset_name", ""),
                "before_include_meta": before.get("include_meta", ""),
                "after_include_meta": after.get("include_meta", ""),
                "before_include_narrative": before.get("include_narrative", ""),
                "after_include_narrative": after.get("include_narrative", ""),
                "before_result": f"{before.get('result_mean', '')}/{before.get('result_sd', '')}",
                "after_result": f"{after.get('result_mean', '')}/{after.get('result_sd', '')}",
                "after_protocol_category": after.get("protocol_category", ""),
                "after_risk_rating": after.get("risk_rating", ""),
                "adjudicator_decision": dec.get("adjudicator_protocol_audit_decision", ""),
                "adjudicator_notes": dec.get("adjudicator_notes", ""),
            }
        )

    return master[columns], pd.DataFrame(audit_rows)


def prep_meta_data(master: pd.DataFrame) -> pd.DataFrame:
    d = master[master["include_meta"].str.lower().eq("yes")].copy()
    d = d[d["metric"].str.contains("acc|accuracy", case=False, regex=True, na=False)].copy()
    d["effect"] = d["result_mean"].map(num)
    d["sd"] = d["result_sd"].map(num)
    d["n"] = d.apply(as_int_subjects, axis=1)
    d = d[d["effect"].notna() & d["sd"].notna() & d["n"].notna() & d["n"].gt(1)].copy()
    d["se"] = d["sd"] / np.sqrt(d["n"])
    d = d[d["se"].gt(0) & np.isfinite(d["se"])].copy()
    d["task"] = d.apply(task_label, axis=1)
    d["stratum"] = d.apply(stratum_label, axis=1)
    d["method_family_group"] = d.apply(method_family, axis=1)
    d["risk_group"] = d["risk_rating"].map(risk_bucket)
    d["year_num"] = pd.to_numeric(d["year"], errors="coerce")
    d["code_group"] = np.where(
        d["code_repo"].str.contains("github|gitlab|http", case=False, regex=True, na=False)
        & ~d["code_repo"].str.contains("none|not verified|NA", case=False, regex=True, na=False),
        "code",
        "no-code",
    )
    return d


def dl_pool(d: pd.DataFrame) -> dict[str, float]:
    y = d["effect"].astype(float).to_numpy()
    se = d["se"].astype(float).to_numpy()
    v = se**2
    k = len(y)
    if k == 0:
        return {}
    if k == 1:
        return {
            "k": 1,
            "DL_mean": y[0],
            "DL_ci_lo": math.nan,
            "DL_ci_hi": math.nan,
            "HK_ci_lo": math.nan,
            "HK_ci_hi": math.nan,
            "I2": math.nan,
            "tau": math.nan,
            "tau2": math.nan,
            "Q": math.nan,
            "Q_df": math.nan,
            "Q_p": math.nan,
            "PI_lo": math.nan,
            "PI_hi": math.nan,
        }
    w = 1.0 / v
    fixed = float(np.sum(w * y) / np.sum(w))
    q = float(np.sum(w * (y - fixed) ** 2))
    df = k - 1
    c = float(np.sum(w) - np.sum(w**2) / np.sum(w))
    tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0
    wr = 1.0 / (v + tau2)
    mu = float(np.sum(wr * y) / np.sum(wr))
    se_mu = float(math.sqrt(1.0 / np.sum(wr)))
    dl_lo, dl_hi = mu - 1.96 * se_mu, mu + 1.96 * se_mu
    hk_q = float(np.sum(wr * (y - mu) ** 2) / df)
    hk_se = float(math.sqrt(max(hk_q, 0.0) / np.sum(wr)))
    tcrit = float(stats.t.ppf(0.975, df))
    hk_lo, hk_hi = mu - tcrit * hk_se, mu + tcrit * hk_se
    i2 = max(0.0, (q - df) / q) * 100.0 if q > 0 else 0.0
    q_p = float(stats.chi2.sf(q, df))
    pi_se = math.sqrt(tau2 + se_mu**2)
    pi_lo, pi_hi = mu - 1.96 * pi_se, mu + 1.96 * pi_se
    return {
        "k": k,
        "DL_mean": mu,
        "DL_ci_lo": dl_lo,
        "DL_ci_hi": dl_hi,
        "HK_ci_lo": hk_lo,
        "HK_ci_hi": hk_hi,
        "I2": i2,
        "tau": math.sqrt(tau2),
        "tau2": tau2,
        "Q": q,
        "Q_df": df,
        "Q_p": q_p,
        "PI_lo": pi_lo,
        "PI_hi": pi_hi,
    }


def logit_sensitivity(d: pd.DataFrame) -> float:
    p = np.clip(d["effect"].astype(float).to_numpy() / 100.0, 1e-4, 1 - 1e-4)
    se_p = d["se"].astype(float).to_numpy() / 100.0
    yi = np.log(p / (1 - p))
    sei = se_p / (p * (1 - p))
    tmp = pd.DataFrame({"effect": yi, "se": sei})
    pooled = dl_pool(tmp)
    if not pooled:
        return math.nan
    q = math.exp(pooled["DL_mean"]) / (1 + math.exp(pooled["DL_mean"]))
    return q * 100.0


def leave_one_out_range(d: pd.DataFrame) -> tuple[float, float]:
    if len(d) <= 1:
        return (math.nan, math.nan)
    vals = []
    for idx in d.index:
        pooled = dl_pool(d.drop(index=idx))
        if pooled:
            vals.append(pooled["DL_mean"])
    if not vals:
        return (math.nan, math.nan)
    return (float(min(vals)), float(max(vals)))


def maturity_label(k: int, i2: float) -> str:
    if k < 3:
        return "narrative only"
    if k <= 3:
        return "fragile (k=3, very high I2)" if i2 >= 75 else "fragile"
    if k < 10:
        return "moderate"
    if i2 >= 75:
        return "moderate (high I2)"
    return "moderate"


def fmt_float(value: float, digits: int = 2) -> str:
    if value is None or not np.isfinite(value):
        return ""
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def compute_meta_results(d: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    diag_rows = []
    for (task, stratum), g in d.groupby(["task", "stratum"], sort=False):
        g = g.sort_values("effect")
        pooled = dl_pool(g)
        studies = ";".join(f"{r.paper_id}({r.effect:.1f}/{r.sd:.1f})" for r in g.itertuples())
        k = int(pooled.get("k", len(g)))
        loo_lo, loo_hi = leave_one_out_range(g)
        logit_mean = logit_sensitivity(g) if k >= 2 else math.nan
        row = {
            "task": task,
            "stratum": stratum,
            "k": k,
            "DL_mean": fmt_float(pooled.get("DL_mean", math.nan), 2) if k >= 3 else "",
            "DL_ci_lo": fmt_float(pooled.get("DL_ci_lo", math.nan), 2) if k >= 3 else "",
            "DL_ci_hi": fmt_float(pooled.get("DL_ci_hi", math.nan), 2) if k >= 3 else "",
            "HK_ci_lo": fmt_float(pooled.get("HK_ci_lo", math.nan), 2) if k >= 3 else "",
            "HK_ci_hi": fmt_float(pooled.get("HK_ci_hi", math.nan), 2) if k >= 3 else "",
            "I2": fmt_float(pooled.get("I2", math.nan), 1) if k >= 3 else "",
            "tau": fmt_float(pooled.get("tau", math.nan), 2) if k >= 3 else "",
            "logit_mean": fmt_float(logit_mean, 2) if k >= 3 else "",
            "LOO_lo": fmt_float(loo_lo, 2) if k >= 3 else "",
            "LOO_hi": fmt_float(loo_hi, 2) if k >= 3 else "",
            "maturity": maturity_label(k, pooled.get("I2", math.nan)),
            "studies": studies,
            "tau2": fmt_float(pooled.get("tau2", math.nan), 4) if k >= 3 else "",
            "Q": fmt_float(pooled.get("Q", math.nan), 4) if k >= 3 else "",
            "Q_df": fmt_float(pooled.get("Q_df", math.nan), 0) if k >= 3 else "",
            "Q_p": fmt_float(pooled.get("Q_p", math.nan), 4) if k >= 3 else "",
            "PI_lo": fmt_float(pooled.get("PI_lo", math.nan), 4) if k >= 3 else "",
            "PI_hi": fmt_float(pooled.get("PI_hi", math.nan), 4) if k >= 3 else "",
        }
        rows.append(row)
        if k >= 3:
            diag_rows.append(
                {
                    "task": task,
                    "stratum": stratum,
                    "k": k,
                    "DL_mean": row["DL_mean"],
                    "tau": row["tau"],
                    "tau2": row["tau2"],
                    "I2": row["I2"],
                    "Q": row["Q"],
                    "Q_df": row["Q_df"],
                    "Q_p": row["Q_p"],
                    "PI_lo": row["PI_lo"],
                    "PI_hi": row["PI_hi"],
                }
            )

    out = pd.DataFrame(rows)
    out["task_order"] = out["task"].map({v: i for i, v in enumerate(TASK_ORDER)}).fillna(999).astype(int)
    out["stratum_order"] = out["stratum"].map({v: i for i, v in enumerate(STRATUM_ORDER)}).fillna(999).astype(int)
    out = out.sort_values(["task_order", "stratum_order", "task", "stratum"]).drop(columns=["task_order", "stratum_order"])
    diag = pd.DataFrame(diag_rows)
    return out, diag


def subgroup_row(d: pd.DataFrame, analysis: str, level: str) -> dict[str, str]:
    pooled = dl_pool(d)
    k = int(pooled.get("k", len(d)))
    if k < 2:
        return {"analysis": analysis, "level": level, "k": k, "pooled": "", "ci_lo": "", "ci_hi": "", "I2": ""}
    return {
        "analysis": analysis,
        "level": level,
        "k": k,
        "pooled": fmt_float(pooled["DL_mean"], 2),
        "ci_lo": fmt_float(pooled["DL_ci_lo"], 2),
        "ci_hi": fmt_float(pooled["DL_ci_hi"], 2),
        "I2": fmt_float(pooled["I2"], 0),
    }


def wls_slope(d: pd.DataFrame) -> tuple[float, float, int]:
    d = d[d["year_num"].notna()].copy()
    if len(d) < 3:
        return (math.nan, math.nan, len(d))
    pooled = dl_pool(d)
    tau2 = pooled.get("tau2", 0.0) if pooled else 0.0
    x = d["year_num"].astype(float).to_numpy()
    y = d["effect"].astype(float).to_numpy()
    w = 1.0 / (d["se"].astype(float).to_numpy() ** 2 + tau2)
    x0 = x - x.mean()
    X = np.column_stack([np.ones_like(x0), x0])
    XtW = X.T * w
    beta = np.linalg.inv(XtW @ X) @ (XtW @ y)
    resid = y - X @ beta
    df = len(d) - 2
    sigma2 = float(np.sum(w * resid**2) / df)
    cov = sigma2 * np.linalg.inv(XtW @ X)
    return (float(beta[1]), float(math.sqrt(cov[1, 1])), len(d))


def compute_moderators(d: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for task, name in [("SEED | 3-class", "SEED-3"), ("SEED-IV | 4-class", "SEED-IV")]:
        td = d[d["task"].eq(task)]
        for stratum, level in [
            ("few-shot/target-label", "few-shot"),
            ("inductive/no-target", "inductive"),
            ("transductive-UDA", "transductive"),
            ("unclear", "unclear"),
        ]:
            rows.append(subgroup_row(td[td["stratum"].eq(stratum)], f"{name} by adaptation setting", level))
        for level in ["CNN/RNN/capsule", "contrastive/SSL", "domain-adversarial/DA", "graph/GNN", "other/DL", "traditional ML", "transformer/attn"]:
            g = td[td["method_family_group"].eq(level)]
            if len(g):
                rows.append(subgroup_row(g, f"{name} by method family", level))
        for level in ["low/low-some", "some-concerns", "high/unclear"]:
            g = td[td["risk_group"].eq(level)]
            if len(g):
                rows.append(subgroup_row(g, f"{name} by leakage risk", level))
        if task == "SEED | 3-class":
            for level in ["code", "no-code"]:
                g = td[td["code_group"].eq(level)]
                if len(g):
                    rows.append(subgroup_row(g, f"{name} by reproducibility", level))

    deap = d[d["task"].str.startswith("DEAP")]
    for stratum, level in [
        ("few-shot/target-label", "few-shot"),
        ("inductive/no-target", "inductive"),
        ("transductive-UDA", "transductive"),
        ("unclear", "unclear"),
    ]:
        rows.append(subgroup_row(deap[deap["stratum"].eq(stratum)], "DEAP by adaptation setting", level))

    seed = d[d["task"].eq("SEED | 3-class")]
    for subset, label in [(seed, "SEED-3 all acc~year"), (seed[seed["stratum"].eq("transductive-UDA")], "SEED-3 transductive acc~year")]:
        slope, se, k = wls_slope(subset)
        rows.append(
            {
                "analysis": "meta-reg",
                "level": label,
                "k": k,
                "pooled": fmt_float(slope, 3),
                "ci_lo": fmt_float(se, 3),
                "ci_hi": "slope_pts_per_year",
                "I2": "",
            }
        )

    mod = pd.DataFrame(rows)

    def pooled_value(task: str, stratum: str) -> float:
        m = meta[(meta["task"].eq(task)) & (meta["stratum"].eq(stratum))]
        if m.empty or not str(m.iloc[0]["DL_mean"]).strip():
            return math.nan
        return float(m.iloc[0]["DL_mean"])

    seed_i = pooled_value("SEED | 3-class", "inductive/no-target")
    seed_t = pooled_value("SEED | 3-class", "transductive-UDA")
    siv_i = pooled_value("SEED-IV | 4-class", "inductive/no-target")
    siv_t = pooled_value("SEED-IV | 4-class", "transductive-UDA")
    low_seed = mod[(mod["analysis"].eq("SEED-3 by leakage risk")) & (mod["level"].eq("low/low-some"))]
    some_seed = mod[(mod["analysis"].eq("SEED-3 by leakage risk")) & (mod["level"].eq("some-concerns"))]
    code = mod[(mod["analysis"].eq("SEED-3 by reproducibility")) & (mod["level"].eq("code"))]
    nocode = mod[(mod["analysis"].eq("SEED-3 by reproducibility")) & (mod["level"].eq("no-code"))]
    graph = mod[(mod["analysis"].eq("SEED-3 by method family")) & (mod["level"].eq("graph/GNN"))]
    trad = mod[(mod["analysis"].eq("SEED-3 by method family")) & (mod["level"].eq("traditional ML"))]
    slope_row = mod[(mod["analysis"].eq("meta-reg")) & (mod["level"].eq("SEED-3 transductive acc~year"))]

    diag = pd.DataFrame(
        [
            {
                "moderator": "Target access",
                "scope": "Matched task pools",
                "contrast": "Transductive minus inductive",
                "result": f"SEED {seed_t - seed_i:+.1f} pp; SEED-IV {siv_t - siv_i:+.1f} pp",
                "interpretation": "No large transductive advantage; protocols should be compared within task and target-access contract.",
            },
            {
                "moderator": "Method family",
                "scope": "SEED 3-class",
                "contrast": "highest vs lowest subgroup",
                "result": f"graph/GNN {graph.iloc[0]['pooled']}% vs traditional ML {trad.iloc[0]['pooled']}%" if not graph.empty and not trad.empty else "",
                "interpretation": "Architecture family explains less spread than protocol and reporting.",
            },
            {
                "moderator": "Leakage risk",
                "scope": "SEED 3-class",
                "contrast": "Some-concerns vs low/low-some",
                "result": f"{some_seed.iloc[0]['pooled']}% vs {low_seed.iloc[0]['pooled']}%" if not some_seed.empty and not low_seed.empty else "",
                "interpretation": "Higher-risk reporting is associated with higher reported accuracy.",
            },
            {
                "moderator": "Code availability",
                "scope": "SEED 3-class",
                "contrast": "Code vs no code",
                "result": f"{code.iloc[0]['pooled']}% vs {nocode.iloc[0]['pooled']}%" if not code.empty and not nocode.empty else "",
                "interpretation": "Association is descriptive; code availability is confounded with recency and method family.",
            },
            {
                "moderator": "Publication year",
                "scope": "transductive SEED 3-class",
                "contrast": "Weighted meta-regression slope",
                "result": f"+{slope_row.iloc[0]['pooled']} pp/year (SE {slope_row.iloc[0]['ci_lo']}, k={slope_row.iloc[0]['k']})" if not slope_row.empty else "",
                "interpretation": "Exploratory upward drift on a fixed benchmark; not causal evidence of progress.",
            },
        ]
    )
    return mod, diag


def compute_dataset_counts(master: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dataset in DATASETS:
        m = dataset_mask(master["dataset_name"], dataset)
        inc = master[m & master["include_narrative"].str.lower().eq("yes")]
        meta = master[m & master["include_meta"].str.lower().eq("yes")]
        rows.append(
            {
                "dataset": dataset,
                "included_unique_papers": inc["paper_id"].nunique(),
                "meta_eligible_unique_papers": meta["paper_id"].nunique(),
                "included_result_rows": len(inc),
                "meta_eligible_result_rows": len(meta),
                "source_file": "04_extraction/extraction_master.csv",
                "counting_rule": "canonical Fig.2 DATASETS regex mask; per-dataset non-additive unique paper_id count; multi-dataset papers count in each relevant dataset; include_narrative/include_meta == yes",
            }
        )
    return pd.DataFrame(rows)


def write_meta_markdown(meta: pd.DataFrame) -> None:
    display = meta[meta["DL_mean"].astype(str).str.len().gt(0)].copy()
    lines = [
        "# Protocol-stratified random-effects meta-analysis",
        "",
        "> Machine source of truth: `meta_results.csv` and `meta_diagnostics.csv`, recomputed after applying completed consensus adjudication on 2026-07-04.",
        "",
        "Comparable rows are pooled only within dataset, task, metric, and target-access protocol. Estimates are descriptive summaries of reported performance, not unbiased population effects.",
        "",
        "| Dataset · task | Protocol | k | DL mean [95% CI] | HK 95% CI | I² | Logit | LOO range | Maturity |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in display.itertuples(index=False):
        lines.append(
            f"| {r.task.replace(' | ', ' · ')} | {r.stratum} | {r.k} | "
            f"{r.DL_mean} [{r.DL_ci_lo}, {r.DL_ci_hi}] | [{r.HK_ci_lo}, {r.HK_ci_hi}] | "
            f"{r.I2}% | {r.logit_mean} | [{r.LOO_lo}, {r.LOO_hi}] | {r.maturity} |"
        )
    lines.extend(
        [
            "",
            "Rows with fewer than three numeric-SD studies remain in `meta_results.csv` as narrative/nonpooled strata.",
            "Every pooled value can be traced to the `studies` field in `meta_results.csv`; dataset coverage is in `dataset_included_counts.csv`.",
        ]
    )
    META_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compute_screening_consensus() -> tuple[pd.DataFrame, dict[str, int]]:
    base = read_csv(SCREEN_BASE)
    h2 = read_csv(SCREEN_H2)
    h2_map = h2.set_index("record_id").to_dict(orient="index")
    rows = []
    for _, row in base.iterrows():
        out = row.to_dict()
        rec = out["record_id"]
        if rec in h2_map:
            h = h2_map[rec]
            out["final_decision"] = str(h.get("adjudicator_decision", "")).strip()
            out["final_reason_code"] = str(h.get("adjudicator_reason_code", "")).strip()
            out["final_notes"] = str(h.get("adjudicator_notes", "")).strip()
            out["adjudicated"] = "yes"
        else:
            out["final_decision"] = str(row.get("reviewer_decision", "")).strip()
            out["final_reason_code"] = str(row.get("reviewer_reason_code", "")).strip()
            out["final_notes"] = str(row.get("reviewer_notes", "")).strip()
            out["adjudicated"] = "no"
        rows.append(out)
    consensus = pd.DataFrame(rows)
    counts = Counter(consensus["final_decision"])
    return consensus, {
        "records_screened": len(consensus),
        "screening_excluded": int(counts.get("exclude", 0)),
        "screening_include_candidate": int(counts.get("include-candidate", 0)),
        "screening_unclear_needs_fulltext": int(counts.get("unclear-needs-fulltext", 0)),
        "screening_reports_assessed_or_sought": int(counts.get("include-candidate", 0) + counts.get("unclear-needs-fulltext", 0)),
        "screening_adjudicated": int((consensus["adjudicated"] == "yes").sum()),
    }


def main() -> None:
    master = read_csv(EXTRACTION)
    master, audit = apply_adjudicator_meta(master)
    write_csv(master, EXTRACTION)
    write_csv(audit, APPLIED_AUDIT)

    consensus, screening_counts = compute_screening_consensus()
    write_csv(consensus, SCREEN_CONSENSUS)

    meta_data = prep_meta_data(master)
    meta, diag = compute_meta_results(meta_data)
    mod, mod_diag = compute_moderators(meta_data, meta)
    dataset_counts = compute_dataset_counts(master)

    write_csv(meta, META_RESULTS)
    write_csv(diag, META_DIAG)
    write_csv(mod, MOD_RESULTS)
    write_csv(mod_diag, MOD_DIAG)
    write_csv(dataset_counts, DATASET_COUNTS)
    write_meta_markdown(meta)

    included_papers = int(master[master["include_narrative"].str.lower().eq("yes")]["paper_id"].nunique())
    included_rows = int((master["include_narrative"].str.lower() == "yes").sum())
    meta_papers = int(master[master["include_meta"].str.lower().eq("yes")]["paper_id"].nunique())
    meta_rows = int((master["include_meta"].str.lower() == "yes").sum())
    summary = {
        "generated_on": "2026-07-04",
        "raw_database_records": 1664,
        "duplicates_removed": 887,
        "unique_records_screened": screening_counts["records_screened"],
        "screening_excluded_after_adjudication": screening_counts["screening_excluded"],
        "screening_include_candidate_after_adjudication": screening_counts["screening_include_candidate"],
        "screening_unclear_needs_fulltext_after_adjudication": screening_counts["screening_unclear_needs_fulltext"],
        "reports_assessed_or_sought_after_adjudication": screening_counts["screening_reports_assessed_or_sought"],
        "screening_adjudicated_rows": screening_counts["screening_adjudicated"],
        "qualitative_included_studies": included_papers,
        "qualitative_result_rows": included_rows,
        "meta_eligible_studies": meta_papers,
        "meta_eligible_result_rows": meta_rows,
        "adjudicator_meta_rows_applied": int(len(audit)),
        "adjudicator_meta_rows_added_to_extraction_master": int((audit["action"] == "added").sum()),
        "adjudicator_meta_rows_set_no_meta": int((audit["after_include_meta"] == "no").sum()),
        "reports_excluded_unobtainable_or_queued_after_fulltext": int(screening_counts["screening_reports_assessed_or_sought"] - included_papers),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {APPLIED_AUDIT.relative_to(ROOT)}")
    print(f"wrote {SCREEN_CONSENSUS.relative_to(ROOT)}")
    print(f"wrote {META_RESULTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
