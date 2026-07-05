# Leakage-Inflation Case File

Evidence base for the review's central RQ: **does evaluation leakage / protocol conflation inflate reported
cross-subject EEG emotion-recognition accuracy?** Each case is graded by how firmly it is verified, per the
no-fabrication rule. "Verified" = read from primary full text this session; "Flagged-unverifiable" = strong
signal but the primary is paywalled / not machine-readable, so the inflation mechanism is **not** confirmed and
**no number is asserted as true**.

> Status legend: ✅ verified from full text · ⚠ flagged, protocol unverifiable · 🧩 benchmark-ambiguity (number
> real but mislabeled).

---

## Case 1 — Normalization leakage (✅ VERIFIED) — EEG-0050

**Fdez et al. 2021, *Cross-Subject EEG Emotion Recognition Through Neural Networks With Stratified
Normalization*, Frontiers in Neuroscience (10.3389/fnins.2021.626277).**

- **Protocol:** leave-one-subject-out, SEED, binary + ternary.
- **Mechanism (verbatim from full text):** features are min-max "stratified" normalized **per feature,
  participant, and session** — and the held-out **test** participant's own data is included when computing its
  normalization statistics. The feature scaling therefore uses **target-subject statistics**.
- **Effect:** ternary accuracy **79.6%** with stratified normalization vs **67.1%** with batch normalization on
  the same model — **+12.5 points**. Binary **91.6%** vs **87.6%**.
- **Why it is inflation:** the normalization makes this **transductive** (it consumes the target subject's
  feature distribution), yet the result is presented and compared as ordinary subject-independent LOSO. It is
  **not comparable** to inductive methods; the +12.5-point ternary gap is the size of the comparability error.
- **Disclosure:** the normalization *method* is described, but its transductive/leakage implication is **not
  acknowledged** as a limitation.
- **Grading:** risk **High**, quality band **Low (50%)** — the corpus's first Low-band study; `include_meta = no`
  (kept out of all pooled strata). `fatal_flag = no` because only **unlabeled** target statistics are used (a
  transductive normalization, not target-label leakage) — but it is a clear comparability/benchmark flaw.

---

## Case 2 — The "98%" that never existed (✅ RESOLVED — secondary number FABRICATED) — EEG-0054

**Bhosale, Chakraborty, Kopparapu 2022, *Calibration free meta learning based approach for subject independent
EEG emotion recognition*, Biomedical Signal Processing and Control vol 72, 103289 (read in full from
user-supplied PDF).**

- **What the secondary literature claimed:** ~**98.09% (SEED) / 98.06% (DEAP)** subject-independent — surfaced
  in an earlier WebSearch snippet and initially flagged here as a prime leakage-inflation candidate.
- **What the full text actually shows:** the number **does not exist in the paper**, and the paper **does not
  even use SEED** — it is **DEAP-only**. This is a fabricated/misattributed secondary figure, the second such
  catch in this review (cf. the "72.81" value misattributed to EEGFuseNet).
- **The real protocol (verified):** 32 DEAP subjects split **70:20:10 at the subject level** (5-fold; test
  subjects unseen) — a *correct* subject-independent design. Prototypical few-shot meta-learning on 8-s segments;
  three sampling regimes (RS / Subject-Dependent / Subject-Independent).
- **The real numbers (Table 7):** Test Setup II (zero-calibration, cross-subject) **valence 69.92 / arousal
  68.89 / dominance 66.81**; Test Setup I (within-subject calibration) 76.46 / 75.81. Honest, mid-60s–70s, with
  SDs in Tables 2–6.
- **Disposition:** reclassified from leakage suspect to a **clean, methodologically careful include** (risk
  Low-Some). **Lesson for the review:** the most extreme "headline" numbers can be artifacts of the *secondary*
  citation chain, not the primary study — only full-text verification settles it.
