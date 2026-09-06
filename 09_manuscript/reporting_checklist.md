# Stage 11.H — Minimum Reporting Checklist for Cross-Subject EEG Emotion-Recognition Studies

A study claiming cross-subject / subject-independent generalization should report **all** of the
following. Each item is designed to make leakage detectable and results reproducible.

## Dataset & task
- [ ] Dataset name, version, and access status; number of subjects and sessions.
- [ ] EEG channels, sampling rate, reference scheme.
- [ ] Stimulus type and emotion model; exact class labels and how continuous ratings were binarized.
- [ ] Class balance per split.

## Splitting & protocol (the leakage-critical section)
- [ ] Explicit protocol: subject-dependent / LOSO / cross-session / UDA (transductive vs inductive) /
      DG / SFDA / TTA / few-shot / cross-dataset.
- [ ] Confirmation that train and test subjects are **disjoint** (no subject leakage).
- [ ] Confirmation that windows/trials are not split across train and test (no window/trial leakage).
- [ ] For cross-session: which sessions train vs test.
- [ ] For cross-dataset: source and target datasets named.

## Target data usage (for adaptation methods)
- [ ] Whether **any** target data was used during training/adaptation, and how much.
- [ ] Whether **target labels** were used (training or model selection).
- [ ] Transductive vs inductive: whether the test set itself was used to estimate target statistics.

## Preprocessing & feature selection
- [ ] Filtering, artifact removal, segmentation, normalization described.
- [ ] **Whether normalization / PCA / feature selection was fit inside the CV loop (or on source only).**

## Model selection & hyperparameters
- [ ] Hyperparameter search space and the data used to select them (must not be test/target).
- [ ] Train / validation / test separation; confirmation that validation ≠ test.

## Results & statistics
- [ ] Metric(s): prefer **balanced accuracy / macro-F1** alongside accuracy for imbalanced tasks.
- [ ] **Mean and dispersion** (SD or CI); per-subject or per-fold results.
- [ ] Whether the headline number is mean-over-subjects/folds or best run.
- [ ] Strong, fairly-tuned baselines; statistical test for claimed improvements.

## Reproducibility
- [ ] Public code repository matching the paper; seeds, configs, and split definitions released.
- [ ] Exact preprocessing pipeline (or use of official precomputed features, with caveats stated).

> This checklist supports structured self-audit and mirrors the 12-item quality
> framework in `../06_quality/quality_scoring_rubric.md`.
