# Protocol Audit Evidence

This file summarizes selected primary-source checks used to illustrate the
evidence-use taxonomy. The examples are not a prevalence sample and are not
used to infer author intent. A result is classified from the reported split,
preprocessing boundary, model-selection rule, and target-access contract.

## Status Definitions

- **Confirmed:** the primary report explicitly documents a mechanism that
  invalidates the stated cross-subject claim.
- **Protocol mismatch:** the reported result is valid for a different,
  generally easier target-access or evaluation contract.
- **Unresolved:** the available description is insufficient to verify the
  stricter claim; the result is retained narratively and not treated as false.
- **Reference:** a clearly documented protocol used as a comparison case.

## Audited Examples

| Paper ID | Reported claim | Primary-source finding | Quantitative consequence | Evidence-use decision |
|---|---|---|---|---|
| EEG-0057 | User-independent accuracy | The methods state that the same subjects and stimuli can occur in training and testing under 10-fold splitting. | DEAP 98.93/99.10 and SEED 99.63 do not estimate subject-independent performance. | Confirmed; fatal flag; exclude from cross-subject pooling. |
| EEG-0050 | LOSO subject-independent | Normalization uses statistics from the held-out subject. | SEED ternary accuracy changes from 67.1 to 79.6 (+12.5 percentage points). | Protocol mismatch; target-statistic access; not strict no-target evidence. |
| EEG-0020 | Cross-subject prediction | Online z-score moments are updated as held-out-subject samples arrive. | No isolated normalization contrast is reported. | Valid transductive target-statistic evidence. |
| EEG-0084 | Cross-subject results | The headline 10-fold analysis is subject-mixed; LOSO-CV is reported separately. | Headline values of 96-98% compare with LOSO values of approximately 67-71%. | Use the LOSO result only for cross-subject synthesis. |
| EEG-0053 | Cross-dataset generalization | Target labels are used during adaptation. | The reported 93%+ result is target-supervised and does not estimate no-label transfer. | Protocol mismatch; retain under target-supervised transfer. |
| EEG-0064 | Subject-independent DEAP | The grouped 10-fold wording does not fully establish the split boundary. | Reported DEAP binary accuracy is 91-93%. | Unresolved; narrative-only; not pooled. |
| EEG-0074 | Cross-validation benchmark results | Split and target access are underspecified. | Reported DEAP, DREAMER, and FACED values are 98-99%. | Unresolved; narrative-only; not pooled. |
| EEG-0087 | LOSO baseline | Inductive LOSO is explicitly described. | SEED 69.9 and MPED 24.9 provide stricter-contract reference values. | Reference case. |

The detailed supporting quotations, source locations, and row-level decisions
are stored in `risk_of_bias_scoring.csv` and
`../04_extraction/extraction_master.csv`. Normalization-specific decisions are
also recorded in
`../04_extraction/normalization_access_audit_20260906.csv`.

## Evidence-Use Rule

Confirmed subject, trial, or window contamination is excluded from
cross-subject pooling. Valid target-access protocols are retained but pooled
only with like contracts. Reports with unresolved protocol detail remain
available for narrative synthesis and do not enter a stricter pooled estimand.
