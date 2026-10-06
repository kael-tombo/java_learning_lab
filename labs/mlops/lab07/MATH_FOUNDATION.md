# CI/CD for ML Pipelines - Mathematical Foundations

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

## Notation

| Symbol | Meaning |
|---|---|
| `pipeline_time = code + data + features + smoke` | Pre-merge budget - must fit a reviewer's patience |
| `delta = metric(candidate) - metric(baseline)` | Gate evaluation - on a frozen eval set |
| `promote if delta > -epsilon` | Regression gate - declared, not observed |
| `cache_key = hash(commit, data_version, lockfile)` | Cache validity - content-addressed, not time-based |
| `smoke_coverage = cases / total_cases` | Fixture size - small but representative |
| `time_to_detect = merge_to_alert` | Pipeline value - the number CI optimises |

## Why the Math Matters

CI/CD for ML is queueing theory applied to correctness: how long a signal takes to reach a human, and whether it is trustworthy enough to block them.


---

## 1. Pre-merge time budget

```text
T_premerge = build + unit + contract + smoke
target: T_premerge < 10 min (a reviewer's attention span)
T_full runs post-merge
```

The value of a pre-merge gate decays sharply with wait time. Beyond ten minutes, engineers route around it, and a bypassed gate is worse than no gate because it creates false confidence.

**Worked example.** build 90 s, unit 120 s, contracts 45 s, smoke 180 s = 7.25 min, acceptable. Adding full training (95 min) makes it 102 min, so full training moves post-merge and the pre-merge budget is preserved.


---

## 2. Regression gate

```text
delta = metric(candidate) - metric(baseline)
pass if delta >= -epsilon
epsilon set from historical run-to-run variance
```

The epsilon must come from observed variance, not taste. If the same code produces metrics varying by 0.4%, an epsilon of 0.1% fails randomly and gets ignored within a week.

**Worked example.** Baseline 0.912. Historical repeat-run sigma = 0.004, so epsilon = 3 sigma = 0.012. A candidate at 0.905 (delta -0.007) passes; 0.890 (-0.022) fails.


---

## 3. Cache validity

```text
key = SHA256(commit + data_version + lockfile_hash)
hit only if all three match
cache data snapshot, feature materialisation, dependency cache
```

Time-based invalidation is the classic mistake: the cache looks fresh while serving last week's data. Content addressing makes a stale cache structurally impossible.

**Worked example.** Commit changed but data version did not: key differs, so the data cache misses even though it could safely hit. Committing to per-stage keys (code, data, features) recovers the hit rate without risking staleness.


---

## 4. Pipeline duration as a metric

```text
effective_time_to_detect = T_pipeline + T_queue + T_review
for a nightly pipeline: T_queue is hours, so total detection is dominated by the schedule
```

Moving a check earlier reduces detection time only if it also moves off the queue. A fast pre-merge check and a slow nightly gate are complementary, not alternatives.

**Worked example.** Full evaluation nightly: T_pipeline 95 min, queue 0 (fixed schedule) = detection up to 24h. Moving a smoke check pre-merge: T 7 min, queue ~0.05 min = detection in minutes. Total coverage is the union.


---

## Cheat Sheet

- `pipeline_time = code + data + features + smoke` - Pre-merge budget
- `delta = metric(candidate) - metric(baseline)` - Gate evaluation
- `promote if delta > -epsilon` - Regression gate
- `cache_key = hash(commit, data_version, lockfile)` - Cache validity
- `smoke_coverage = cases / total_cases` - Fixture size
- `time_to_detect = merge_to_alert` - Pipeline value

## Numerical Traps

- Putting full training in pre-merge and watching engineers bypass CI.
- Setting epsilon below the historical run-to-run variance.
- Keying caches by time instead of content hash.
- Moving a check earlier without reducing queue time, and calling it faster detection.
- Letting CI promote to production because the gate was green.

## Self-Check Problems

1. Break a 100-minute pipeline into a pre-merge budget and a post-merge schedule, and justify the split.
2. Compute epsilon from six repeat runs of the same code, then decide the gate threshold.
3. Design a three-stage cache key scheme that recovers hit rate without staleness.
4. Compare detection time for a nightly-only gate versus pre-merge plus nightly, including queue time.
5. Write the contract tests needed to catch a breaking upstream schema change.
