# Operational evaluation and target-access taxonomy

The revision describes every result on three orthogonal axes. This avoids treating an
algorithm name as though it automatically defines the information available at
deployment.

## Axis 1: evaluation regime

| Regime | Held-out unit | Interpretation |
|---|---|---|
| Subject-dependent | Trials/windows from participants represented in training | Within-participant recognition; not cross-subject evidence |
| Subject-disjoint / LOSO | One or more participants absent from source training | Cross-subject evaluation; target access is coded separately |
| Cross-session | Session or day held out | Temporal/session shift; may still include the same participant |
| Cross-dataset | Acquisition cohort/dataset held out | External dataset shift; label and montage compatibility must be reported |

## Axis 2: generalization mechanism

| Mechanism | Design objective | Target access is not implied by the name |
|---|---|---|
| Source-only learning | Fit a predictor on source subjects | Usually no target access |
| Domain generalization | Learn source-domain invariance before deployment | No target access by definition |
| Domain adaptation | Align source and target distributions | Usually unlabeled target access; verify the actual inputs |
| Source-free adaptation | Adapt a source-trained model without source data present | Commonly uses target data during adaptation |
| Test-time adaptation | Update model or statistics during deployment | Uses target stream/batch information unless purely per-instance |
| Contrastive/self-supervised learning | Learn representations through auxiliary objectives | Can be source-only or target-aware |
| Pretraining/fine-tuning | Initialize from an external or prior corpus and optionally update parameters | Record corpus overlap and all fine-tuning data/labels |
| Few-shot/semi-supervised calibration | Adapt using limited target labels | Target-supervised by definition |

## Axis 3: target-information access

| Access class | Permitted information | Strict no-target? | Supported claim |
|---|---|---:|---|
| Strict inductive | Source-training data and source-fitted preprocessing only | Yes | No-target unseen-subject generalization |
| Per-instance inductive | Current test window transformed without aggregating other target windows | Yes | No-target online inference; transformation must be disclosed |
| Target-statistic | Statistics estimated from target subject/session/batch/stream, without emotion labels | No | Transductive or test-time target adaptation |
| Unlabeled-target adaptation | Target samples used in adaptation, without emotion labels | No | Unlabeled-target cross-subject performance |
| Separate calibration set | Unlabeled target calibration set disjoint from the evaluation set | No | Inductive evaluation after target calibration |
| Target-supervised | Some or all target emotion labels used | No | Few-shot, semi-supervised, or supervised target calibration |

## Normalization decision rule

Normalization is coded by the data used to estimate its parameters:

1. A scaler fitted only on source-training participants and applied unchanged to the
   target is strict inductive preprocessing.
2. A deterministic transform computed independently within the current window is
   per-instance inductive when it does not use other target windows or future data.
3. Statistics fitted on all samples of the held-out subject, a target session, a target
   batch, or an accumulating target stream are target-statistic access. This can be a
   valid disclosed transductive/test-time method, but not a strict no-target result.
4. Any normalization chosen or estimated using target emotion labels is target-supervised.
5. If fitting scope is not stated, the result receives a reporting-uncertainty flag; it is
   not automatically accused of leakage.

## Legacy codes

The extraction master retains historical A--N protocol strings for audit continuity.
Analysis scripts derive the published strata from the explicit `split_type`,
`target_data_used`, `target_labels_used`, `adaptation_method`, and
`protocol_category` fields. The current manuscript reports operational strata rather
than interpreting a legacy letter alone.

## Comparability rules

- Do not pool subject-dependent and subject-disjoint regimes.
- Do not interpret transductive versus no-target pools as a causal target-access effect.
- Do not compare target-supervised calibration with no-label methods as equivalent tasks.
- Keep cross-dataset outcomes separate from within-dataset cross-subject outcomes.
- Require source/fold-level fitting for preprocessing in a strict inductive claim.
