# Quality Assessment Summary — Included Corpus (52 included; 49 scored)

> **Sweep 11 update (2026-06-24):** +19 included studies from the user-supplied root PDFs
> (full-text verified). Scored tally now **13 High / 32 Moderate / 4 Low across 49 scored**
> (3 not-scored narrative-only), **1 fatal** (EEG-0057). New High: **EEG-0060 (ASJDA, 87.5)**,
> **EEG-0063 (FDDGNet, 87.5)**, **EEG-0073 (BGAGCN-MT, 83.3)**. New Low (both leakage-suspect, non-fatal):
> **EEG-0064 (EmoCaps, 58.3)** and **EEG-0074 (UACL-Net, 50.0)**. Per-study scores in
> `risk_of_bias_scoring.csv`; per-paper evidence in `../03_screening/scopus_fulltext_verification.md`.
>
> **New cross-study finding — an "implausibly-high cross-subject" cluster.** Four sweep-11 papers report
> near-ceiling cross-subject numbers that do not survive scrutiny: **EEG-0064** (DEAP "subject-independent"
> 91–93% binary), **EEG-0067** (SEED-V 5-class 78.12%), **EEG-0068** (DEAP SI ~78–80% with ~92% recall),
> **EEG-0074** (DEAP ~98 / DREAMER ~99 / FACED ~99) — versus the credible LOSO range (~57–70% on DEAP).
> Together with the verified EEG-0084 10-fold-vs-LOSO ~27-pt gap and the fatal EEG-0057, this is direct
> RoB evidence that a non-trivial slice of recent venues publishes inflated "cross-subject" results — the
> review's central thesis. The contrasting **clean inductive** sweep-11 results (EEG-0073 SEED 89.66,
> EEG-0077/0079/0059 DEAP ~61–69%) show the honest range when LOSO is respected.

Scores live in `risk_of_bias_scoring.csv` (12 items × 0–2, max 24); rubric in
`quality_scoring_rubric.md`. This summary records the cross-study patterns (manuscript RoB section
material). **All scored studies are verified from full text or RGNN's full-text common-protocol
reproduction** — no row depends on secondary snippets. 3 narrative-only includes (EEG-0044 mdJPT,
EEG-0045 EEG-SCMM, EEG-0027 degradation-analysis) report only relative gains / no benchmark number, so
the rubric is not yet applicable and they are `not-scored`.

## Band distribution (updated 2026-06-24, sweep 8 — corpus expansion)

| Band | Studies | n |
|------|---------|---|
| High (≥80%) | EEG-0022 (RSM-CoDG, 91.7), EEG-0054 (calib-free, 87.5), EEG-0033 (LGF, 87.5), EEG-0002 (RGNN, 83.3), EEG-0006 (MS-MDA, 83.3), EEG-0024 (EEGMatch, 83.3), EEG-0042 (PR-PL, 83.3), EEG-0053 (PESD, 83.3), EEG-0043 (DAMSDAN, 83.3), EEG-0030 (E2STN, 83.3) | 10 |
| Moderate (60–79%) | EEG-0004 (PPDA, 79.2), EEG-0008 (BiHDM, 79.2), EEG-0017 (MTLFuseNet, 79.2), EEG-0020 (CLISA, 79.2), EEG-0009 (SDC-Net, 79.2), EEG-0010 (HEDN, 79.2), EEG-0035 (DAGAM, 79.2), EEG-0021 (FACE, 79.2), EEG-0047 (cross-dataset UDA, 79.2), EEG-0001 (Li, 75.0), EEG-0003 (Zheng & Lu, 75.0), EEG-0015 (EmT, 75.0), EEG-0041 (DEPL, 75.0), EEG-0011 (source-free, 75.0), EEG-0005 (DGCNN, 70.8), EEG-0007 (BiDANN-S, 70.8), EEG-0016 (EEGFuseNet, 70.8), EEG-0014 (SOGNN, 66.7) | 18 |
| Low (<60%) | EEG-0050 (stratified-norm leakage, 50.0), EEG-0057 (channel-wise, 41.7) | 2 |
| Fatal flag | EEG-0057 (subject + trial leakage) | 1 |
| Not scored (narrative, abstract-only) | EEG-0044, EEG-0045, EEG-0027 | 3 |

> **RSM-CoDG (EEG-0022, 91.7%) is now the top-scored study** — the only genuinely inductive domain-generalization
> entry (no target data, full reporting, public code). The two cleanest-protocol studies (RSM-CoDG, LGF) are both
> inductive DG, a notable inversion of the usual pattern where transductive methods dominate the leaderboard.

## What the full-text PDF pass changed (2026-06-24)

The user supplied the four previously-inaccessible primaries (Zheng & Lu, PPDA, EEGFuseNet, MTLFuseNet)
as PDFs in the project root. All four were read in full and rescored:

