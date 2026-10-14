# Exploratory Analysis - Architecture

## EDA session pipeline

```text
question --> DISPLAY (sort, bin, tabulate) --> SUMMARIZE (robust first)
   --> STRATIFY (split by confounders) --> RECORD (numbers + limits)
       ^                                              |
       +------------------ next question -------------+
```

## Component responsibilities

- **Display:** sorted lists, text bins, contingency tables. No modelling,
  no tests - arrangement for the eye.
- **Summarize:** medians, quartiles, grouped means with n. Resistant
  summaries first; moments only after shape is known.
- **Stratify:** re-cuts every comparison by each plausible confounder
  (ward, age band, region). A comparison that survives stratification is a
  candidate finding; one that flips (77.34 vs 82.57 pooled against two
  within-ward wins) was composition all along.
- **Record:** appends question, display, numbers, strata checked, and the
  named next question. The record is the deliverable, not any single plot.

## JDK mapping

- Grouping: `LinkedHashMap` key to (sum, n) via `computeIfAbsent`.
- Rates: integer fractions printed as doubles (81/90 shown as 90.0%) with
  the raw k/n kept alongside for audit.
- Correlations: one shared `corr(a, b)` routine reused for all pairs.
- Ordering: `TreeMap` cells and sorted arrays keep displays deterministic.

## Invariants

1. No pooled rate is reported without its stratum rates beside it.
2. Every mean carries its n; every r carries its n and its scatter check.
3. Displays precede summaries in code order, mirroring the workflow.
4. The record accumulates; no finding exists only in a console scrollback.
