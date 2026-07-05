# Stage 2 — Search Strategy (PRISMA-S)

## Concept blocks

- **A. EEG terms:** `"EEG" OR "electroencephalography" OR "electroencephalogram" OR "brain signals"`
- **B. Emotion terms:** `"emotion recognition" OR "affective computing" OR "affect recognition" OR "emotion classification" OR "valence" OR "arousal"`
- **C. Cross-subject / transfer terms:** `"cross-subject" OR "subject-independent" OR "subject independent" OR "leave-one-subject-out" OR "LOSO" OR "domain adaptation" OR "domain generalization" OR "transfer learning" OR "unsupervised domain adaptation" OR "cross-session" OR "cross-dataset"`
- **D. Dataset terms (optional booster, not required for inclusion):** `"DEAP" OR "SEED" OR "SEED-IV" OR "SEED-V" OR "DREAMER" OR "AMIGOS" OR "MAHNOB-HCI" OR "ASCERTAIN" OR "MPED" OR "FACED" OR "GAMEEMO"`

**Logic:** `A AND B AND C` is the core. Block **D** is used as a secondary booster run
(`A AND B AND D`) to catch dataset-named papers that omit explicit cross-subject vocabulary in title/
abstract. Date filter: **2010–present**.

## Master Boolean string (generic)

```
("EEG" OR "electroencephalography" OR "electroencephalogram" OR "brain signals")
AND
("emotion recognition" OR "affective computing" OR "affect recognition" OR "emotion classification" OR "valence" OR "arousal")
AND
("cross-subject" OR "subject-independent" OR "leave-one-subject-out" OR "LOSO" OR "domain adaptation" OR "domain generalization" OR "transfer learning" OR "unsupervised domain adaptation" OR "cross-session" OR "cross-dataset")
```

## Database-specific strings

### IEEE Xplore (Command Search)
```
("All Metadata":"EEG" OR "All Metadata":"electroencephalography")
AND ("All Metadata":"emotion recognition" OR "All Metadata":"affective computing" OR "All Metadata":"valence" OR "All Metadata":"arousal")
AND ("All Metadata":"cross-subject" OR "All Metadata":"subject-independent" OR "All Metadata":"leave-one-subject-out" OR "All Metadata":"domain adaptation" OR "All Metadata":"domain generalization" OR "All Metadata":"transfer learning" OR "All Metadata":"cross-session" OR "All Metadata":"cross-dataset")
```
Filters: Year 2010–present.

### ACM Digital Library
```
[All: "eeg"] AND [[All: "emotion recognition"] OR [All: "affective computing"] OR [All: "valence"] OR [All: "arousal"]]
AND [[All: "cross-subject"] OR [All: "subject-independent"] OR [All: "leave-one-subject-out"] OR [All: "domain adaptation"] OR [All: "domain generalization"] OR [All: "transfer learning"] OR [All: "cross-session"] OR [All: "cross-dataset"]]
```
Filter: publication date 2010–present.

### Scopus (TITLE-ABS-KEY)
```
TITLE-ABS-KEY(("EEG" OR "electroencephalography")
AND ("emotion recognition" OR "affective computing" OR "affect recognition" OR "valence" OR "arousal")
AND ("cross-subject" OR "subject-independent" OR "leave-one-subject-out" OR "LOSO" OR "domain adaptation" OR "domain generalization" OR "transfer learning" OR "cross-session" OR "cross-dataset"))
AND PUBYEAR > 2009
AND (LIMIT-TO(LANGUAGE,"English"))
```

### Web of Science (Topic = TS)
```
TS=(("EEG" OR "electroencephalography")
AND ("emotion recognition" OR "affective computing" OR "affect recognition" OR "valence" OR "arousal")
AND ("cross-subject" OR "subject-independent" OR "leave-one-subject-out" OR "LOSO" OR "domain adaptation" OR "domain generalization" OR "transfer learning" OR "cross-session" OR "cross-dataset"))
```
Timespan: 2010–present; language English.

### PubMed
```
(("EEG"[Title/Abstract] OR "electroencephalography"[MeSH Terms] OR "electroencephalography"[Title/Abstract])
AND ("emotion recognition"[Title/Abstract] OR "affective computing"[Title/Abstract] OR "emotion"[Title/Abstract] OR "affect"[Title/Abstract])
AND ("cross-subject"[Title/Abstract] OR "subject-independent"[Title/Abstract] OR "leave-one-subject-out"[Title/Abstract] OR "domain adaptation"[Title/Abstract] OR "domain generalization"[Title/Abstract] OR "transfer learning"[Title/Abstract]))
AND ("2010"[Date - Publication] : "3000"[Date - Publication])
```

### ScienceDirect (limited Boolean depth — split runs if rejected)
```
("EEG" OR "electroencephalography") AND ("emotion recognition" OR "affective computing" OR "valence" OR "arousal") AND ("cross-subject" OR "subject-independent" OR "domain adaptation" OR "domain generalization" OR "transfer learning")
```
Note: ScienceDirect limits Boolean connectors per field; run reduced variants and log each separately.

### SpringerLink
```
"EEG" AND ("emotion recognition" OR "affective computing") AND ("cross-subject" OR "subject-independent" OR "domain adaptation" OR "domain generalization" OR "transfer learning" OR "cross-dataset")
```
Filter: 2010–present; English.

### arXiv (search interface)
```
all:(EEG AND ("emotion recognition" OR affective) AND ("cross-subject" OR "subject-independent" OR "domain adaptation" OR "domain generalization" OR "transfer learning"))
```
Categories of interest: cs.LG, cs.HC, eess.SP, cs.CV, q-bio.NC.

### Google Scholar (no field operators; keep short, run multiple)
```
EEG emotion recognition cross-subject domain adaptation
EEG emotion subject-independent LOSO
EEG affective computing domain generalization transfer learning
```
Use as snowballing / coverage check; record top-N screened per query.

### Semantic Scholar (API / UI)
```
EEG emotion recognition cross-subject generalization domain adaptation
```
Use Semantic Scholar relevance + citation graph for forward/backward snowballing.

## Snowballing strategy

- **Backward:** screen reference lists of all included studies and of any existing EEG-emotion surveys.
- **Forward:** use Semantic Scholar / Google Scholar "cited by" on included studies and on the seminal
  dataset papers (DEAP, SEED, DREAMER, AMIGOS, etc.).
- Snowball hits enter the same screening pipeline; source flagged `snowball` in the search log.

## Deduplication method

1. Export all records (RIS/BibTeX/CSV) into a single pool.
2. Deduplicate on **DOI** (exact), then on **normalized title + first author + year** (case/whitespace
   insensitive) for records lacking DOIs.
3. Manual check of near-duplicate titles (preprint vs published) — keep peer-reviewed, link the other.
4. Record counts before/after dedup in `prisma_flow.md`.

## Screening workflow

1. **Identification** → all DB + snowball records pooled, deduplicated.
2. **Title/abstract screening** → apply I1–I5 / E1–E7; `unclear` cases promoted to full text.
3. **Full-text screening** → final include/exclude with reason code.
4. **Eligible studies** → extraction (`04_extraction/`).

## PRISMA flow variables to record

See `02_search/prisma_flow.md`. Per-database hit counts and export counts go in
`02_search/search_log.csv`.
