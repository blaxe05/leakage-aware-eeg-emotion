# Protocol-Stratified Meta-Analysis Plan

## Objective

The quantitative synthesis estimates descriptive pooled performance within
comparable cross-subject EEG emotion-recognition contracts. It does not treat
published benchmark results as independent population samples and does not use
between-study protocol contrasts as causal estimates.

## Pooling Eligibility

A result is eligible for a primary pool when all of the following hold:

1. The dataset and task granularity match the stratum definition.
2. The metric is the same or explicitly convertible within the stratum.
3. The evaluation and target-access protocol match the stratum definition.
4. The result is a prespecified primary configuration for its paper and
   stratum.
5. The mean, dispersion, and the number of held-out subjects or folds are
   recoverable.
6. At least three independent studies contribute to the stratum.
7. The evidence-use decision permits quantitative synthesis.

Results that fail a pooling criterion remain available for narrative
synthesis where appropriate.

## Non-Comparable Results

The following are not combined in one primary pool:

- subject-dependent and subject-disjoint evaluations;
- no-target, unlabeled-target, and target-label protocols;
- cross-session, within-dataset cross-subject, and cross-dataset evaluations;
- binary, three-class, four-class, and other task granularities; or
- accuracy, balanced accuracy, macro-F1, and AUC unless an explicit conversion
  is justified.

## Effect And Variance

The primary effect is the reported performance percentage. Sampling variance
is computed as `(SD / sqrt(n))^2`, where `n` is the number of held-out subjects
or cross-validation folds over which the SD was calculated. Trial, window, or
epoch counts are not substituted for subjects or folds. Missing dispersion is
not imputed.

Chance-normalized accuracy is reported as a supplementary comparison across
class granularities:

`A_norm = (A - A_chance) / (1 - A_chance)`, where `A_chance = 1 / C` for `C`
balanced classes.

## Statistical Model

- DerSimonian-Laird random-effects pooled mean and 95% confidence interval.
- Hartung-Knapp 95% interval for small-sample uncertainty.
- Cochran Q, I-squared, tau, and tau-squared heterogeneity statistics.
- Approximate 95% prediction interval.
- Leave-one-study-out pooled range.
- Logit-transformed sensitivity analysis, back-transformed for reporting.

Pooled estimates are interpreted as benchmark-conditioned summaries because
many studies reuse the same public participants and experimental sessions.

## Moderator And Small-Study Analyses

Exploratory subgroup and meta-regression analyses may examine target-access
setting, method family, quality/risk category, code availability, and
publication year. Architecture and protocol are interpreted jointly, and
moderator associations are not treated as causal effects.

Funnel plots and Egger regressions are reported only for strata with sufficient
precision-eligible studies. These are treated as asymmetry diagnostics because
shared benchmarks, heterogeneity, and dependent design choices weaken standard
publication-bias assumptions.

## Post-Hoc Matched Analysis

The dated amendment in
`../01_protocol/revision_protocol_amendment_20260906.md` defines a separate
within-study, same-model target-access comparison. Its contrasts are reported
as a descriptive case series and are not pooled because only two studies were
eligible, rows within each study are dependent, and paired covariance was not
available.

## Outputs

- `meta_results.csv`: pooled and narrative strata.
- `meta_diagnostics.csv`: heterogeneity, prediction intervals, and Q tests.
- `moderator_analysis.csv` and `moderator_diagnostics.csv`: exploratory
  moderator results.
- `publication_bias_diagnostics.csv`: funnel and Egger inputs.
- `matched_target_access_*.csv` and `.json`: post-hoc matched summaries.
