# Cross-Subject EEG Emotion Recognition Revisited

Reproducibility package for the paper:

> **Cross-Subject EEG Emotion Recognition Revisited: A Leakage-Aware, Protocol-Normalized Systematic Review and Meta-Analysis**
> Muhamad Hafiz Abd Latif and Nur Syahirah Roslan.
> *IEEE Transactions on Affective Computing* (under review), 2026.

This repository releases the full, auditable evidence base and analysis code behind the review: the
extraction corpus, the risk-of-bias sheet, the leakage-evidence records, the meta-analysis inputs and
code, the figure-generation code, the search strings and PRISMA records, the blinded reviewer and
consensus-adjudication logs, the citation-to-record map, the reporting checklist, and a
data-traceability map. Its purpose is to let anyone **reproduce every number in the paper from the raw
files**.

No raw human-participant EEG data are redistributed. All quantitative synthesis uses published
aggregate results or publicly released benchmark descriptions.

## Headline corpus (frozen snapshot)

| Quantity | Value |
|---|---:|
| Active included studies (full-text verified) | 404 |
| Extracted result rows | 672 |
| Meta-eligible studies | 98 |
| Meta-eligible result rows | 198 |
| Public benchmarks covered | 11 |

## Repository layout

The folders follow the systematic-review pipeline in order.

| Path | Contents |
|---|---|
| `01_protocol/` | Review protocol, PICOS scope, inclusion/exclusion criteria (I1–I5, E1–E7) |
| `02_search/` | Boolean search strings per database, PRISMA flow record, raw search log |
| `03_screening/` | Title/abstract screening decisions, deduplication notes, and the blinded reviewer + consensus screening sheets (`reviewer_screening_777_records/`) |
| `04_extraction/` | 63-field extraction corpus (`extraction_master.csv`), extraction schema, citation-to-record map, active-exclusion log, and the blinded reviewer meta-extraction sheets (`reviewer_meta_extraction_review/`) |
| `06_quality/` | Risk-of-bias sheet, 12-item scoring rubric, leakage-evidence cases, quality summary |
| `07_meta_analysis/` | Pooled results, diagnostics, moderator analyses, publication-bias diagnostics, per-dataset counts, statistics summary, and the analysis plan |
| `scripts/` | Meta-analysis and figure-generation code |
| `10_figures_nature_style/` | Generated figures (PNG + PDF) |
| `09_manuscript/` | Data-traceability map and the minimum reporting checklist |

**Naming note:** in file and column names the prefix `reviewer_` denotes the independent reviewer and
`adjudicator_` denotes the consensus adjudicator.

## Reproduce the analysis

Run everything from the repository root.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1. Recompute the meta-analysis from the frozen extraction sheet.
#    Regenerates every file in 07_meta_analysis/ and prints the corpus counts
#    (404 studies, 672 rows, 98 meta-eligible, 198 meta rows).
python scripts/recompute_statistics_after_adjudication.py

# 2. Regenerate the figures.
python scripts/generate_nature_style_figures.py          # main figures (PRISMA, forest, landscape, ...)
python scripts/generate_publication_bias_diagnostics.py  # funnel plots
```

The scripts read only the CSV/JSON files in this repository and write back into `07_meta_analysis/`
and `10_figures_nature_style/`. `recompute_statistics_after_adjudication.py` is idempotent.

## Trace any number in the paper

`09_manuscript/manuscript_data_traceability.md` lists, for every reported count and pooled value, its
source file and the exact reproduction rule (e.g. "count unique `paper_id` where `include_meta == yes`").
To map a manuscript citation to its extraction record, use
`04_extraction/meta_eligible_reference_audit_20260705.csv` (paper id, citation key, DOI, title).

## Provenance

Screening and extraction were initialized by an LLM-assisted pass and then audited by an independent
reviewer, with a consensus adjudicator resolving disagreements (`03_screening/`,
`04_extraction/reviewer_meta_extraction_review/`). Three records were removed from active analysis
(`04_extraction/excluded_from_active_analysis_20260704.csv`): EEG-0041 and EEG-0096, and the duplicate
EEG-0104 (a preprint superseded by its published version, EEG-0350).

## Citation

See `CITATION.cff`. Please cite the paper; the volume/issue/pages/DOI will be added on acceptance.

## License

- **Code** (`scripts/`): MIT — see `LICENSE`.
- **Data and documentation** (all other files): CC BY 4.0.

## Contact

Muhamad Hafiz Abd Latif (corresponding author) — ORCID [0000-0002-9246-1028](https://orcid.org/0000-0002-9246-1028)
Nur Syahirah Roslan — ORCID [0000-0002-6371-1067](https://orcid.org/0000-0002-6371-1067)
