# PRISMA 2020 Flow — Variables and Running Counts

Counts are updated as the review proceeds. Each number must reconcile with the per-query rows in
`search_log.csv` and the decisions in `../03_screening/screening_decisions.csv`.

> **STATUS: MULTI-DATABASE IDENTIFICATION STARTED (2026-06-24, sweep 4).** The identification stage now
> carries **real, citable database counts** from the two databases with open programmatic APIs —
> **PubMed = 276** (NCBI E-utilities) and **arXiv = 63** (arXiv export API). These are not estimates; the
> query URLs and returned `<Count>` / `<opensearch:totalResults>` values are logged in `search_log.csv`
> (S039, S041). **What is still pending:** (1) exhaustive title/abstract screening of the full 276 + 63
> pool — this pass triaged a high-relevance subset (~38 new records) on top of the original seed corpus;
> (2) the **subscription databases** (Scopus, Web of Science, IEEE Xplore full Command Search,
> ScienceDirect, SpringerLink, ACM DL) require institutional authentication that the fetch tool cannot
> pass — they are logged as **access-limited**, not run, and **not faked**; individual records from them
> were instead surfaced indirectly via WebSearch and PubMed/arXiv; (3) cross-source deduplication of the
> full pools; (4) full-text extraction of the newly promoted records. **Included (full-text verified)
> remains 12** — promotion to "included" requires full-text verification, which the new records have not
> yet had.

## Identification

| Source | Records | Retrieval method | Status |
|--------|--------:|------------------|--------|
| **IEEE Xplore** | **251** | full metadata export + 250 full-text PDFs (journal-only, our search string), user-supplied 2026-06-25 | ✅ REAL COUNT + abstracts + PDFs. Log: `03_screening/ieee_xplore_screening.csv` |
| **Web of Science** | **656** | BibTeX export `WOS_v2.bib` (journal articles), user-supplied 2026-06-25 (replaces the earlier 50-entry partial) | ✅ REAL COUNT + abstracts |
| **Scopus (export)** | **616** | Scopus CSV export (Document Type = Article), user-supplied 2026-06-25 | ✅ REAL COUNT + abstracts |
| **PubMed (export)** | **141** | PubMed text export (journal), user-supplied 2026-06-25 | ✅ REAL COUNT (141 distinct PMIDs) + abstracts |
| **— COMBINED 4-DATABASE POOL** | **777 unique** | DOI→PMID→title dedup (`03_screening/combined_screening.csv`) | ✅ **COMPLETE SYSTEMATIC SEARCH** (IEEE 251 + WoS 656 + Scopus 616 + PubMed 141 = raw **1,664** → **777 unique**, 887 duplicates removed); screened → **33 known / 116 excluded / 628 in-scope cross-subject EEG-emotion journal candidates**. **33 candidates publicly share code** (abstract-detected lower bound; `code_available_papers.csv`). Full-text access: 204 local PDFs, 177 OA-fetchable, remainder for manual download (`need_fulltext_PAYWALLED.csv`, to be refreshed on the 628-pool). |

> **Updated reconciliation (2026-06-25): the search is now a genuine multi-database systematic search.**
> Four databases (IEEE Xplore 251, Scopus 616, PubMed 141, Web of Science 50; raw 1,058) were exported with
> our journal-only cross-subject string, deduplicated by DOI→PMID→title to **709 unique records**, and
> screened to **597 in-scope cross-subject EEG-emotion journal candidates** (33 already verified in the
> corpus; 79 excluded as off-task or non-primary). This satisfies the senior-reviewer requirement for a
> complete, counted, deduplicated search. Full-text verification of the 597 (under the no-fabrication rule)
> proceeds in batches; the manuscript can now be framed as a true systematic review rather than a
> verified evidence synthesis.
| **PubMed** | **276** | E-utilities esearch API (public) | ✅ real count (S039); 100 PMIDs captured; full t/a screening pending |
| **arXiv** | **63** | export API (public) | ✅ real count (S041); 39 entries captured + triaged |
| Google Scholar / Semantic Scholar (WebSearch surfaces) | 20 + targeted sweeps | WebSearch (S008–S034, S043–S048) | seed corpus + coverage sweeps |
| Semantic Scholar Graph API | — | API returned HTTP 429 | ⚠️ not retrieved (S042); retry later, not fabricated |
| IEEE Xplore (full Command Search) | — | requires institutional auth | ⛔ access-limited; records surfaced indirectly only |
| Scopus | — | requires institutional auth | ⛔ access-limited; not run |
| Web of Science | — | requires institutional auth | ⛔ access-limited; not run |
| ScienceDirect | — | requires institutional auth | ⛔ access-limited; individual papers surfaced via WebSearch |
| SpringerLink | — | requires institutional auth | ⛔ access-limited; individual papers surfaced via WebSearch |
| ACM Digital Library | — | requires institutional auth | ⛔ access-limited; not run |
| Snowballing (backward/forward) | 0 | pending | not yet started |
| Duplicate records removed | not yet deduped across full pools | DOI + title/author/year | pending |