- **Bonus provenance:** this paper's Related Work attributes the stray "**72.81%**" to its ref **[32]** — a
  pretrained ResNet on DEAP, **68.60% → 72.81% after median filtering** — a third independent fix on where
  "72.81" actually comes from (it is **not** EEGFuseNet's result).

---

## Case 3 — "Cross-dataset" numbers achieved with target adaptation (✅ VERIFIED) — EEG-0053

**Wang, Tian, Zhou 2025, *Cross-dataset EEG emotion recognition based on pre-trained Vision Transformer
considering emotional sensitivity diversity* (PESD), Expert Systems with Applications vol 279, 127348 (read in
full from user-supplied PDF). Code: github.com/fangwangeeg/PESD.**

- **Headline (verified, Table 2 cross-dataset section):** SEED **93.14 ± 5.00** / DEAP **93.53 ± 4.32** / FACED
  **92.55 ± 6.86**.
- **How they are obtained (the crux, now confirmed from full text):** a two-phase **PESD** pipeline —
  pre-train a ViT encoder on a high-sensitivity source subject, then **adapt to the target dataset using
  Mixup + domain-adversarial + triplet alignment**, evaluated by **leave-one-out cross-validation on all
  trials**. The adaptation phase **consumes target-domain data**, and its classifier loss (Eq. 11) uses
  **target labels** — i.e. **transductive and target-supervised**, not inductive zero-shot transfer.
- **Internal contrast within the same paper:** PESD's *cross-subject* (within-dataset, still transductive DA)
  accuracy is markedly lower — SEED **87.02 ± 4.36**, DEAP **86.98 ± 6.07**. The cross-dataset 93% is the
  *higher*, target-adapted number.
- **External contrast (verified elsewhere):** genuine **inductive** cross-dataset SEED↔DEAP is ~**58–67%**
  (EEG-0011 source-free; UDA reports similar). Reading "93%" as cross-dataset *generalization* overstates it by
  ~25–35 points — the gap is the **protocol**, not the method.
- **Caveats noted:** DEAP's dimensional labels are **relabeled into 3 classes** and channels **up-sampled 32→62**
  for cross-dataset alignment — further reducing comparability to native-protocol DEAP results.
- **Disposition:** **verified transductive/target-adaptive exemplar.** Cross-dataset rows recorded with
  `include_meta = no` (separate stratum, not pooled with inductive results); the value of the case is the
  protocol-labeling ambiguity it makes concrete. *(Note: the secondary "DFF-Net 93.37/82.32" remains a
  distinct, still-unverified paper — the earlier number/name conflation is resolved by reading this primary.)*

---

## Case 4 — "User-independent" that trains and tests on the same subjects (✅ VERIFIED — FATAL) — EEG-0057

**"Interpretable Cross-Subject EEG-Based Emotion Recognition Using Channel-Wise Features" (E-EmotiConNet),
~2020, PMC7727848 (read in full, methods section).**

- **The claim:** the paper presents a "**user-independent**" model, defined in its own words as *"trained using
  data from some subjects while applied to new subjects in testing."*
- **The contradiction (verbatim from the methods):** *"We randomly split 10-fold that **the same subject and the
  same stimuli could be both in the training set and testing set**."* The implementation is a **sample-level**
  10-fold split — so segments from the *same subject* (and even the *same stimulus/trial*) appear in both train
  and test.
- **Two leakage types at once:** **subject leakage** (the most severe) **+ trial/stimulus leakage**.
- **The result:** near-ceiling **DEAP 98.93% (valence) / 99.10% (arousal) / 98.60% (4-class)** and **SEED 99.63%
  (3-class)** — physically implausible for genuine subject-independent EEG emotion recognition, where honest LOSO
  on SEED sits at ~**76–89%**. The ~13–20-point excess over the honest range is the leakage signature.
- **Grading:** **first FATAL flag in the corpus.** Risk High, quality band **Low (41.7%)**, `fatal_flag = yes`
  (confirmed subject leakage from the paper's own text), `include_meta = no` (excluded from every pooled
  stratum). Datasets are DEAP + SEED (**not** AMIGOS).
- **Why it is the keystone exemplar:** unlike Cases 1–3 (which involve transductive normalization or target
  adaptation — *different protocols* presented as cross-subject), this is a paper that **labels itself
  cross-subject while its own method section admits same-subject train/test contamination**. It is the cleanest
  possible illustration of the review's central thesis that "cross-subject" claims must be checked against the
  actual split, not the abstract.

---

## Case 5 — Headline 10-fold (subject-mixed) vs honest LOSOCV (✅ VERIFIED — eval-framework inflation, disclosed) — EEG-0084

**Chen et al. 2026, *A Multi-Task EEG Emotion Recognition Method Based on Emotion-Dimension Coupling
Constraints* (MLT-EDCC), Scientific Reports 16(1), 10.1038/s41598-025-34211-z (Europe PMC PMC12859010,
read in full).**

- **Headline (abstract + Table 2):** DEAP **97.68 / 97.74 / 97.41** (V/A/D), DREAMER **96.16 / 95.78 / 95.96** —
  these are **10-fold CV with subjects mixed across folds.**
- **The honest cross-subject numbers (Table 9, same paper):** DEAP LOSOCV **69.18 / 70.86 / 70.42**, DREAMER
  LOSOCV **67.53 / 67.24 / 66.88** — a **~27–28-point** drop from the headline.
- **Verdict:** **not fatal** — the authors *do* report LOSOCV in Table 9 — but the paper foregrounds the
  subject-mixed 96–98% figure in the abstract/headline. A clean **evaluation-framework inflation** exhibit:
  the gap is entirely the protocol (subject-mixed k-fold vs LOSO), not the method.
- **Grading:** risk some-concerns, band Moderate (70.8%), `fatal_flag = no`, `include_meta = no` (only the
  LOSOCV ~67–71% rows kept, narrative; no SD on LOSOCV). The 10-fold/LOSO gap is the case's value.

## Case 6 — The "implausibly-high cross-subject" cluster (⚠ SUSPECT — mechanism unconfirmed, numbers NOT asserted)

Four sweep-11 primaries report cross-subject numbers far above the credible LOSO range (~57–70% on DEAP;
~60–63% inductive on SEED-V 5-class). Per the no-fabrication rule these are recorded as **suspect**, kept
`include_meta = no`, and **not asserted as valid cross-subject results**:

| Study | Venue | Claim | Why implausible |
|-------|-------|-------|-----------------|
| **EEG-0064** EmoCaps | IEEE TAFFC 2026 | DEAP "subject-independent" **91.80/93.43/92.53** (binary V/A/D) | Stated grouped 10-fold-by-subject, but 91–93% is ~25–35 pts above credible DEAP LOSO (Li 2018 59.06); likely undisclosed global normalization or 1 s-segment fold leakage. |
| **EEG-0067** Bagherzadeh | Biomed. Signal Process. Control 2024 | SEED-V 5-class **78.12** (2-channel inductive) | ~15 pts above inductive SEED-V norm (RSM-CoDG 62.77); cross-database channel selection raises selection-leakage suspicion. |
| **EEG-0068** CMHFE-DAN | Information 2025 | DEAP SI **78.20/79.91** | Above typical LOSO DEAP; reported recall ≈ 92% at ~78–80% accuracy → class-imbalance-aided. |
| **EEG-0074** UACL-Net | IEEE Trans. Cybernetics 2026 | DEAP **~98** / DREAMER **~99** / FACED **~99** | Near-ceiling; "Cross-Validation" table label does not pin protocol to LOSO → likely subject-mixed CV mislabelled. (SEED 94.88 ± 3.86 is plausible and is the only recorded number.) |

**Why this matters:** unlike Cases 1–5 (mechanism verified from text), Case 6 is a *pattern* — recent peer-reviewed
venues (including IEEE TAFFC and TCYB) publishing near-ceiling "cross-subject" DEAP/DREAMER results whose magnitude
alone fails a sanity check against the field. It is strong, citable evidence for the review's thesis that
"cross-subject" headline numbers require protocol verification — while being scrupulous not to assert the suspect
numbers as real.

## Cross-references to already-verified ambiguity cases

| Case | Type | Status | Where |
|------|------|--------|-------|
| EEGFuseNet-misattributed "72.81" | **Propagated secondary-number error** — value absent from EEGFuseNet; real EEGFuseNet DEAP unsupervised LOSO is V 56.44 | ✅ verified (root PDF); origin traced to a separate DEAP/SDA-FSL or pretrained-CNN record | EEG-0016 / EEG-0115 |
| BiDANN ~92–97 vs BiDANN-S 84.14 | 🧩 benchmark-ambiguity — subject-**dependent** number cited as cross-subject | ✅ verified (RGNN Table II) | EEG-0007 |
| PR-PL 93.06 (single-session) vs 85.56 (cross-session) | 🧩 protocol-variant ambiguity within one paper | ✅ verified full text | EEG-0042 |

---

## What this case file supports in the manuscript

1. **Leakage inflation is real, measurable, and sometimes self-admitted.** EEG-0057 (FATAL) reaches
   **98.93–99.63%** while its own methods state the same subject and stimuli appear in train and test — a
   ~13–20-point excess over honest LOSO (~76–89% on SEED). The milder EEG-0050 (normalization touching
   test-subject data) shows a **+12.5-point** ternary inflation. Both are verified from primary text.
2. **"Cross-dataset" ≠ generalization when target data is used.** PESD's verified 93%+ (EEG-0053) is a
   **transductive, target-supervised** result; genuine inductive cross-dataset is ~58–67%. The ~25–35-point gap
   is a protocol-labeling artifact, not method magic — a concrete benchmark-ambiguity case.
3. **The most extreme "headline" numbers can be artifacts of the secondary citation chain.** Two now-verified
   cases — the "72.81" value misattributed to EEGFuseNet and the "98%" attributed to EEG-0054 — **do not exist
   in those primary papers** (EEG-0054 is DEAP-only and reports honest mid-60s–70s). Only full-text checking
   caught both.
4. **Conservative consequence:** compare **protocol-matched** results only; treat secondary numbers as
   unverified until the primary is read; never ingest an unverified extreme number as cross-subject SOTA.

> Every "verified"/"resolved" line here now traces to a primary full text read this session (the two ScienceDirect
> primaries were supplied by the user as PDFs and read in full). No number is asserted without that trace. New
> cases are appended as the pending pool (EEG-0009..0013, 0020..0057) is extracted.
