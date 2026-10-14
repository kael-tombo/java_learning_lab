# Lab 04 - Exploratory Analysis

Tukey-style EDA on small data: distributions, grouped comparisons,
correlations held at arm's length, and the stratification habit that
defeats Simpson's paradox.

## What you will learn

- Run the EDA loop: question, display, summarize, stratify, record.
- Read distribution shape (skew, gaps, strays) from sorted values and bins.
- Compute grouped means with sanity checks (n sums, overall mean between
  group means).
- Reproduce a genuine Simpson reversal in concrete counts and explain it.
- Treat strong correlations (0.99, -0.99) as association only, and say what
  evidence would upgrade them toward causation.

## Working data

- Spend by region: north {10,30,50} mean 30.0, south {20,40,60} mean 40.0,
  overall mean 35.0, n = 6.
- Two wards: A treat 81/90 (90.0%) vs control 234/270 (86.7%); B treat
  192/263 (73.0%) vs control 55/80 (68.8%); pooled treat 77.34% loses to
  pooled control 82.57%.
- Five customers: age/spend r 0.9932316263764919, age/visits r
  -0.9853034458841585, spend/visits r -0.990942442678138.
- Shape demo {1,1,2,2,3,3,4,9,15}: mean 4.444444444444445, median 3.0.

## Build and run (plain JDK only)

```text
javac --release 21 -encoding UTF-8 EdaGroupByC.java
java EdaGroupByC
```

Only `java.util` and `java.lang.Math`. No statistics or plotting libraries:
displays are sorted lists and text bins, summaries are explicit loops.

## Suggested path

THEORY.md for the workflow and the paradox mechanics, CODE_DEEP_DIVE.md for
the three verified programs, STEP_BY_STEP.md to check the reversal by hand,
then EXERCISES.md. Read COMMON_MISTAKES.md before you trust any pooled rate.
