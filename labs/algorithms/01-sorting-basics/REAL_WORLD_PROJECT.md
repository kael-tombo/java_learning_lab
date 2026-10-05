# REAL_WORLD_PROJECT — Sorting Basics in Production: Service-Side Log Ordering
> Production use-case: small in-memory sorts behind admin log viewer + DB ORDER BY awareness.

## 1. Scenario
- Service: ops console lists last 500 error events; user sorts by time/severity.
- Constraint: tiny n (<1000), latency budget 50ms p99, stability required (equal timestamps keep ingest order).
- Choice: insertion sort for nearly-sorted (append-mostly) + `Collections.sort` (TimSort) default path.
- Data: `LogEvent{ts, severity, msg, seq}`; comparator chain severity→ts→seq.

## 2. Architecture
```
ingest → ring buffer (500) → copy-on-read → insertion/Collections.sort → paginate
```
- Copy-on-read avoids mutating shared buffer (concurrency).
- Comparator single source (used by both DIY + stdlib) — consistency.
- Feature flag `sort.impl=stdlib|insertion` for comparison in prod.

## 3. War-Story (plausible, representative)
- Incident: bubble sort left in handler; reverse-filtered view (500 items) took 400ms p99.
- Symptom: UI spinner on severity-sort; traces showed O(n²) compares + swap churn.
- Root cause: intern demo code shipped; nearly-sorted assumption undocumented, stability broken (seq ignored).
- Fix: insertion for n<64 runs + TimSort fallback; comparator adds `seq` tiebreak.
- Lesson: basics are fine at small n, but document assumptions + measure.

## 4. Metrics (before → after, staging n=500)
| Metric | Before (bubble) | After (insertion/stdlib) | Delta |
|--------|-----------------|--------------------------|-------|
| p50 sort | 18ms | 1.2ms | −93% |
| p99 sort | 410ms | 3.1ms | −99% |
| Compares | ~125k | ~2k | −98% |
| Stability violations/1k | 14 | 0 | −100% |
| Alloc/op | O(1)+churn | O(n) copy once | cleaner |

## 5. Prevention Checklist
- [ ] Complexity comment on every hand sort (`O(n²) ok iff n<…`).
- [ ] Stability test with `(key,seq)` pairs in CI.
- [ ] Benchmark gate: n=500/5k timings in PR.
- [ ] Default to stdlib; DIY only with measured reason.
- [ ] Comparator unit tests (transitivity, nulls, tiebreak).
- [ ] Copy-on-read or documented in-place contract.
- [ ] Flag to flip implementations without deploy.
- [ ] Dashboard: sort latency histogram by view.

## 6. What "Good" Looks Like
- p99 <5ms at n=500; zero stability complaints; choice logged per request (debug).

## 7. Stretch
- Graduate path: external merge when n→10⁶ (see advanced-sorting lab).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Java sort contract + TimSort stability: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Sorting algorithm taxonomy + stability: https://en.wikipedia.org/wiki/Sorting_algorithm
