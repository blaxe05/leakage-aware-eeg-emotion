# Stage 7 — Meta-Analysis Feasibility and Statistical Plan

> **PRIMARY-ANALYSIS STATEMENT.** Because reported EEG emotion-recognition performance is highly dependent on
> dataset, class structure, validation protocol, and target-subject access, the primary quantitative synthesis
> uses **random-effects meta-analysis stratified by dataset and validation protocol**. Accuracy is pooled only
> within comparable protocol groups, while **macro-F1 or balanced accuracy is preferred where available**.
> Additional **subgroup and meta-regression analyses** examine whether reported performance is moderated by
> **dataset, method family, adaptation setting, leakage risk, and reproducibility indicators**.

> **ACTIVE SNAPSHOT 2026-07-05 after dropping `EEG-0041`, `EEG-0096`, and the duplicate STRAViT preprint
> `EEG-0104` from active analysis (404 included / 98 meta-eligible) → `meta_results.csv` +
> `moderator_analysis.csv`.** 13 primary strata are currently pooled (DerSimonian–Laird, Hartung–Knapp CIs):
> SEED 3-class inductive 86.0% (k=26) / transductive 89.1% (k=56) / few-shot 88.7% (k=7); SEED-IV inductive
> 75.1% (k=12) / transductive 75.4% (k=39) / few-shot 70.6% (k=5); SEED-V inductive 73.2% (k=3); DEAP
> valence transductive 67.5% (k=7), while DEAP valence inductive/no-target is narrative-only after exclusion
> (k=2); DEAP arousal inductive 67.8% (k=3) / transductive 69.0% (k=5); DEAP binary transductive 65.3%
> (k=3); DREAMER valence 74.9% (k=4) / arousal 74.6% (k=3). **No stratum reaches the strong maturity criterion
> because flagship strata still have high heterogeneity.** Headline: the protocol gradient remains **small AND
> inconsistent** (+3.1 SEED, +0.2 SEED-IV; DEAP valence no-target is no longer poolable). Moderators: method
> family weak (graph 89.0, DA 87.5, transformer 87.1 on SEED-3, traditional ML 79.3); **leakage risk runs the
> wrong way** (some-concerns 88.3 > low/low-some 83.8); meta-regression shows **+1.07 acc-pts/year**
> leaderboard creep on transductive SEED.
> The ≥90% figures are leakage, not method gains.
>
> *(Superseded earlier runs: 2026-06-26 was 13 strata on a 408/103 corpus; 2026-06-25 was 7 strata on a
> 52/31 corpus.)*

## Guiding principle

Pool **only comparable results**. Where results are not comparable, use **narrative synthesis**.
Heterogeneity in EEG emotion recognition (datasets, tasks, protocols, features, models) is large, so
meta-analysis is **stratified and conservative**, and many comparisons will *intentionally* not be pooled.

## Feasibility decision tree

```
For a candidate group of results:
1. Same dataset?                                   no → do not pool (narrative)
2. Same emotion task granularity?                  no → do not pool (or normalize, separate analysis)
   (binary valence / binary arousal / 3-class / 4-class / multi-class)
3. Same protocol stratum?                          no → do not pool
   (LOSO-DG / UDA-transductive / UDA-inductive / DG-no-target / few-shot / cross-session / cross-dataset)
4. Same (or convertible) metric?                   no → do not pool
   (accuracy / balanced accuracy / macro-F1)
5. Leakage risk low or some-concerns?              no → exclude from primary; sensitivity only
6. ≥ 3 independent comparable studies?             no → narrative; report individually
   → If all yes: include in a primary meta-analysis stratum.
```

## Stratification (never collapse these)

- **Dataset** (DEAP, SEED, SEED-IV, ...).
- **Emotion task:** binary valence | binary arousal | 3-class | 4-class | multi-class.
- **Protocol:** LOSO subject-independent (DG, no target) | UDA transductive | UDA inductive | DG (no
  target) | few-shot target calibration | cross-session | cross-dataset.
- **Metric:** accuracy | balanced accuracy | macro-F1.
- **Feature/model family** (subgroup).
- **Leakage risk** (subgroup; drives sensitivity analysis).

### Explicit do-not-pool rules
- Do **not** pool subject-dependent (protocol A) with subject-independent (B–N).
- Do **not** pool transductive UDA (I) with domain generalization (K) unless as labelled subgroups.
- Do **not** pool binary with multi-class tasks without normalization or separate analysis.
- Do **not** pool high/unclear-leakage studies into the primary analysis (sensitivity only).

## Effect size

- Primary effect sizes are **proportions**: accuracy, balanced accuracy, macro-F1.
- Use **logit-transformed proportions** (or Freeman–Tukey double-arcsine where proportions near 0/1
  destabilize variance), back-transformed for reporting.
- Variance requires n (subjects/folds) and a dispersion estimate. If **SD/CI is missing, record as
  missing — do not impute or fabricate**; such studies may be summarized narratively only.

## Dependency handling (multiple results per study)

When one paper contributes several results to the same stratum:
1. **Preferred:** select one **pre-specified primary result** per study/dataset/protocol
   (`primary_result = yes`), or
2. Use **multilevel / hierarchical random-effects** models, or
3. Use **robust variance estimation (RVE)** to account for within-study correlation.

## Model and heterogeneity

- **Random-effects** models (DerSimonian–Laird or REML) due to expected heterogeneity.
- Report **I², τ², and Cochran's Q** where applicable.
- **Subgroup analysis** by dataset, protocol, feature family, model family, leakage risk.
- **Sensitivity analysis** excluding unclear/high-risk studies; compare pooled estimates with/without.

## Publication / small-study bias

- Assess **only** when enough comparable studies exist (rule of thumb ≥ 10 in a stratum).
- Use **funnel plots** and **Egger-type tests cautiously** — ML benchmark studies violate many
  assumptions (shared datasets, leaderboard chasing, non-independent errors). Interpret as exploratory.

## Outputs

- Meta-analysis feasibility table (which strata are poolable vs narrative-only).
- Recommended **primary** meta-analysis groups.
- Recommended **secondary / sensitivity** analyses.
- Explicit list of **what not to meta-analyze and why**.
- Required extracted fields for pooling: `metric`, `result_mean`, `result_sd`/`result_ci`,
  `n_subjects`/`n_folds`, `protocol_category`, `dataset_name`, `emotion_model`, `risk_rating`.

## Suggested implementation packages

- **R:** `metafor` (RE models, moderators), `meta`, `robumeta` / `clubSandwich` (RVE), `dmetar` (helpers).
- **Python:** `PythonMeta`, `statsmodels` (mixed effects), `scipy`; `numpy`/`pandas` for transforms;
  `matplotlib` for forest/funnel plots.
