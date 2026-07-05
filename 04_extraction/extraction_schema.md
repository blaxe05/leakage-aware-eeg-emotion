# Stage 5 — Data Extraction Field Dictionary

One row per **study × dataset × protocol × reported result** in `extraction_master.csv`. If a study
reports several comparable results, use multiple rows and mark the pre-specified primary with
`primary_result = yes` (see `../07_meta_analysis/meta_analysis_plan.md` for dependency handling).

Fill only what is confirmable from the paper / supplement / repo / dataset doc. Unknowns are written
`not verified`, `unclear`, or `NA` — never guessed.

## Bibliographic fields
| Column | Meaning |
|--------|---------|
| `paper_id` | Stable ID `EEG-####`. |
| `authors` | Author list (or first author + et al.). |
| `year` | Publication year. |
| `title` | Full title. |
| `venue` | Journal or conference name. |
| `venue_type` | `journal` / `conference` / `preprint`. |
| `doi` | DOI (or `NA`). |
| `url` | Stable URL to the record. |
| `code_repo` | Code repository URL (or `none found`). |
| `dataset_link` | Link to dataset used (or `NA`). |
| `peer_reviewed` | `yes` / `no` (preprint). |

## Dataset fields
| Column | Meaning |
|--------|---------|
| `dataset_name` | DEAP / SEED / SEED-IV / ... |
| `n_subjects` | Number of subjects used. |
| `n_sessions` | Number of sessions. |
| `eeg_channels` | Channel count. |
| `sampling_rate_hz` | Sampling rate. |
| `stimulus_type` | Video / music / images / etc. |
| `emotion_model` | discrete classes / valence-arousal / pos-neg-neutral / 4-class / etc. |
| `class_labels` | Label set used. |
| `class_balance` | Balance info if reported (else `not reported`). |
| `data_status` | `public` / `private`. |

## Preprocessing fields
| Column | Meaning |
|--------|---------|
| `filtering` | Band-pass / notch settings. |
| `artifact_removal` | ICA / ASR / manual / none. |
| `baseline_correction` | yes/no/details. |
| `re_referencing` | scheme or `not reported`. |
| `window_length_s` | Segment length (seconds). |
| `window_overlap` | Overlap fraction/step. |
| `feature_extraction` | What features computed. |
| `normalization` | Scaling/normalization scheme. |
| `preproc_in_cv` | `inside` / `outside` / `unclear` — was preprocessing/scaling/feature-selection fit inside the CV loop? |

## Feature / model fields
| Column | Meaning |
|--------|---------|
| `feature_type` | Raw EEG / PSD / DE / DASM / RASM / DCAU / wavelet / connectivity / graph / Riemannian / entropy / handcrafted / deep features. |
| `model_family` | SVM / KNN / RF / LR / ELM / CNN / RNN / LSTM / GRU / Transformer / GNN / autoencoder / contrastive / domain-adversarial / MMD / CORAL / TCA / optimal-transport / Riemannian-align / source-selection / ensemble / foundation-SSL. |
| `adaptation_method` | Specific DA/UDA/DG/SFDA/TTA/few-shot method (or `none`). |
| `source_selection` | Source-selection / weighting method (or `none`). |
| `target_data_used` | `yes` / `no` — was any target data used during training/adaptation? |
| `target_labels_used` | `yes` / `no` — were target labels used (for training or model selection)? |
| `hyperparam_protocol` | How hyperparameters were chosen (and on which data). |

## Evaluation fields
| Column | Meaning |
|--------|---------|
| `subject_independent` | `yes` / `no` / `unclear`. |
| `split_type` | LOSO / k-fold-subject / cross-session / cross-dataset / other. |
| `n_folds` | Number of folds (or `NA`). |
| `cross_setting` | none / cross-session / cross-dataset. |
| `train_val_test_separation` | Description of separation; flag if val=test. |
| `model_selection_strategy` | What data selected the final model. |
| `metric` | accuracy / balanced-accuracy / macro-F1 / weighted-F1 / AUC. |
| `result_mean` | Mean value (proportion or %). Record units. |
| `result_sd` | SD (or `not reported`). |
| `result_ci` | CI (or `not reported`). |
| `per_subject_reported` | `yes` / `no`. |
| `statistical_test` | Test used (or `none`). |
| `baselines_compared` | Baselines listed. |
| `best_baseline` | Best baseline value if given. |
| `claimed_sota` | `yes` / `no` — did authors claim SOTA? |
| `mean_or_best` | `mean-over-folds/subjects` / `best-run` / `unclear`. |

## Risk-of-bias / leakage fields
| Column | Meaning |
|--------|---------|
| `protocol_category` | A–N from `../05_taxonomy/protocol_taxonomy.md`. |
| `leakage_categories` | Semicolon-separated leakage types flagged (`../05_taxonomy/leakage_taxonomy.md`). |
| `risk_rating` | `low` / `some-concerns` / `high` / `unclear`. |
| `risk_evidence` | Quote/location supporting the rating. |
| `ambiguity_notes` | Free text. |
| `include_meta` | `yes` / `no` — include in primary meta-analysis? |
| `include_narrative` | `yes` / `no` — include in narrative synthesis? |
| `primary_result` | `yes` / `no` — is this the pre-specified primary row for the study/dataset/protocol? |

## Verification field (Stage 12)
| Column | Meaning |
|--------|---------|
| `verification_status` | `verified` / `partially-verified` / `unclear` / `not-enough-information` / `exclude-from-quant`. |
| `source_checked` | URL(s) actually inspected to confirm the row. |
