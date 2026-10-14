# Data Wrangling - Architecture

## Pipeline stages as components

```text
raw text -> PROFILER -> COERCER -> DEDUPER -> IMPUTER -> OUTLIER SCREEN -> VALIDATOR -> clean table
               |           |          |           |             |               |
            counts    reject log   key set    fill value    fence bounds    receipts
```

## Component responsibilities

- **Profiler:** read-only pass. Emits per-column missing counts and observed
  type samples. Never mutates.
- **Coercer:** pure function `String -> OptionalDouble` plus a reject log.
  Trimming happens inside; the grammar is fixed (sign, digits, one dot).
- **Deduper:** `LinkedHashMap<String, Row>` keyed by composite key with
  `putIfAbsent`, preserving first-seen order and giving stable output.
- **Imputer:** two-phase. Fit phase computes the fill value from observed
  cells only; apply phase substitutes it for NaN. The fill value and the
  filled count travel together as one record.
- **Outlier screen:** needs sorted data for quartiles; emits bounds plus the
  flagged subset for human review, never deletes by itself.
- **Validator:** asserts row-count reconciliation
  (in = kept + removed + rejected) and zero unexplained missing.

## JDK mapping

- Missing numerics: `Double.NaN` with `Double.isNaN` tests.
- Ordered dedup: `LinkedHashMap` (insertion order + O(1) lookup).
- Quantiles: copy, `Arrays.sort`, linear interpolation.
- Aggregation without libraries: `Map.merge` and `computeIfAbsent`.

## Data-flow invariants

1. No stage after the coercer sees unparsed text.
2. The imputer never sees duplicated rows (dedup runs first).
3. Every dropped or filled cell is counted in the receipts.
