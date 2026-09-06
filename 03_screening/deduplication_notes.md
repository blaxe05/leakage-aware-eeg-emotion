# Deduplication and Screening Notes

## Deduplication procedure (executed once per identification batch)

1. **Pool** all exported records into a single working table (RIS/BibTeX/CSV).
2. **DOI exact-match** dedup first.
3. **Fuzzy dedup** for DOI-less records: normalize title (lowercase, strip punctuation/whitespace) +
   match on first-author surname + publication year.
4. **Manual preprint↔published reconciliation**: when an arXiv preprint and a peer-reviewed version
   coexist, keep the **peer-reviewed** record, set `reason_code = duplicate` on the preprint row, and
   record the preprint URL in the kept record's notes.
5. Log `records identified`, `duplicates removed`, and `records screened` in `../02_search/prisma_flow.md`.

## Screening rules

- Two-pass screening: **title/abstract** → **full text**.
- Apply inclusion (I1–I5) and exclusion (E1–E7) from `../01_protocol/inclusion_exclusion.md`.
- Default to **promote to full text** when title/abstract is ambiguous (`reason_code = unclear-needs-fulltext`).
- Every row in `screening_decisions.csv` gets exactly one `decision` (`include` / `exclude` / `unclear`)
  and, if excluded, one `reason_code`.
- `paper_id` convention: `EEG-####` (zero-padded, assigned at first identification; stable thereafter).

## Reliability

The independent reviewer screened all 777 title/abstract records. Agreement with the initial project
decision was recorded before consensus adjudication, and discordant or unclear records were resolved
in the frozen consensus file under `reviewer_screening_777_records/`.
