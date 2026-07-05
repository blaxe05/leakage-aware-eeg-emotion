# Protocol-stratified random-effects meta-analysis

> Machine source of truth: `meta_results.csv` and `meta_diagnostics.csv`, recomputed after applying completed consensus adjudication on 2026-07-04.

Comparable rows are pooled only within dataset, task, metric, and target-access protocol. Estimates are descriptive summaries of reported performance, not unbiased population effects.

| Dataset · task | Protocol | k | DL mean [95% CI] | HK 95% CI | I² | Logit | LOO range | Maturity |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| DEAP · arousal (binary) | inductive/no-target | 3 | 67.78 [59.95, 75.61] | [48.94, 86.61] | 96.3% | 68.02 | [65.01, 71.93] | fragile (k=3, very high I2) |
| DEAP · arousal (binary) | transductive-UDA | 5 | 68.96 [64.99, 72.93] | [63.9, 74.03] | 91.7% | 69.03 | [67.89, 70.47] | moderate |
| DEAP · binary | transductive-UDA | 3 | 65.25 [64.3, 66.2] | [64.4, 66.1] | 0% | 65.25 | [65.13, 65.42] | fragile |
| DEAP · valence (binary) | transductive-UDA | 7 | 67.5 [64.55, 70.45] | [63.82, 71.18] | 92.9% | 67.56 | [66.41, 68.27] | moderate |
| DREAMER · arousal (binary) | inductive/no-target | 3 | 74.59 [67.11, 82.07] | [55.12, 94.07] | 94.4% | 74.75 | [70.58, 78.23] | fragile (k=3, very high I2) |
| DREAMER · valence (binary) | inductive/no-target | 4 | 74.91 [71.56, 78.26] | [67.54, 82.29] | 88.6% | 74.94 | [73.37, 76.57] | moderate |
| SEED · 3-class | inductive/no-target | 26 | 85.96 [83.33, 88.6] | [82.75, 89.18] | 95.5% | 87.1 | [85.58, 87.15] | moderate (high I2) |
| SEED · 3-class | transductive-UDA | 56 | 89.07 [87.85, 90.29] | [87.5, 90.64] | 91.3% | 89.49 | [88.92, 89.54] | moderate (high I2) |
| SEED · 3-class | few-shot/target-label | 7 | 88.67 [84.39, 92.95] | [81.36, 95.98] | 96.9% | 90.19 | [87.16, 90.47] | moderate |
| SEED-IV · 4-class | inductive/no-target | 12 | 75.13 [71.98, 78.28] | [70.39, 79.87] | 92.6% | 75.42 | [74.46, 77.22] | moderate (high I2) |
| SEED-IV · 4-class | transductive-UDA | 39 | 75.38 [72.99, 77.77] | [73.11, 77.64] | 94.2% | 75.79 | [75.06, 75.83] | moderate (high I2) |
| SEED-IV · 4-class | few-shot/target-label | 5 | 70.61 [60.85, 80.37] | [58.22, 83.01] | 93.2% | 70.76 | [66.16, 73.69] | moderate |
| SEED-V · 5-class | inductive/no-target | 3 | 73.18 [62.31, 84.05] | [50.41, 95.96] | 94% | 73.66 | [69.86, 78.72] | fragile (k=3, very high I2) |

Rows with fewer than three numeric-SD studies remain in `meta_results.csv` as narrative/nonpooled strata.
Every pooled value can be traced to the `studies` field in `meta_results.csv`; dataset coverage is in `dataset_included_counts.csv`.
