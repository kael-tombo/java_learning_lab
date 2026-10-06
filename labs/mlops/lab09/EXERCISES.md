# Data Validation & Quality - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab09
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out DataValidationLab
```

## Exercise 1: Expectation framework

**Task.** A reusable, classified check system.

**Steps**
- Define an Expectation type with severity, threshold and owner.
- Implement null, range, uniqueness and category checks.
- Collect all violations, not just the first.
- Write a suite report.

**Deliverable.** A framework plus a suite report.

## Exercise 2: Schema and contract checks

**Task.** Catch the destructive failures first.

**Steps**
- Declare a schema contract for 3 tables.
- Implement type, nullability and primary key expectations.
- Simulate an upstream type change.
- Confirm the failure blocks before any transformation.

**Deliverable.** A contract that blocks a simulated upstream break.

## Exercise 3: Rate checks with a noise floor

**Task.** Stop alerting on normal variation.

**Steps**
- Implement rate comparison against a reference.
- Generate null-rate series with noise and with a real break.
- Tune the z threshold; show false positives and detection.
- Report the chosen z.

**Deliverable.** A comparison showing the noise floor working.

## Exercise 4: Shape comparison for skewed data

**Task.** Range checks pass while the shape changes.

**Steps**
- Implement a rank-based shape comparison.
- Build a reference and a skewed current distribution.
- Show range checks pass while the comparison fires.
- Compute the critical value for your sample sizes.

**Deliverable.** A demonstration that range checks are insufficient.

## Exercise 5: Blocking versus warning

**Task.** Keep the gate trustworthy.

**Steps**
- Classify 10 expectations by severity.
- Show a warning channel that does not block.
- Inject a blocking violation and verify the pipeline stops.
- Write the routing policy for warnings.

**Deliverable.** A severity policy with a demonstrated block.

## Exercise 6: Freshness and volume

**Task.** Catch upstream stalls first.

**Steps**
- Implement freshness and volume expectations.
- Make volume window-aware for weekly seasonality.
- Simulate a stalled upstream.
- Verify the alert fires before other checks.

**Deliverable.** An alert that catches a stalled pipeline.

## Exercise 7: Quality trends

**Task.** See degradation before failure.

**Steps**
- Store suite results with timestamps.
- Compute the score trend and its slope.
- Alert on sustained slope before a blocking threshold trips.
- Show the lead time gained.

**Deliverable.** A trend alert with a measured lead time.

## Exercise 8: Validate at scale

**Task.** Push checks to the engine.

**Steps**
- Generate 10M rows with injected corruptions.
- Compare sampled versus full validation detection rates.
- Show sampling misses low-frequency corruption.
- Move the checks into a query and measure the speedup.

**Deliverable.** A detection-rate comparison justifying full validation.


---

## Self-Check Before You Move On

- [ ] My blocking gate fires rarely enough that people trust it.
- [ ] My thresholds came from observed history.
- [ ] I validate freshness and volume, not just ranges.
- [ ] I can show the quality trend for any suite.
