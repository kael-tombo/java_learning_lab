# REAL_WORLD_PROJECT — Binary Search in Production: Release Bisect + Range Queries
> Production use-case: regression bisect over 100k builds + timestamp range scans.

## 1. Scenario
- CI keeps 100k ordered builds; on-call bisects first-bad via monotonic `isBad()`.
- Also: event store range query `[t1,t2)` via lower/upper bounds.
- Constraint: each probe = 2-min test; minimize probes (log n ≈ 17 max).
- Choice: half-open bounds, overflow-safe mid, lowerBound core reused everywhere.

## 2. Architecture
```
bisect Temmuz → lowerBound(isBad) → culprit + range links
query [t1,t2) → [lower(t1), lower(t2)) slice
```
- Predicate caching (memo probe results; flaky-test retry with quorum).
- Probe log (`lo,hi,mid→verdict`) for audit + flaky detection.
- Rotated-index variant (canary ring) uses same invariant.

## 3. War-Story
- Incident: `(lo+hi)/2` overflow on 32-bit build ids near 2³¹ → negative mid, infinite loop.
- Symptom: bisect hung at 2B+ builds; on-call killed after 40min, no verdict.
- Root cause: int overflow + closed-interval off-by-one on duplicates (first-bad returned later bad).
- Fix: `>>>1`, half-open, lowerBound (no early return) + hang watchdog (max 32 probes).
- Lesson: boundary code needs overflow + duplicate fixtures, not just happy path.

## 4. Metrics (bisect run)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Probes (100k) | hang (∞) | 17 | fixed |
| MTTR regression | 3h | 45min | −75% |
| Wrong-culprit | 1/8 | 0/40 | −100% |
| Range p99 (10M events) | 120ms (linear) | 4ms | −97% |
| Flaky-misbisect | 2/qtr | 0 | quorum |

## 5. Prevention Checklist
- [ ] `>>>1` + half-open standard (lint).
- [ ] Overflow fixture (ids near MAX_VALUE).
- [ ] Duplicate/first-hit tests (lowerBound, not any-hit).
- [ ] Probe cap + watchdog (fail loud, not hang).
- [ ] Predicate cache + flaky quorum (2/3).
- [ ] Probe audit log per bisect.
- [ ] Sortedness assertion on index load.
- [ ] Range-slice property tests (fuzz vs linear).

## 6. What "Good" Looks Like
- ≤17 probes always; first-bad exact; ranges in single-digit ms.

## 7. Stretch
- Search-on-answer for capacity tuning (min hosts for SLO).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- `Arrays.binarySearch` miss encoding to mirror: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Binary search bounds + overflow history: https://en.wikipedia.org/wiki/Binary_search
