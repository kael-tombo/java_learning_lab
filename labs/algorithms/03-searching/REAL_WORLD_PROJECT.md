# REAL_WORLD_PROJECT — Searching in Production: Versioned Artifact Lookup
> Production use-case: artifact/version retrieval across registries (mixed orderings).

## 1. Scenario
- Deploy service resolves `(service, version)` across 3 registries: unsorted spillover,
- sorted releases, hashed cache. 20k QPS, p99 15ms.
- Choice: dispatch — cache hash → sorted binary → linear spillover (+sort-if-hot).
- Miss encoding unified (`-(insert+1)` style) for range/bisect reuse.

## 2. Architecture
```
query → L1 hash (hot) → L2 sorted binary (releases) → L3 linear scan (spillover)
```
- Spillover sorted nightly if q* break-even crossed (measured).
- Comparator single-sourced with sort job (drift detector compares orders).
- Bloom prefilter for absent versions (cuts L3 scans 80%).

## 3. War-Story
- Incident: sort job changed comparator (case-insensitive) but binary probe stayed sensitive.
- Symptom: 2% versions "missing" despite present; bisect discarded correct half.
- Root cause: order/probe skew — sortedness precondition violated silently.
- Fix: shared comparator artifact + order assertion (isSorted sample per deploy).
- Lesson: searching is a contract between writer (sort) and reader (probe).

## 4. Metrics (20k QPS)
| Metric | Before (skewed) | After | Delta |
|--------|-----------------|-------|-------|
| False-miss | 2.0% | 0.01% | −99.5% |
| p99 lookup | 34ms | 9ms | −74% |
| L3 scans/s | 4100 | 800 | −80% |
| Cache hit | 71% | 88% | +17pp |
| MTTD skew | days | minutes | detector |

## 5. Prevention Checklist
- [ ] One comparator for sort + probe (shared lib).
- [ ] `isSorted` sample gate on deploy.
- [ ] Unified miss encoding + tests.
- [ ] Workload-winner matrix in design doc.
- [ ] Bloom FP budget stated (e.g., 1%).
- [ ] Sort-amortization logged (sortMs/q).
- [ ] Mutation suite (insert cost) for registry growth.
- [ ] Replay log for miss disputes.

## 6. What "Good" Looks Like
- p99 <10ms; misses explainable (Bloom + encoding); no order drift.

## 7. Stretch
- Interpolated search on uniform version ints; history sharding.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Binary search contract + insertion-point encoding: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Search algorithm landscape: https://en.wikipedia.org/wiki/Search_algorithm
