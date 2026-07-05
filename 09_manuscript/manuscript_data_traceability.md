# Manuscript Data Traceability Map

Updated 2026-07-05 after applying completed consensus adjudication, dropping `EEG-0041` and `EEG-0096`, and removing the duplicate `EEG-0104` (STRAViT SSRN preprint, superseded by the published `EEG-0350`) from active analysis.

## Active Corpus Counts

| Reported item | Current value | Source file | Reproduction rule |
|---|---:|---|---|
| Active included studies | 404 | `../04_extraction/extraction_master.csv` | Count unique `paper_id` where `include_narrative == yes` |
| Active result rows | 672 | `../04_extraction/extraction_master.csv` | Count rows where `include_narrative == yes` |
| Meta-eligible studies | 98 | `../04_extraction/extraction_master.csv` | Count unique `paper_id` where `include_meta == yes` |
| Meta-eligible result rows | 198 | `../04_extraction/extraction_master.csv` | Count rows where `include_meta == yes` |
| Dropped active-analysis records | 3 | `../04_extraction/excluded_from_active_analysis_20260704.csv` | Count rows in exclusion log |

## Risk-of-Bias Counts

| Reported item | Current value | Source file | Reproduction rule |
|---|---:|---|---|
| Active risk-sheet papers | 404 | `../06_quality/risk_of_bias_scoring.csv`; `../04_extraction/extraction_master.csv` | Filter risk sheet to active `paper_id` values where `include_narrative == yes` |
| Risk-scored active papers | 401 | `../06_quality/risk_of_bias_scoring.csv`; `../04_extraction/extraction_master.csv` | Active risk-sheet papers excluding `quality_band == not-scored` |
| High quality band | 21 | `../06_quality/risk_of_bias_scoring.csv`; `../04_extraction/extraction_master.csv` | Active-paper count where `quality_band == High` |
| Moderate quality band | 224 | `../06_quality/risk_of_bias_scoring.csv`; `../04_extraction/extraction_master.csv` | Active-paper count where `quality_band == Moderate` |
| Low quality band | 156 | `../06_quality/risk_of_bias_scoring.csv`; `../04_extraction/extraction_master.csv` | Active-paper count where `quality_band == Low` |
| Not scored | 3 | `../06_quality/risk_of_bias_scoring.csv`; `../04_extraction/extraction_master.csv` | Active-paper count where `quality_band == not-scored` |
| Fatal flags | 4 | `../06_quality/risk_of_bias_scoring.csv`; `../04_extraction/extraction_master.csv` | Active-paper count where `fatal_flag == yes`; these are contained within Low, not additive |

## Meta-Analysis Tables

| Manuscript/table item | Source file | Source fields |
|---|---|---|
| Table VII pooled means, HK CIs, I², tau², LOO ranges, maturity | `../07_meta_analysis/meta_results.csv` | `task`, `stratum`, `k`, `DL_mean`, `DL_ci_lo`, `DL_ci_hi`, `HK_ci_lo`, `HK_ci_hi`, `I2`, `tau2`, `LOO_lo`, `LOO_hi`, `maturity` |
| Table VII prediction intervals and Q diagnostics | `../07_meta_analysis/meta_diagnostics.csv` | `task`, `stratum`, `tau`, `tau2`, `I2`, `Q`, `Q_df`, `Q_p`, `PI_lo`, `PI_hi` |
| Protocol ladder and subgroup summaries | `../07_meta_analysis/moderator_analysis.csv` | `analysis`, `level`, `k`, `pooled`, `ci_lo`, `ci_hi`, `I2` |
| Moderator interpretation bullets | `../07_meta_analysis/moderator_diagnostics.csv` | `dimension`, `dataset_task`, `contrast`, `result`, `interpretation` |
| Publication-bias/asymmetry diagnostics | `../07_meta_analysis/publication_bias_diagnostics.csv` | all diagnostic columns |

## Dataset Landscape Counts

| Manuscript/table item | Source file | Reproduction rule |
|---|---|---|
| Table IV qualitative-synthesis/meta counts | `../07_meta_analysis/dataset_included_counts.csv` | Use `included_unique_papers/meta_eligible_unique_papers`; these are per-dataset, non-additive counts generated from `../04_extraction/extraction_master.csv` with the canonical Fig. 2 `DATASETS` regex masks in `../scripts/generate_revised_figures.py`; count unique `paper_id` where `include_narrative == yes` (qualitative synthesis) or `include_meta == yes`; multi-dataset papers count once in each relevant dataset |
| Fig. 2A included and meta-eligible dataset coverage | `../07_meta_analysis/dataset_included_counts.csv` | Use `included_unique_papers` and `meta_eligible_unique_papers`; the plotting script uses the same dataset masks and yes-only inclusion filters; bars are non-additive across datasets |

## PRISMA/Figure Inputs

| Figure or claim | Source file | Reproduction rule |
|---|---|---|
| PRISMA included and pooled counts | `../07_meta_analysis/statistics_summary_20260704.json`; `../scripts/generate_prisma_flow.py`; `../scripts/generate_nature_style_figures.py` | Figure scripts read active counts: 647 reports assessed/sought, 243 excluded/queued after full text, 404 included, 98 pooled/meta-eligible, 198 meta rows |
| Evidence landscape and pooled-strata plots | `../07_meta_analysis/meta_results.csv` | Read pooled rows with `maturity` not starting with `narrative` |
| Dataset/protocol distributions | `../04_extraction/extraction_master.csv`; `../07_meta_analysis/dataset_included_counts.csv` | Aggregate by dataset/task/protocol fields; dataset coverage uses the canonical Fig. 2 dataset masks |

## Active Exclusion Audit Trail

`EEG-0041` and `EEG-0096` were removed from the active extraction, risk, and meta-analysis files after the
source files were removed and the analysis decision was made to drop them. On 2026-07-05, `EEG-0104`
(STRAViT SSRN preprint) was additionally removed as a duplicate of the published `EEG-0350` (STRAViT,
IEEE TIM); both had been marked meta-eligible, so keeping both double-counted the study in the SEED and
SEED-IV inductive strata. The audit trail is retained in
`../04_extraction/excluded_from_active_analysis_20260704.csv`; backups of the pre-drop CSVs are stored next
to the active files with `before_20260704_drop_EEG0041_EEG0096` and `before_20260705_drop_EEG0104` in the filename.

Consensus-adjudication decisions are retained in
`../03_screening/reviewer_screening_777_records/screening_consensus_after_adjudication_20260704.csv` and
`../07_meta_analysis/adjudicator_meta_decisions_applied_20260704.csv`; the latter records each applied
meta-row update, addition, or exclusion before recomputation.
