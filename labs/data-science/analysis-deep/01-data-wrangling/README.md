# Lab 01 - Data Wrangling

Cleaning raw tables so analysis is honest: missing values, duplicate rows,
ragged types, and outliers.

## What you will learn

- Classify missingness as MCAR, MAR, or MNAR and pick a matching response.
- Impute with mean, median, mode, or forward-fill without faking certainty.
- Remove duplicates with composite keys while keeping first-seen order.
- Coerce strings to numbers with explicit reject rules and counts.
- Flag outliers with the 1.5 x IQR rule and z-score screening.

## Working data

All examples use tiny inline arrays so every number is checkable by hand:

- `col = {2, 4, NaN, 8, 10}` - one missing entry, observed mean 6.0.
- Five order rows collapsing to three `(customer, date)` keys.
- Raw strings `{"12", " 45 ", "3x", "", "7.5", "N/A", "-8"}`.
- Outlier demo `{12, 14, 13, 15, 14, 13, 12, 15, 14, 60}`.

## Build and run (plain JDK only)

```text
javac --release 21 -encoding UTF-8 WrangleMeanImpute.java
java WrangleMeanImpute
```

No external libraries are used anywhere in this lab: only
`java.util`, `java.lang.Math`, and `java.util.stream`.

## Map of this lab

THEORY.md gives the definitions, MATH_FOUNDATION.md the derivations,
CODE_DEEP_DIVE.md the three verified programs, EXERCISES.md the practice
tasks, and STEP_BY_STEP.md a fully worked numeric example. Start with
THEORY.md, then run the code, then attempt the exercises.

## Suggested path

Read THEORY.md for the mechanism taxonomy, run the three programs in
CODE_DEEP_DIVE.md, follow STEP_BY_STEP.md with a calculator, then do
EXERCISES.md tasks 1-4 before touching 5-8. COMMON_MISTAKES.md lists the
traps (NaN comparison, zero-filling) that most first attempts hit.

## What done looks like

You can classify a missing column as MCAR/MAR/MNAR in one sentence, write
the impute/dedup/coerce trio from memory on plain arrays, and produce the
receipts (counts at every stage) for any cleaning run you perform.
