# Data Validation & Quality

**Track:** mlops  |  **Lab:** lab09  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. The Problem This Solves

Garbage in is not a modelling problem, it is a data problem. Most silent model failures start as a schema change nobody noticed.

Validation is the cheapest place to catch an incident: a failed expectation costs seconds, a model trained on corrupted data costs a quarter of debugging.

## 2. Learning Objectives

- Express data quality as verifiable expectations rather than ad-hoc checks
- Implement schema, range, nullability, uniqueness and distribution checks
- Approximate a distribution comparison with a rank statistic
- Design a validation suite that fails the pipeline rather than logging
- Separate blocking expectations from warnings
- Track data quality as a metric with trend and ownership

## 3. Core Concepts

### 3.1 Expectations are executable contracts

An expectation is a statement that can be evaluated: 'column x is never null', 'column y is between 0 and 1', 'column z is unique'. Bundling them into a suite gives a validation run an identity that can be compared over time, which is what turns spot checks into a trend.

### 3.2 Blocking versus warning

A blocking expectation stops the pipeline. A warning is recorded and routed. Confusing them is why teams end up ignoring all alerts: a nightly null rate of 0.5% becomes an error, gets overridden daily, and then hides a real 60% null rate.

### 3.3 Schema and contract checks come first

Type, nullability and column existence are cheap and catch the most destructive failures. An upstream integer that becomes a string will silently produce garbage features unless a contract blocks it.

### 3.4 Distribution checks catch subtle drift

Range checks pass while the shape changes. A rank statistic comparing sorted reference and current samples catches shape change without assuming a distribution, which matters for skewed business data.

### 3.5 Validation runs on the data that matters

Validating a sample is a trade: a 1% sample misses a rare corruption. Full validation is often affordable if the checks are pushed down to the engine rather than pulled into the JVM.

### 3.6 Quality is a metric, not a gate alone

Null rate, duplicate rate and freshness need trend dashboards with owners. A gate tells you it broke; a trend tells you it is degrading before it breaks.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `expectation: violation_count = |{r : predicate(r) false}|` | Expectation | the atomic unit of validation |
| `null_ratio = nulls / rows` | Null ratio | with a threshold and an owner |
| `rate_diff = |p_current - p_reference|` | Rate comparison | for binary and categorical checks |
| `KS = max|F_cur(x) - F_ref(x)|` | Rank statistic | shape comparison without assuming a form |
| `freshness = now - max(event_ts)` | Freshness | the most common real failure |
| `suite_score = 1 - weighted_violations` | Suite result | comparable over time |

## 5. How the Pieces Fit Together

1. Declare the schema contract: columns, types, nullability, primary keys.

2. Add domain expectations: ranges, allowed categories, referential integrity.

3. Add distribution expectations against a reference sample from production.

4. Add freshness and volume expectations, which catch upstream stalls first.

5. Classify each expectation as blocking or warning, with owners.

6. Run the suite on every pipeline stage that consumes the data and store the results as a trend.

## 6. Assumptions and Invariants

- Every expectation has an owner and a threshold with provenance
- Blocking expectations are rare enough to be trusted when they fire
- Checks are pushed to the engine so full validation is affordable
- Reference distributions come from known-good production data
- Validation results are stored as a trend, not just a pass or fail
- Freshness and volume are validated, since they catch upstream stalls first

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Warnings are overridden daily and a real break hides among them | no separation of blocking from warning | classify expectations explicitly; keep blocking failures rare |
| An integer column became a string and nothing failed | no type contract on the boundary | schema expectations run before any transformation |
| Validation passes but the data is 9 days old | no freshness expectation | freshness and volume are expectations like any other |
| Sampling 1% misses a corruption affecting 0.5% of rows | sampling below the failure granularity | push checks down to the engine and validate fully |
| Duplicate rows double-count revenue | no uniqueness or primary key expectation | uniqueness on the natural key plus a duplicate rate trend |
| Every alert is ignored after two weeks | thresholds copied with no reference history | set thresholds from observed history and review them quarterly |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `record Expectation(String name, String column, Predicate<Row> check, Severity severity)` | a named, classified, executable check |
| `BigDecimal for rate comparisons` | null and duplicate ratios compared at a defensible precision |
| `Stream<LongSummaryStatistics> for volume` | row counts and key cardinalities in one pass |
| `record ValidationResult(String suite, Instant at, Map<String,Long> violations)` | the stored trend row |
| `EnumSet / Map<Expectation,Long> for the report` | all failures listed, not just the first |

## 9. Where This Sits in the Larger System

- **mlops/lab01** runs validation as the first node of the DAG.
- **mlops/lab04** validates the inputs before materialising features.
- **mlops/lab08** uses validation results as an early drift signal.
- **mlops/lab07** puts contract tests in the CI fast lane.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Express data quality as verifiable expectations rather than ad-hoc checks
- [ ] 0 — cannot yet — Implement schema, range, nullability, uniqueness and distribution checks
- [ ] 0 — cannot yet — Approximate a distribution comparison with a rank statistic
- [ ] 0 — cannot yet — Design a validation suite that fails the pipeline rather than logging
- [ ] 0 — cannot yet — Separate blocking expectations from warnings
- [ ] 0 — cannot yet — Track data quality as a metric with trend and ownership

## 11. Summary Checklist

- [ ] Every expectation has an owner and a threshold with provenance.
- [ ] Blocking and warning expectations are separated and stay rare.
- [ ] Schema, freshness and volume are validated before anything else.
- [ ] Checks are pushed down so full validation is affordable.
- [ ] Results are stored as a trend with history.
- [ ] Thresholds come from observed production history.
