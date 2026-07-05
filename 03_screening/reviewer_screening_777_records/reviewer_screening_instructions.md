# Independent Reviewer Title/Abstract Screening Instructions

Screen the 777 records in `reviewer_title_abstract_screening_blinded.csv` independently.
The current project decisions are intentionally omitted from this file.

## Fill These Columns

- `reviewer_decision`
  - `include-candidate` = potentially eligible; keep for full-text eligibility.
  - `exclude` = clearly ineligible from title/abstract.
  - `unclear-needs-fulltext` = cannot decide from title/abstract.

- `reviewer_reason_code`
  - Use `include` for `include-candidate`.
  - Use one exclusion code for `exclude`.
  - Use `unclear-needs-fulltext` when unsure.

- `reviewer_notes`
  - Optional, but useful for disagreements or uncertain cases.

## Optional Protocol Red-Flag Fields

Use these only when the title/abstract or quick full-text glance gives enough information. Do not exclude a paper solely because of a red flag at this stage unless it is clearly ineligible.

- `author_protocol_claim_seen`
  - Record the protocol wording used by the authors, if visible, for example `subject-independent`, `cross-subject`, `LOSO`, `transfer learning`, `cross-session`, or `not stated`.

- `protocol_red_flag`
  - Use `yes`, `no`, or `unclear`.

- `protocol_red_flag_type`
  - Use the most relevant code:
    - `subject-dependent-labelled-subject-independent`
    - `subject-mixed-kfold`
    - `cross-session-labelled-cross-subject`
    - `target-access-unclear`
    - `preprocessing-or-selection-unclear`
    - `claim-method-mismatch-suspected`
    - `other`

- `protocol_red_flag_note`
  - Briefly state why the protocol looks suspicious and where you saw it, if available.

## Eligibility Rule

Include at title/abstract if the record appears to satisfy all five criteria:

- I1: EEG-based emotion or affective-state recognition.
- I2: cross-subject, subject-independent, LOSO, cross-session, transfer, domain adaptation, domain generalization, source-free adaptation, few-shot target adaptation, or cross-dataset evaluation.
- I3: at least one quantitative performance metric.
- I4: public dataset or identifiable/clearly described dataset.
- I5: enough detail likely exists to classify the protocol.

## Exclusion Codes

- `subject-dependent-only`
- `no-subject-separation`
- `private-insufficient`
- `not-eeg`
- `non-primary-study`
- `non-english`
- `insufficient-info`
- `duplicate`
- `out-of-date-range`

## Consensus Rule

After independent reviewer screening:

- The independent reviewer and initial project decision agree: decision stands.
- The independent reviewer and initial project decision disagree: a consensus adjudicator resolves the record.
- Report agreement before adjudication, including raw agreement and Cohen's kappa where applicable.
