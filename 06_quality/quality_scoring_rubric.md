# Stage 8 — Quality Assessment Framework (ML-specific)

Each study is scored on **12 items**, each **0–2**:

- **0** = not reported or problematic
- **1** = partially reported / unclear
- **2** = clearly reported and appropriate

Columns in `risk_of_bias_scoring.csv` map 1:1 to these items.

| # | Item (CSV column) | What "2" looks like |
|---|-------------------|---------------------|
| 1 | `dataset_clarity` | Dataset, subjects, channels, labels unambiguously stated. |
| 2 | `protocol_clarity` | Split type and target access fully specified (maps to a protocol A–N). |
| 3 | `subject_independent_validity` | Subject-disjoint train/test demonstrably enforced. |
| 4 | `train_val_test_separation` | Distinct train/val/test; val ≠ test; selection data named. |
| 5 | `preproc_inside_cv` | Scaling/feature-selection/PCA fit inside CV (or on source only). |
| 6 | `hyperparam_selection_clarity` | HP search space + selection data explicitly described, no target/test peeking. |
| 7 | `target_data_usage_disclosure` | Clear whether/which target data and labels were used. |
| 8 | `statistical_reporting` | Mean **and** SD/CI; per-subject or per-fold spread reported. |
| 9 | `baseline_strength` | Strong, fairly-tuned, current baselines compared. |
| 10 | `reproducibility_code` | Working code repo matching the paper; seeds/configs available. |
| 11 | `leakage_risk_item` | No confirmed leakage (this mirrors the leakage taxonomy rating). |
| 12 | `affective_theory_relevance` | Emotion model / labels grounded in affective theory where applicable. |

## Scoring

- `max_score` = 24 (12 items × 2).
- `percent` = `total_score / 24 × 100`.

| Band (`quality_band`) | Percent |
|-----------------------|---------|
| High quality | ≥ 80% |
| Moderate quality | 60–79% |
| Low quality | < 60% |

## Fatal flag (overrides band)

Set `fatal_flag = yes` if **any** confirmed fatal leakage exists (subject leakage, target-label
leakage, or undisclosed transductive use), regardless of total score. Record `fatal_reason`. Studies
with `fatal_flag = yes` are excluded from the primary meta-analysis (`include_meta = no` in extraction)
and discussed in narrative + sensitivity analysis only.
