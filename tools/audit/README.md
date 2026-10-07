# Content audit

This directory holds the tooling and results of the content audits run on `labs/`.
It exists because "every lab has all 10 layers" (a file-existence check) says nothing
about whether those files contain real material. Numbers below are from the audit run on
2026-10-07 and can be regenerated.

## 1. Templated filler (`filler_audit.py`)

```
python tools/audit/filler_audit.py     # from the repository root
```

A line of genuine, lab-specific prose is very unlikely to appear verbatim in many
unrelated labs, so the tool flags prose lines that appear in **20 or more lab
directories** and reports files made largely of them. It needs no list of known filler
phrases. Typical flagged lines:

- "Detailed explanation of the second core concept. Building on the first, this explores
  more advanced aspects of the methodology."
- "Topic 1: In-depth coverage with examples" / "Pitfall 1: How to identify and avoid it"
- "// More complex example showing best practices"

**Result (20,793 markdown files): 2,731 are filler-heavy (13.1%)** — at least 5 filler
lines making up at least 25% of the file's prose, or the generator stub
`try (var scope = null) { /* resource goes here */ }`.

| Academy | Filler-heavy files |
|---|---|
| java | 1,069 |
| math | 532 |
| data-science | 459 |
| algorithms | 214 |
| ai | 170 |
| backend | 107 |
| databases | 105 |
| data-structures | 55 |
| architecture | 20 |

Among the 10 pedagogy layers (filler-heavy / total): `CODE_DEEP_DIVE` 169/929,
`EXERCISES` 89/896, `FLASHCARDS` 79/894, `MATH_FOUNDATION` 117/898, `MINI_PROJECT`
146/688, `QUIZ` 49/905, `README` 190/1572, `REAL_WORLD_PROJECT` 166/680, `THEORY`
120/941, `VISION` 135/669.

`filler_heavy_files.csv` lists every flagged file, worst first.

**What this under-counts.** The test is deliberately conservative. Templated text with the
topic name swapped in differs line by line and is *not* caught, so the real share of
filler is higher. Code is excluded because idiomatic code legitimately repeats. Treat the
figures as a floor.

**What the flagged files look like.** `math/calculus-deep/01-limits-continuity/
MATH_FOUNDATION.md` is a generic "prerequisite mathematics" review (addition,
exponentiation, linear equations) with nothing on limits or epsilon-delta.
`data-science/01-data-wrangling/REAL_WORLD_PROJECT.md` is 95% filler: a generic
"ingestion → processing → storage" diagram and "REST API endpoints for data submission"
that would read identically for any topic.

## 2. Things that were checked and corrected

- **JEP citations**: ~140 JEP pages on openjdk.org were read for Release/Status/Title and
  compared with every citation in `labs/java`. Wrong numbers, releases, stages and LTS
  labels were fixed in `java-migration` and `java-version-history`, and preview JEPs cited
  as the final feature were fixed in 8 other labs.
- **Code snippets**: complete Java snippets were compiled with `javac`. The raw failure
  rate is **not** a quality metric here: many failures are deliberate counter-examples
  ("this does not compile"), JPA/Spring annotations, or collaborator types that exist only
  in the prose. The one unambiguous defect found by compiling was the generator stub above.
- **Links**: 3,005 unique URLs were probed individually; 285 returned 404/410. Of these,
  290 "unreachable" entries are almost all sample-code hostnames, and 10 of the dead URLs are
  XML namespace identifiers or placeholders that are *meant* not to resolve.

## 3. Not verified

- Numeric and version claims in the other academies (Kafka, PostgreSQL, Kubernetes, ...).
- Whether filler-heavy files should be rewritten, trimmed or removed is a content decision;
  this audit only finds them.
- The Wayback Machine *availability* API returned an empty result for a page that is
  certainly archived (`docs.oracle.com/javase/8/docs/api/`), so "not archived" cannot be
  concluded from it; the CDX index passed the same control and is the one to use.