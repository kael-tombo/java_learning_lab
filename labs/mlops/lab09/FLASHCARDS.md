# Data Validation & Quality - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | What is a data expectation? | An executable statement about data that can be evaluated and stored, such as a nullability or range rule. |
| 2 | Why separate blocking from warning expectations? | So blocking failures stay rare and trustworthy; a gate that fires daily gets ignored. |
| 3 | Which check catches an upstream type change? | A schema or type contract on the boundary |
| 4 | Why validate freshness and volume? | They catch upstream stalls and partial loads before any downstream model sees bad data. |
| 5 | What does a KS-style statistic give you? | A shape comparison between reference and current samples without assuming a distribution. |
| 6 | Why is sampling risky for validation? | A 1% sample misses corruptions affecting less than 1% of rows, which are often the important ones. |
| 7 | Where should checks run? | Pushed down to the query engine so full validation is affordable on large tables. |
| 8 | Why store validation results as a trend? | A pass or fail tells you it broke; a trend tells you it is degrading before it breaks. |
| 9 | What is Expectations are executable contracts? | An expectation is a statement that can be evaluated: 'column x is never null', 'column y is between 0 and 1', 'column z is unique'. |
| 10 | What is Blocking versus warning? | A blocking expectation stops the pipeline. |
| 11 | What is Schema and contract checks come first? | Type, nullability and column existence are cheap and catch the most destructive failures. |
| 12 | What is Distribution checks catch subtle drift? | Range checks pass while the shape changes. |
| 13 | What is Validation runs on the data that matters? | Validating a sample is a trade: a 1% sample misses a rare corruption. |
| 14 | What is Quality is a metric, not a gate alone? | Null rate, duplicate rate and freshness need trend dashboards with owners. |
| 15 | In this lab, what does `expectation: violation_count = \|{r : predicate(r) false}\|` mean? | Expectation: the atomic unit of validation |
| 16 | In this lab, what does `null_ratio = nulls / rows` mean? | Null ratio: with a threshold and an owner |
| 17 | In this lab, what does `rate_diff = \|p_current - p_reference\|` mean? | Rate comparison: for binary and categorical checks |
| 18 | In this lab, what does `KS = max\|F_cur(x) - F_ref(x)\|` mean? | Rank statistic: shape comparison without assuming a form |
| 19 | In this lab, what does `freshness = now - max(event_ts)` mean? | Freshness: the most common real failure |
| 20 | In this lab, what does `suite_score = 1 - weighted_violations` mean? | Suite result: comparable over time |
| 21 | You see 'Warnings are overridden daily and a real break hides among them' in production. What is the cause and the fix? | no separation of blocking from warning Fix: classify expectations explicitly; keep blocking failures rare |
| 22 | You see 'An integer column became a string and nothing failed' in production. What is the cause and the fix? | no type contract on the boundary Fix: schema expectations run before any transformation |
| 23 | You see 'Validation passes but the data is 9 days old' in production. What is the cause and the fix? | no freshness expectation Fix: freshness and volume are expectations like any other |
| 24 | You see 'Sampling 1% misses a corruption affecting 0.5% of rows' in production. What is the cause and the fix? | sampling below the failure granularity Fix: push checks down to the engine and validate fully |
| 25 | You see 'Duplicate rows double-count revenue' in production. What is the cause and the fix? | no uniqueness or primary key expectation Fix: uniqueness on the natural key plus a duplicate rate trend |
| 26 | You see 'Every alert is ignored after two weeks' in production. What is the cause and the fix? | thresholds copied with no reference history Fix: set thresholds from observed history and review them quarterly |
| 27 | Which Java API is the backbone of: a named, classified, executable check | `record Expectation(String name, String column, Predicate<Row> check, Severity severity)` |
| 28 | Which Java API is the backbone of: null and duplicate ratios compared at a defensible precision | `BigDecimal for rate comparisons` |
| 29 | Which Java API is the backbone of: row counts and key cardinalities in one pass | `Stream<LongSummaryStatistics> for volume` |
| 30 | Which Java API is the backbone of: the stored trend row | `record ValidationResult(String suite, Instant at, Map<String,Long> violations)` |
| 31 | Which Java API is the backbone of: all failures listed, not just the first | `EnumSet / Map<Expectation,Long> for the report` |
| 32 | Why does Expectations are executable contracts matter operationally? | An expectation is a statement that can be evaluated: 'column x is never null', 'column y is between 0 and 1', 'column z is unique'. |
| 33 | Why does Blocking versus warning matter operationally? | A blocking expectation stops the pipeline. |
| 34 | Why does Schema and contract checks come first matter operationally? | Type, nullability and column existence are cheap and catch the most destructive failures. |
| 35 | Why does Distribution checks catch subtle drift matter operationally? | Range checks pass while the shape changes. |
| 36 | Why does Validation runs on the data that matters matter operationally? | Validating a sample is a trade: a 1% sample misses a rare corruption. |
| 37 | Why does Quality is a metric, not a gate alone matter operationally? | Null rate, duplicate rate and freshness need trend dashboards with owners. |
| 38 | In the Data Validation & Quality pipeline, what happens next? Declare the schema contract: columns, types, nullability, pr... | Declare the schema contract: columns, types, nullability, primary keys. |
| 39 | In the Data Validation & Quality pipeline, what happens next? Add domain expectations: ranges, allowed categories, referen... | Add domain expectations: ranges, allowed categories, referential integrity. |
| 40 | In the Data Validation & Quality pipeline, what happens next? Add distribution expectations against a reference sample fro... | Add distribution expectations against a reference sample from production. |
| 41 | In the Data Validation & Quality pipeline, what happens next? Add freshness and volume expectations, which catch upstream ... | Add freshness and volume expectations, which catch upstream stalls first. |
| 42 | In the Data Validation & Quality pipeline, what happens next? Classify each expectation as blocking or warning, with owner... | Classify each expectation as blocking or warning, with owners. |
| 43 | In the Data Validation & Quality pipeline, what happens next? Run the suite on every pipeline stage that consumes the data... | Run the suite on every pipeline stage that consumes the data and store the results as a trend. |
| 44 | Exercise focus: Expectation framework | A reusable, classified check system. |
| 45 | Exercise focus: Schema and contract checks | Catch the destructive failures first. |
| 46 | Exercise focus: Rate checks with a noise floor | Stop alerting on normal variation. |
| 47 | Exercise focus: Shape comparison for skewed data | Range checks pass while the shape changes. |
| 48 | Exercise focus: Blocking versus warning | Keep the gate trustworthy. |
| 49 | Exercise focus: Freshness and volume | Catch upstream stalls first. |
| 50 | State the Rate differences and their noise floor result for Data Validation & Quality. | Null rate 0.5% on n=1M vs 0.52% on n=1M: difference 0.02 points, SE_each = 0.00022, pooled SE = 0.00031, z = 0.64. Not a change. At 0.9% the z is 25 and the alert is unambiguous. |
| 51 | State the Sampling and the failure granularity result for Data Validation & Quality. | n=10,000 of 10M (0.1% sample): misses a 1% corruption with probability 0.99^10000 = 4.3e-44, essentially always caught. Misses a 0.01% corruption with probability 0.99^10000 ~ 0, so 10M rows slip through. |
| 52 | State the Rank-based shape comparison result for Data Validation & Quality. | With effective n = 10,000 at alpha = 0.5: critical KS at 5% is 1.36/sqrt(10000) = 0.0136. A KS of 0.08 is far beyond chance, indicating genuine shape change. |
| 53 | State the Suite score as a trend result for Data Validation & Quality. | 10 expectations, 1M rows, 3 violations in one non-blocking expectation with weight 0.5: score = 1 - 0.5*3/1e6 = 0.9999985, a flat trend. The same 3 violations in a blocking expectation stop the pipeline regardless of score. |
| 54 | What is the cheapest high-value expectation set? | Schema, nullability, primary key uniqueness, freshness and volume. |
| 55 | How do you pick a threshold for a null rate? | From observed history, with a review cadence, rather than a round number. |
| 56 | What is a duplicate rate expectation for? | Catching fan-out from a join or a replayed ingestion, which silently double-counts metrics. |
| 57 | How do you avoid validation blocking on seasonality? | Use window-aware expectations: volume in the same period last week rather than a flat number. |
| 58 | What is a validation suite for? | Grouping expectations under an identity so results are comparable over time and per dataset. |
| 59 | Assumption / invariant to defend: Every expectation has an owner and a threshold with provenance... | Every expectation has an owner and a threshold with provenance |
| 60 | Assumption / invariant to defend: Blocking expectations are rare enough to be trusted when they fire... | Blocking expectations are rare enough to be trusted when they fire |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
