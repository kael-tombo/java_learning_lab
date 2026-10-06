# Feature Store Architecture - Exercises

**Track:** mlops  |  **Lab:** lab04  |  **Level:** Intermediate

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab04
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out FeatureStoreLab
```

## Exercise 1: Design the feature view contract

**Task.** Get the semantics right before the code.

**Steps**
- Define an entity, 4 features, owners, TTLs and staleness tolerances.
- Document units, null semantics and lookback windows.
- Write the version bump policy.
- Implement a registry that rejects views without owners.

**Deliverable.** A documented contract plus a registry that enforces it.

## Exercise 2: One transform, two stores, verified

**Task.** The anti-skew property, demonstrated.

**Steps**
- Implement a single transformation.
- Materialise to offline and online from it.
- Write a parity test over a sample of entities.
- Break the online path and watch parity fail.

**Deliverable.** A passing parity test and a failing one when you break it.

## Exercise 3: Point-in-time joins done correctly

**Task.** Prove the leak and fix it.

**Steps**
- Build events with a feature that includes future information.
- Show a naive join producing optimistic CV accuracy.
- Implement the lookback join and re-measure.
- Quantify the optimism you removed.

**Deliverable.** A quantified leakage number and the corrected accuracy.

## Exercise 4: Freshness monitoring

**Task.** Catch stale features before users do.

**Steps**
- Record event and write timestamps per feature.
- Compute freshness and the staleness rate.
- Break an upstream job and show the alert firing.
- Define TTL per feature from its staleness tolerance.

**Deliverable.** An alert that fires on a broken upstream.

## Exercise 5: Online read batching and latency

**Task.** Make the serving path fast enough.

**Steps**
- Implement per-feature reads; measure p50/p99.
- Implement batched reads; measure again.
- Find the feature that dominates payload size.
- Set and test a latency budget.

**Deliverable.** A before/after latency table with a budget.

## Exercise 6: Materialisation lag attribution

**Task.** Know which stage to fix.

**Steps**
- Measure ingest, compute and write lag per run.
- Plot the distribution over 20 runs.
- Identify the dominant stage.
- Fix it and re-measure.

**Deliverable.** A lag attribution table and a measured improvement.

## Exercise 7: Versioning and deprecation

**Task.** Change features without breaking consumers.

**Steps**
- Version a feature view; show old and new both materialise.
- Track which models used which version.
- Add a deprecation path with a notice period.
- Migrate a consumer and show the old version retired.

**Deliverable.** A versioning scheme with a working deprecation.

## Exercise 8: Reuse and adoption

**Task.** Make the case for the platform with numbers.

**Steps**
- Track features defined versus reused across teams.
- Compute reuse ratio per team.
- Find the most-duplicated feature and consolidate it.
- Report the storage and latency saving.

**Deliverable.** An adoption report with a measured saving.


---

## Self-Check Before You Move On

- [ ] I can name the feature definition feeding both stores.
- [ ] My training joins are point-in-time correct.
- [ ] I alert on staleness, not only on pipeline success.
- [ ] My online reads are batched and within the latency budget.
