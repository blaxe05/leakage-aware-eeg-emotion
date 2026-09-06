# Stage 4b — Leakage and Ambiguity Taxonomy

Each study is screened for the leakage types below. Flag all that apply in the extraction field
`leakage_categories` (semicolon-separated), then assign an overall `risk_rating`.

## Leakage / ambiguity types

| Key | Type | Description |
|-----|------|-------------|
| `subject` | Subject leakage | Same subject appears in both training and test. |
| `window` | Window leakage | Overlapping/adjacent windows split across train and test. |
| `trial` | Trial leakage | Windows from the same trial placed in both train and test. |
| `session` | Session leakage | Same session used for both tuning and testing. |
| `target-label` | Target-label leakage | Target labels used for model selection but reported as unsupervised/cross-subject. |
| `transductive` | Target-test transductive leakage | All test samples used to estimate target distribution without clear disclosure. |
| `normalization` | Normalization leakage | Scaler/PCA/feature selection fit on the full dataset before splitting. |
| `hyperparam` | Hyperparameter leakage | Hyperparameters chosen using target/test subjects. |
| `feature-selection` | Feature-selection leakage | Channels/features chosen using all subjects or test labels. |
| `cv` | Cross-validation leakage | Fold aggregation or repeated random splits that break subject independence. |
| `modality` | Modality leakage | Multimodal labels/non-EEG signals used but reported as EEG-only. |
| `pretrain` | Pretrained-representation leakage | Pretraining includes target/test subjects or same dataset folds. |
| `benchmark-ambiguity` | Benchmark ambiguity | Unclear whether result is subject-dependent or subject-independent. |
| `dataset-preproc` | Dataset preprocessing leakage | Official preprocessed features may smooth/normalize across sessions/subjects; verify split integrity (e.g., SEED DE features, LDS smoothing). |

## Risk rating rubric

| Rating | Definition |
|--------|------------|
| **low** | Protocol clearly leakage-safe for its claimed setting; subject/trial separation explicit; preprocessing/HP selection inside CV or on source only; target usage disclosed. |
| **some-concerns** | Mostly sound but ≥1 under-specified element (e.g., normalization timing unclear) that *could* but probably does not inflate results. |
| **high** | ≥1 confirmed leakage that plausibly inflates the headline number (e.g., subject leakage, target-label leakage, transductive without disclosure). |
| **unclear** | Insufficient detail to determine — cannot confirm safety. Treated conservatively (excluded from primary meta-analysis). |

> **Fatal-leakage flag:** any confirmed `subject`, `target-label`, or undisclosed `transductive`
> leakage is a *fatal* issue for the claimed cross-subject result regardless of other quality scores —
> record in `../04_quality/risk_of_bias_scoring.csv` (`fatal_flag = yes`) and set `include_meta = no`.

## How rating feeds synthesis

- `low` / `some-concerns` → eligible for **primary meta-analysis** (if otherwise comparable).
- `high` / `unclear` → **narrative + sensitivity analysis only**, never primary pooling.
- Always record `risk_evidence` (quote or location) justifying the rating — no unsupported ratings.
