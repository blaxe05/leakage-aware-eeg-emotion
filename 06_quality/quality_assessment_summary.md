# Quality Assessment Summary

Quality and reporting completeness were evaluated with the 12-item rubric in
`quality_scoring_rubric.md`. Each item is scored 0, 1, or 2, for a maximum of
24 points. The percentage score is mapped to High (at least 80%), Moderate
(60-79%), or Low (below 60%). A fatal flag is recorded separately for a
verified protocol condition that invalidates the stated cross-subject claim.

## Frozen Active-Corpus Distribution

| Quality band | Papers |
|---|---:|
| High | 21 |
| Moderate | 224 |
| Low | 156 |
| Not scored | 3 |
| **Active papers** | **404** |

Among the 401 scored active papers, four carry a fatal flag. All four are in
the Low band and are excluded from quantitative pooling. The `not-scored`
records are retained for narrative synthesis where the available reporting
does not support application of the complete rubric.

## Interpretation

The quality band is an evidence-use aid, not a judgment of author intent or a
standalone measure of model merit. Each score is accompanied by a source quote
or location in `risk_of_bias_scoring.csv`. Confirmed train-test contamination,
subject-mixed evaluation presented as cross-subject, and target-label misuse
can invalidate a specific claim. Disclosed transductive adaptation and
few-shot calibration remain valid evidence for their declared target-access
contracts.

Recurring reporting limitations in the active corpus include:

- unclear placement of preprocessing and feature selection relative to the
  cross-validation boundary;
- incomplete train, validation, and test separation details;
- limited public code availability; and
- missing subject- or fold-level dispersion, which prevents inverse-variance
  pooling.

These limitations are handled through protocol reclassification,
narrative-only retention, or quantitative exclusion according to the evidence
taxonomy in `../01_protocol/leakage_taxonomy.md`.

## Reproduction

- Per-paper item scores and evidence: `risk_of_bias_scoring.csv`.
- Scoring definitions: `quality_scoring_rubric.md`.
- Protocol-audit examples: `protocol_audit_evidence.md`.
- Active paper identifiers: `../04_extraction/extraction_master.csv`, filtered
  to `include_narrative == yes`.
