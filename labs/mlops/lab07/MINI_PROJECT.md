# MINI_PROJECT — ML CI Pipeline with an Evaluation Gate

**Track:** mlops  |  **Lab:** lab07  |  **Level:** Intermediate

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

**Brief.** Build a pipeline with fast pre-merge gates and a frozen-set evaluation gate, and prove it catches regressions.

**Timebox.** 3–4 hours

## 1. Why This Project Exists

The regression gate is the highest-value piece of ML CI/CD: it is the difference between discovering a 3% accuracy drop in CI and in a quarterly review.

## 2. Requirements

- Pre-merge pipeline: compile, unit, schema contracts, smoke training on a fixture — under 10 minutes.
- Break a feature transform and prove the smoke stage fails fast.
- Simulate an upstream schema change and prove a contract test catches it before training.
- Freeze and version an evaluation set; run the baseline 6 times to measure variance.
- Derive epsilon from variance; implement a gate that blocks a regressed model and reports the delta.
- Content-addressed per-stage caching with a measured hit rate and no staleness.
- Report time-to-detect for pre-merge and for the post-merge suite, including queue time.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Stage graph with dependencies, budgets and timing | A timed pipeline |
| 2 | 30m | Smoke training on a fixture; break a feature and verify fast failure | A smoke gate that works |
| 3 | 25m | Schema contracts with failing examples | Contracts that catch upstream change |
| 4 | 40m | Freeze eval set; 6 repeat runs; derive epsilon | A defended epsilon |
| 5 | 30m | Implement the gate; show it passing good and failing regressed | A demonstrated block |
| 6 | 30m | Per-stage content-addressed caching; measure hit rates | A cache table and time saving |
| 7 | 25m | Time-to-detect report including queue time | A detection-time comparison |

## 4. Architecture Sketch

```text
 pre-merge (<10 min)              post-merge (scheduled)
   +---------------------+           +--------------------------+
   | compile / unit      |           | full train (cached data) |
   | schema contracts    |           | frozen-set evaluation    |
   | smoke train (fixture)|----------| regression gate -> shadow|
   +---------------------+           +--------------------------+
        |                                    |
   fail fast                        register + shadow deploy
   (broken features,                     promotion via registry gate
    upstream changes)
   cache: content-addressed per stage    report: stage timings, detection time
```

## 5. Implementation Notes

- Break something on purpose; a gate you have not seen fail is a gate you cannot trust.
- Deriving epsilon from six repeat runs takes minutes and saves weeks of noise-driven bypasses.
- Per-stage caches matter: a code change should not invalidate the data snapshot.
- Include queue time in detection time or the comparison is dishonest.

## 6. Deliverables

1. Pre-merge pipeline with a measured duration and two demonstrated failures.
1. Frozen eval set with a variance-derived epsilon.
1. Evaluation gate blocking a regressed model with the delta reported.
1. Cache hit-rate table and a time-to-detect comparison.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Speed | 20% | Pre-merge under 10 minutes with real stages |
| Coverage | 25% | Smoke and contract gates demonstrably catch their bugs |
| Gate quality | 25% | Frozen set, derived epsilon, correct pass/fail behaviour |
| Efficiency | 15% | Content-addressed caching with measured hit rate |
| Honesty | 15% | Detection time includes queue time and is reported |

## 8. Stretch Goals

- Add per-slice evaluation gates with slice-specific minimum sample sizes.
- Implement a nightly drift and stability suite writing to the tracking store.
- Trigger the post-merge suite on model or data change rather than on a schedule.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Pre-merge pipeline: compile, unit, schema contracts, smoke training on a fixture — under 10 minutes.
- [ ] Break a feature transform and prove the smoke stage fails fast.
- [ ] Simulate an upstream schema change and prove a contract test catches it before training.
- [ ] Freeze and version an evaluation set; run the baseline 6 times to measure variance.
- [ ] Derive epsilon from variance; implement a gate that blocks a regressed model and reports the delta.
- [ ] Content-addressed per-stage caching with a measured hit rate and no staleness.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
