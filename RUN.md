# Reproducing the analysis and figures

Run all commands from the repository root. The revision analyses are CPU-only.

## 1. Environment

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Recompute the frozen meta-analysis

```bash
python scripts/recompute_statistics_after_adjudication.py
```

This reads `04_extraction/extraction_master.csv` and reviewer-adjudication inputs,
then regenerates the outputs under `07_meta_analysis/`.

## 3. Regenerate the figures

```bash
python scripts/generate_nature_style_figures.py
python scripts/generate_electrode_montage_figure.py
python scripts/generate_publication_bias_diagnostics.py
```

Generated figures are written under `10_figures_nature_style/`.

## 4. Regenerate the reviewer-requested analyses

```bash
python scripts/generate_reviewer_revision_analyses.py
```

This validates `04_extraction/matched_target_access_extraction_20260906.csv` and
regenerates the matched case-series, architecture-by-protocol, and
generalization-mechanism-by-protocol summaries under `07_meta_analysis/`. It does
not pool the matched contrasts because only two studies were eligible, multiple
rows within each study are dependent, and paired covariance was unavailable.

## 5. Trace manuscript values

See `09_manuscript/manuscript_data_traceability.md`. The normalization decision
trail is `04_extraction/normalization_access_audit_20260906.csv`.
