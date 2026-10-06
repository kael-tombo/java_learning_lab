# MINI_PROJECT — Data Quality Suite with a Trustworthy Gate

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

**Brief.** Build a validation suite with schema, domain, distribution and freshness checks, and make the blocking gate reliable.

**Timebox.** 3 hours

## 1. Why This Project Exists

Every silent model failure in practice begins as a data failure that nobody validated. This suite is the antidote.

## 2. Requirements

- Expectation framework with severity, threshold, owner and threshold provenance.
- Schema contract for 3 tables: columns, types, nullability, primary key.
- Domain expectations: ranges, categories, uniqueness, duplicate rate.
- Distribution check that fires when a range check passes (skewed data).
- Rate comparisons against a reference with a sampling-noise floor.
- Freshness and window-aware volume checks that catch a stalled upstream.
- Quality trends with a slope alert that beats the blocking threshold.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Expectation framework collecting all violations | A suite report with every failure |
| 2 | 30m | Schema contract; simulate an upstream type change | A contract that blocks the break |
| 3 | 25m | Domain expectations with owners and severities | A classified expectation set |
| 4 | 30m | Distribution check on skewed data | A case where ranges pass and shape fails |
| 5 | 30m | Rate comparison with a noise floor | A tuned z with demonstrated behaviour |
| 6 | 30m | Freshness plus window-aware volume; simulate a stall | An early alert on a stalled pipeline |
| 7 | 25m | Quality trends with slope alerting; measure lead time | A trend alert with lead time |

## 4. Architecture Sketch

```text
 dataset version
      |
 [1] schema contract (columns, types, nullability, PK)  -> BLOCKING
 [2] domain (range, category, uniqueness, duplicates)     -> mixed
 [3] distribution (rank shape vs reference)              -> warning
 [4] rates vs reference with noise floor                 -> warning
 [5] freshness + window-aware volume                     -> BLOCKING
      |
 ValidationResult (all violations, weighted score, blocking list)
      |
 quality trend store -> slope alert (before the blocking threshold)
      |
 pipeline gate: block if any BLOCKING expectation violates
```

## 5. Implementation Notes

- Collect every violation; an operator debugging at 3 a.m. needs the list, not the first failure.
- Generate your own noise so you can see false positives before you tune anything.
- Inject a 0.5% corruption and test whether sampling catches it; it will not.
- The freshness and volume checks should fire before anything else when an upstream stalls.

## 6. Deliverables

1. Expectation framework plus a suite report listing all violations.
1. Schema contract that blocks a simulated upstream type change.
1. Distribution check demonstration on skewed data.
1. Quality trend with slope alerting and a measured lead time.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 25% | All violations reported; schema blocks; severities applied |
| Statistical soundness | 25% | Rate comparison uses a noise floor; distribution check detects shape change |
| Coverage | 20% | Schema, domain, distribution, freshness and volume all present |
| Trustworthiness | 20% | Blocking gate fires rarely; thresholds from history |
| Operations | 10% | Trends stored with slope and a lead-time measurement |

## 8. Stretch Goals

- Push predicates into a query engine and validate 10M rows.
- Add anomaly detection over the suite score series.
- Attach validation metadata to a model version so consumers see the data state.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Expectation framework with severity, threshold, owner and threshold provenance.
- [ ] Schema contract for 3 tables: columns, types, nullability, primary key.
- [ ] Domain expectations: ranges, categories, uniqueness, duplicate rate.
- [ ] Distribution check that fires when a range check passes (skewed data).
- [ ] Rate comparisons against a reference with a sampling-noise floor.
- [ ] Freshness and window-aware volume checks that catch a stalled upstream.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