- **EEG-0003 Zheng & Lu** 54.2 → **75.0** (Table 1: TPT 76.31/**15.89** — SD now captured; explicit
  transductive LOSO; ANOVA + per-subject reported).
- **EEG-0004 PPDA** 54.2 → **79.2** (Table 2: PPDA-Few **86.7/7.1**; PPDA-NC 85.4; strong DA/DG
  baselines; few unlabeled-target calibration disclosed).
- **EEG-0016 EEGFuseNet** 54.2 → **70.8** — **NO-FABRICATION CATCH**: the previously-recorded DEAP
  "72.81%" was a secondary/misattributed value and **does not appear anywhere in the paper**. The real DEAP subject-independent *unsupervised*
  LOSO accuracies are **V 56.44 / A 58.55 / D 61.71 / Liking 65.89** (Table I); SEED 3-class 59.06 /
  2-class 80.83; MAHNOB-HCI V 60.64 / A 62.06. Tables report point values only (no SD →
  stat-reporting=1).
- **EEG-0017 MTLFuseNet** 54.2 → **79.2** (Table 4 DREAMER V **80.43/8.01** A **83.33/11.24**; Table 3
  DEAP V **71.33/5.24** A **73.28/7.74** newly captured; subject-independent LOSOCV, inductive; strong
  modern DL baselines).

Net across the two reconfirmation passes: **7 Low → 0 Low; 3 Moderate → 10 Moderate; 2 High unchanged.**

## Why nothing sits in High except RGNN and MS-MDA — and it is not an artifact

The High/Moderate line now falls cleanly on **item 10 (reproducibility / public code)**. Only RGNN and
MS-MDA have a verified public repository; every other study loses the points that would push it over
80%. PPDA, BiHDM, and MTLFuseNet all land at exactly **79.2** — strong on every axis except code
availability. This is a substantive field-level finding, not a verification gap.

## Cross-study patterns (these are findings, field-wide reporting gaps)

1. **Preprocessing-inside-CV is never clearly reported (item 5 = 1 for all 12).** No study in the seed
   corpus unambiguously stated whether normalization / feature selection / PCA was fit inside the CV
   loop or on source only. This is the single most consistent reporting gap and a prime driver of
   `normalization` / `feature-selection` leakage risk.
2. **Train/val/test separation rarely specified (item 4 mostly 1).** And one concrete failure:
   **SOGNN (EEG-0014) uses the held-out (test) subject as the validation set** — model/epoch selection
   on test data (a model-selection-leakage instance; items 4 & 6 = 0). Verify exact protocol, but as
   reported it inflates the 86.81% figure.
3. **Code availability is the exception (item 10).** Verified public repos: RGNN, MS-MDA, EEGMatch
   (EEG-0024), PR-PL (EEG-0042), PESD (EEG-0053) — about **5/22 scored**; SDC-Net (EEG-0009) promises
   release but it is not yet available. Reproducibility remains the norm's weakest link and is the main
   line separating the High and Moderate bands.
4. **Dispersion reporting is now confirmed from full text for most, with one clear exception (item 8).**
   Re-checked against primaries: Zheng & Lu (SD 15.89 + ANOVA), PPDA (SD 7.1), MTLFuseNet (SD on every
   cell + 5 metrics) **do** report dispersion — the earlier "mean-only" assumption was wrong.
   **EEGFuseNet is the genuine exception**: its result tables (I–III) report single point values with
   **no standard deviation across subjects**, which limits its meta-analytic weighting. Note EEGFuseNet
   also reports four affective dimensions separately (V/A/D/Liking), so a pooled DEAP accuracy is not
   directly defined.
5. **Benchmark-ambiguity is a scored item, not just narrative (EEG-0007).** BiDANN's subject-dependent
   (~92–97%) vs subject-independent BiDANN-S (84.14%) split is logged as a leakage-risk concern.
6. **Affective-theory grounding is universally strong (item 12 = 2 for all).** All use standard discrete
   (SEED family) or dimensional (DEAP/DREAMER) models.

## Fatal flags and leakage exemplars

**One fatal flag: EEG-0057** (channel-wise CNN, PMC7727848) — the paper's own methods put *"the same
subject and same stimuli"* in train and test while claiming "user-independent" (subject + trial leakage),
yielding near-ceiling DEAP 98.93/99.10, SEED 99.63. Kept as a leakage exemplar, `include_meta=no`
(`leakage_inflation_cases.md` Case 4).

For the rest, target-data usage is **disclosed** (it is the method — NodeDAT, MS-MDA, PPDA, EEGMatch,
PR-PL, CLISA online normalization, SDC-Net pseudo-labels). Disclosed transductive use is a protocol choice
(→ separate meta-analysis stratum), not fatal leakage. Two **Low-band non-fatal** cases sit between: EEG-0050
(stratified normalization using held-out test-subject statistics, undisclosed comparability flaw, +12.5 pts)
and CLISA (EEG-0020, online test-subject normalization — disclosed, scored Moderate but flagged transductive).
The SOGNN (EEG-0014) model-selection-on-test issue is hyperparameter/CV leakage, not fatal — it lowers the
score and is flagged for the sensitivity analysis.

## Next for the quality layer

- [x] Reconfirm the secondary rows against primaries and rescore — **done**: all 12 now full-text /
      RGNN-reproduction verified; 0 Low remaining.
- [ ] Resolve SOGNN's validation-set protocol from the full text (selection leakage yes/no) — still the
      one open methodological flag in the corpus.
- [ ] Once ≥2 reviewers exist, double-score and report inter-rater agreement (currently single-rater).
- [ ] Feed bands into meta-analysis as a subgroup/sensitivity variable (code-available-only synthesis).
