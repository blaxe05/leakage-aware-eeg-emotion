# Stage 1 — Review Protocol: Question and Scope

## Working title

**Cross-Subject Generalization in EEG-Based Emotion Recognition: A Systematic Review, Leakage-Aware
Taxonomy, and Meta-Analysis Across Public Datasets.**

## Positioning (what makes this not a generic survey)

This review treats **cross-subject generalization as the central problem**, not one topic among many.
Its distinguishing contributions are:

1. A **leakage-aware evaluation taxonomy** that separates genuinely subject-independent results from
   results inflated by evaluation leakage or protocol ambiguity.
2. **Dataset- and protocol-normalized evidence synthesis** — results are only compared when the
   underlying task, dataset, and protocol are compatible.
3. **Quantitative meta-analysis only where results are comparable**, with narrative synthesis elsewhere.
4. Explicit separation of: subject-dependent, subject-independent (LOSO), cross-session, transductive
   UDA, inductive UDA, domain generalization (DG), source-free adaptation, few-shot target calibration,
   and cross-dataset generalization.
5. Practical, **leakage-safe benchmarking recommendations** for the field.

## PICOS-ML framing (PICOS adapted for machine learning)

| Element | Definition for this review |
|---------|----------------------------|
| **Population / data** | Human EEG recordings used for emotion / affective-state recognition (public or clearly described datasets). |
| **Intervention / model** | ML / DL / transfer-learning / domain-adaptation / domain-generalization / source-free / few-shot methods producing emotion predictions from EEG. |
| **Comparator** | Baselines: traditional ML, deep learning, and DA/UDA/DG methods reported in the same study or as referenced SOTA. |
| **Outcomes** | Accuracy, balanced accuracy, macro-F1, weighted-F1, AUC; subject-level / cross-session / cross-dataset performance; SD and confidence intervals. |
| **Study design** | Cross-subject / subject-independent evaluation (primary), plus related transfer settings (cross-session, UDA, DG, few-shot, cross-dataset). Subject-dependent-only studies are excluded from primary synthesis. |

## Research questions

### Primary
- **RQ1** — Which datasets, emotion models, and evaluation protocols dominate cross-subject EEG emotion
  recognition?
- **RQ2** — Which method families show consistent gains under **leakage-safe** subject-independent
  evaluation?
- **RQ3** — How much does reported performance vary by dataset, protocol, feature type, model family,
  and adaptation setting?
- **RQ4** — What types of data leakage or protocol ambiguity are common, and how do they affect
  reported results?
- **RQ5** — Which evidence is strong enough for meta-analysis, and where is narrative synthesis more
  appropriate?
- **RQ6** — What are the unresolved methodological gaps for future IEEE TAC-level work?

### Secondary
- **SQ1** — How consistently are validation and hyperparameter-selection protocols reported?
- **SQ2** — How available and faithful is released code relative to reported results?
- **SQ3** — How often are per-subject statistics and confidence intervals reported (vs. single means)?
- **SQ4** — How comparable are emotion-label schemes across datasets, and what harmonization is needed?

## Scope boundaries

- **In scope:** EEG-based emotion/affect recognition with at least one cross-subject / subject-independent
  / cross-session / DA / DG / source-free / few-shot / cross-dataset result and ≥1 quantitative metric.
- **Out of scope:** Subject-dependent-only studies (except as contrast); non-EEG modalities unless EEG
  results are separately reported; reviews/editorials/abstract-only; insufficient protocol detail.
- **Date range:** **2010–present** (rationale: public EEG emotion benchmarks DEAP (2011) and SEED
  (2015) anchor the modern literature; pre-2010 work predates these shared benchmarks). Earlier
  foundational work may be cited in Background but not extracted for synthesis.
- **Languages:** English (non-English included only if essential and fully extractable — flagged).

## Deliverable linkage

Stage 1 → drives the search strategy (`02_search/`), the inclusion/exclusion criteria
(`01_protocol/inclusion_exclusion.md`), and the structure of the meta-analysis strata
(`07_meta_analysis/meta_analysis_plan.md`).
