# Stage 3 — Inclusion and Exclusion Criteria

Applied in two passes: **title/abstract screening** then **full-text screening**. Each decision is
logged in `03_screening/screening_decisions.csv` with an explicit reason code.

## Inclusion criteria (ALL must hold)

| # | Criterion |
|---|-----------|
| I1 | Uses **EEG** for emotion or affective-state recognition (EEG-only, or a multimodal study that reports EEG results separately). |
| I2 | Evaluates at least one of: cross-subject / subject-independent / LOSO, cross-session, domain adaptation, domain generalization, source-free adaptation, few-shot target adaptation, or cross-dataset generalization. |
| I3 | Reports **≥1 quantitative performance metric** (accuracy, balanced accuracy, F1, AUC, etc.). |
| I4 | Uses **public datasets** or clearly described datasets with enough detail to identify them. |
| I5 | Provides **enough methodological detail to classify the protocol** (split type, target-data usage). |

## Exclusion criteria (ANY triggers exclusion)

| # | Criterion | Reason code |
|---|-----------|-------------|
| E1 | Purely **subject-dependent** with no cross-subject result. | `subject-dependent-only` |
| E2 | Mixes train/test windows from the same subject **without subject-level separation** but presents it as generalization. | `no-subject-separation` |
| E3 | Uses **private datasets only** with insufficient protocol detail. | `private-insufficient` |
| E4 | **Not EEG-based** (and no separately reported EEG result in a multimodal study). | `not-eeg` |
| E5 | Review, survey, editorial, abstract-only, poster, or **non-English** (unless essential and fully extractable). | `non-primary-study` / `non-english` |
| E6 | Reports results **without enough information** to determine dataset / protocol / metric. | `insufficient-info` |
| E7 | Duplicate / superseded version of an included record (keep peer-reviewed over preprint). | `duplicate` |

## Special handling

- **arXiv / preprints:** included only if (a) they contain enough methodological detail, or (b) they
  later appeared in peer-reviewed form (then prefer the peer-reviewed version; note the link).
- **Conference vs journal:** both eligible but **classified separately** (field `venue_type` in the
  extraction sheet) so synthesis can stratify or weight accordingly.
- **Multimodal studies:** included only for their **EEG-only** results; multimodal-fusion numbers are
  recorded but flagged and excluded from EEG-only meta-analysis strata.
- **Multiple results per study:** all retained in extraction; dependency handled at meta-analysis stage
  (one pre-specified primary result per study/dataset/protocol, or robust/multilevel models).

## Reason-code vocabulary (for the screening log)

`include` · `subject-dependent-only` · `no-subject-separation` · `private-insufficient` · `not-eeg` ·
`non-primary-study` · `non-english` · `insufficient-info` · `duplicate` · `out-of-date-range` ·
`unclear-needs-fulltext`
