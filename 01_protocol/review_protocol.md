# Review Protocol

## Review Question And Scope

This systematic review evaluates what can be concluded from published
cross-subject EEG emotion-recognition results after aligning their dataset,
task, metric, evaluation regime, generalization mechanism, and target-access
contract.

The review does not presume that protocol explains all performance variation.
Architecture, feature representation, preprocessing, optimization, model
selection, reporting completeness, and dataset characteristics are retained as
candidate sources of variation.

## PICOS-ML Framework

| Element | Definition |
|---|---|
| Population/data | Human EEG recordings used for emotion or affective-state recognition. |
| Intervention/model | Machine-learning, deep-learning, transfer-learning, adaptation, generalization, pretraining, and calibration methods that predict affect from EEG. |
| Comparator | Contract-matched classical, deep-learning, adaptation, or generalization baselines. |
| Outcomes | Accuracy, balanced accuracy, macro-F1, weighted-F1, or AUC, with subject- or fold-level dispersion where available. |
| Study design | Cross-subject, subject-independent, cross-session, cross-dataset, transductive, inductive, source-free, or target-calibrated evaluation with a quantitative result. |

## Review Questions

1. Which public benchmarks and corpus patterns define the evidence base?
2. Which method families have been evaluated under each target-access contract?
3. What pooled performance is supported within comparable
   dataset-by-task-by-metric-by-protocol strata?
4. Which recoverable factors structure reported performance variation?
5. How do verified protocol limitations, reclassifications, and unresolved
   ambiguity affect evidence use?
6. What reporting and benchmarking practices follow from the evidence?

Secondary questions address risk of bias, reproducibility and dispersion
reporting, non-poolable evidence, and uncertainty remaining after protocol
normalization.

## Scope Boundaries

- Publication years: 2010 through the final search date, 14 May 2026.
- Language: English.
- Study type: primary research with at least one quantitative EEG-based
  cross-subject or transfer result.
- Exclusions: subject-dependent-only evaluation, non-EEG work, reviews,
  non-primary reports, private data without an extractable public-benchmark
  result, insufficient protocol information, and duplicate reports.
- Subject-dependent and cross-session results may be retained only as explicit
  contrasts and are not pooled with subject-disjoint evidence.

## Evidence Model

Each extracted result receives three separate descriptors:

1. evaluation regime, such as subject-disjoint LOSO, subject-mixed validation,
   cross-session, or cross-dataset;
2. generalization mechanism, such as source-only learning, domain adaptation,
   domain generalization, contrastive learning, or pretraining; and
3. target-access class, ranging from no target data to unlabeled target data or
   target labels.

Pooling is permitted only when dataset, task granularity, metric, and
target-access protocol are compatible and the dispersion unit is recoverable.
The operational definitions are in `protocol_taxonomy.md` and
`leakage_taxonomy.md`.

## Reproducibility Links

- Search strategy: `../02_search/boolean_search_strings.md`.
- Eligibility rules: `inclusion_exclusion.md`.
- Extraction fields: `../04_extraction/extraction_schema.md`.
- Statistical plan: `../07_meta_analysis/meta_analysis_plan.md`.
- Reporting and risk rubric: `../06_quality/quality_scoring_rubric.md`.