> **Honest reconciliation note.** A true PRISMA identification total requires pooling all database
> exports and deduplicating. Two databases now return real counts (PubMed 276, arXiv 63 — overlap with
> each other and with the WebSearch seed not yet removed). The remaining databases are access-blocked in
> this environment. So the identification stage is **genuinely underway with real counts for the
> API-open databases**, but is **not yet the complete multi-database export** a finished review needs.

## Screening (triaged subset to date — NOT the full 276+63 pool)

| Variable | Count | Note |
|----------|------:|------|
| Records title/abstract screened (triaged subset) | 61 | seed 20 + 38 new candidates + 3 reviews; full 276+63 pool pending |
| Records excluded at title/abstract | 5 | 3 non-primary reviews (Apicella 2024; Eval-review 2025; Few-shot survey 2024) + 1 out-of-scope task (EEG-to-image retrieval) + 1 duplicate (EEG-0032 ≡ EEG-0030, E2STN text-overlap) |
| Reports sought for retrieval (full text) | 56 | |
| Reports assessed & full-text verified (INCLUDED) | 33 | 24 meta-eligible + 9 narrative-only (mdJPT EEG-0044, EEG-SCMM EEG-0045, degradation EEG-0027, stratified-norm EEG-0050, **fatal-leakage exemplar EEG-0057**, source-free cross-dataset EEG-0011, SEED-VII inductive EEG-0033, cross-dataset style-transfer EEG-0030, cross-dataset UDA EEG-0047) |
| Reports promoted / sought, full-text extraction PENDING | 23 | EEG-0012, 0013, 0018, 0019 + remaining EEG-0023..0056 (EEG-0009/0010/0011/0020/0021/0022/0030/0033/0035/0041/0043/0047 now INCLUDED; EEG-0032 excluded as duplicate) |
| Reports excluded at full text (with reasons) | 1 | EEG-0080 ELSTNN (Huang 2026, Information Fusion) — five-fold **subject-dependent** only, no LOSO/subject-independent experiment → out of scope (within-subject) |
| **Fatal-flag studies (kept as leakage exemplars, not pooled)** | 1 | EEG-0057 — confirmed subject + trial leakage (paper's own text); see `../06_quality/leakage_inflation_cases.md` Case 4 |

> Reconciliation (triaged subset): 61 t/a screened − 5 excluded = 56 sought for full text. Of those 56,
> **33 are full-text verified and included** (24 meta-eligible + 9 narrative-only); **23 are promoted and
> awaiting full-text extraction**. 33 + 23 = 56. EEG-0053 and EEG-0054 (the two ScienceDirect leakage
> candidates) were **user-supplied as PDFs and read in full** — EEG-0054's secondary "98%" proved fabricated
> (DEAP-only, honest mid-60s–70s; reclassified clean), EEG-0053's cross-dataset 93%+ confirmed transductive
> (leakage_inflation_cases Case 3). The
> 5 t/a exclusions: Apicella et al. 2024 (Neurocomputing review), the 2025 evaluation review
> (arXiv 2505.18175), the 2024 few-shot survey (Frontiers) — all retained for Related Work — the
> EEG-to-image retrieval paper (out-of-scope task), and EEG-0032 (E2STN, duplicate of EEG-0030). This subset proves the screening pipeline at
> multi-database scale; it is **not** the exhaustive screen of all 276 PubMed + 63 arXiv records.

## Included

| Variable | Count |
|----------|-------|
| Studies included in qualitative (narrative) synthesis | 408 |
| Studies included in quantitative synthesis (meta-analysis) | 103 |
| Extracted result rows (study × dataset × protocol) | 682 |

> **Sweep 9–11 update (2026-06-24): Scopus-MCP identification + root-PDF full-text verification.** The Scopus
> MCP (the only working subscription-DB MCP this pass — **IEEE Xplore MCP returned zero for all queries and was
> logged unavailable**, S049) surfaced ~55 records; 28 new were promoted (`../03_screening/scopus_screening_table.csv`).
> The user then supplied 17 of the paywalled promotions + 1 bonus paper as root PDFs, all **full-text verified**
> (`../03_screening/scopus_fulltext_verification.md`). Result: **+19 included** (33→**52**), **+7 meta-eligible**
> (24→**31**, after transcribing SDs for EEG-0058 and EEG-0070), **1 newly excluded at full text** (EEG-0080 ELSTNN — five-fold subject-dependent only, out of scope),
> and **7 Scopus promotions remain full-text-pending** (PDFs not obtainable: EEG-0061/0062/0069/0072/0075/0082/0083).
> **AMIGOS gap CLOSED** (2 independent verified sources: EEG-0078 Bendrich LOPO F1 0.741, EEG-0063 FDDGNet acc
> 0.7466). New datasets entered after English-scope filtering: **FACED, AMIGOS**. The 5 new meta rows: EEG-0059 (AD-TCN),
> EEG-0060 (ASJDA), EEG-0063 (FDDGNet), EEG-0073 (BGAGCN-MT inductive SEED 89.66/4.72), EEG-0086 (curriculum MSDA), plus **EEG-0058 (IDDA SEED 85.75/8.11, SEED-IV 72.36/9.43)** and **EEG-0070 (CA2DANet SEED 81.05/9.32)** upgraded after transcribing across-subject SDs from source tables.
> 14 further new includes are narrative-only (no transcribed SD or flagged), incl. 3 leakage-suspect (EEG-0064,
> 0067, 0074) + 1 disclosed eval-inflation (EEG-0084) — see `../06_quality/leakage_inflation_cases.md` Cases 5–6.

> The 21 meta-eligible = 16 prior + **CLISA (EEG-0020)** SEED 86.4/6.4 transductive + **SDC-Net (EEG-0009)**
> SEED 91.85/5.98 & SEED-IV 74.88/10.47 transductive + **DEPL (EEG-0041)** DEAP V66.23/A68.50 & MAHNOB-HCI
> V70.25/A73.27 inductive (closes the MAHNOB-HCI gap) + **HEDN (EEG-0010)** SEED 94.00/7.05, SEED-IV 79.36/9.62,
> DEAP V73.07/A73.20 transductive + **DAMSDAN (EEG-0043)** SEED 94.86/4.87, SEED-IV 82.48/8.02, FACED-binary
> 82.88/7.71 transductive (code verified) + **DAGAM (EEG-0035)** SEED 92.59/3.21, SEED-IV 80.74/4.14 transductive
> + **RSM-CoDG (EEG-0022)** SEED 86.35/7.17, SEED-IV 71.59/9.78, SEED-V 62.77/8.86 **inductive domain-generalization
> (no target data — stratum K, first in corpus; code verified)** + **FACE (EEG-0021)** SEED 5-shot 93.96/2.70,
> SEED-IV 89.51/3.13, SEED-V 95.20/1.42 **few-shot target-calibration (uses target labels — new stratum)**. (LGF
> EEG-0033 SEED-VII 7-class 40.1, E2STN EEG-0030 cross-dataset, and EEG-0047 cross-dataset UDA are includes but
> narrative-only — no SD or singleton cross-dataset directions.) The 6 narrative-only includes (mdJPT EEG-0044, EEG-SCMM
> EEG-0045, degradation EEG-0027, stratified-norm leakage exemplar EEG-0050, fatal-leakage exemplar EEG-0057,
> **source-free cross-dataset EEG-0011** DEAP->SEED 65.84/SEED->DEAP 58.99 with no SD) report only relative
> gains, no benchmark number, a non-comparable transductive-normalization result, leakage, or no dispersion.
> EEG-0050 (+12.5 pts) and EEG-0053 cross-dataset are documented in `../06_quality/leakage_inflation_cases.md`.
> Remaining pending promotions (32) move into these counts only after full-text verification under the
> no-fabrication rule.

## Dataset coverage of the INCLUDED studies (verified)

| Dataset | Included studies with a verified cross-subject result |
|---------|-------------------------------------------------------|
| SEED | EEG-0001,0002,0003,0004,0005,0007,0008,0009,0010,0014,0015,0020,0021,0022,0024,0035,0042,0043,0053 + EEG-0011,0030,0047 (cross-dataset) (22) |
| SEED-IV | EEG-0002,0005,0007,0008,0009,0010,0014,0021,0022,0024,0035,0042,0043,0053 + EEG-0030 (cross-dataset) (15) |
| SEED-V | EEG-0021,0022 (2 — FACE few-shot-labeled, RSM-CoDG inductive DG; **new dataset coverage**) |
| SEED-VII | EEG-0033 (1 — LGF, 7-class, inductive, narrative/no-SD; **new dataset coverage**) |
| MPED | EEG-0030 (1 — E2STN cross-dataset target; **new dataset coverage**) |
| DEAP | EEG-0001,0010,0016,0017,0041,0054,0053 + EEG-0011,0047 (cross-dataset) (9 — Li 2018, HEDN, EEGFuseNet, MTLFuseNet, DEPL, calibration-free meta-learning, PESD, + 2 source/cross-dataset) |
| DREAMER | EEG-0017 (1) |
| FACED | EEG-0015,0043 (2; EmT 9-class leave-12-out vs DAMSDAN binary — different tasks, not pooled; SDC-Net EEG-0009 also reports FACED but not extracted as a meta row) |
| MAHNOB-HCI | **1 — GAP CLOSED.** EEG-0041 (DEPL, Zhong & Yin 2020, full text Table V): MAHNOB-HCI 24 subj, inductive LOSO binary, Valence 70.25/5.54, Arousal 73.27/6.77 — first verifiable per-dataset MAHNOB-HCI cross-subject LOSO primary. EEGFuseNet also reports MAHNOB-HCI (V60.64/A62.06/D67.08/Pred74.63) but those rows are not in the included meta set; EmT uses it for regression only |
| AMIGOS | **2 — GAP CLOSED (sweep 11).** EEG-0078 (Bendrich 2022, Sensors; AMIGOS EEG-only LOPO subject-independent, valence F1 0.741 / arousal 0.699) and EEG-0063 (FDDGNet 2026, Neurocomputing; inductive domain-generalization LOSO, valence acc 0.7466±0.053). Two independent verified AMIGOS cross-subject EEG-only sources, both ~0.74 valence — the long-open gap is closed. |
| FACED (added) | EEG-0074 (UACL-Net; FACED number flagged near-ceiling/protocol-ambiguous — see leakage Case 6) |

## Pending pool — dataset/stratum breadth that WILL expand coverage once extracted

The 38 newly promoted records substantially broaden the protocol strata once verified:
- **Cross-dataset (stratum E):** EEG-0030, 0032, 0045, 0047, 0053 — currently thin in the included set.
- **Domain generalization, no target (stratum K):** EEG-0022, 0033.
- **Semi-supervised / target-label (stratum N):** EEG-0023, 0024, 0048, 0055 — leakage-critical.
- **Foundation / pretraining:** EEG-0037, 0044 — a stratum absent from the current included set.
- **Leakage-inflation exemplars (for the RQ on leakage→inflation):** EEG-0054 (SEED 98.09 / DEAP 98.06,
  implausible), EEG-0053 (cross-dataset 93+), EEG-0043/0052 (SEED 92–95), EEG-0050 (normalization
  leakage). EEG-0027 ("What Causes Performance Degradation…") is a methodological anchor for the
  Discussion.

> **Provenance note (updated 2026-06-24, sweep 4).** All 12 included studies remain `verified-from-fulltext`
> except EEG-0005/0007/0008 (`verified-RGNN-reproduction`). The 38 newly promoted records (EEG-0020..0057)
> were identified via the real PubMed/arXiv API counts and targeted WebSearch sweeps (S039–S048); each
> carries a source URL and is marked `unclear / passes-ta-needs-fulltext` (or a `leakage-flag-verify`
> note) — **none is counted as included** until its full text is read. The stray "72.81" once mis-attributed
> to EEGFuseNet was found during S047 to match **SDA-FSL on DEAP** — a different method — corroborating the
> earlier EEGFuseNet correction. Update this file whenever `search_log.csv` or `screening_decisions.csv`
> changes; the PRISMA flow figure is generated from these numbers.
