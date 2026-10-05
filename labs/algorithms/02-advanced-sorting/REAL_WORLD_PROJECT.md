# REAL_WORLD_PROJECT — Advanced Sorting in Production: Log Pipeline Sort Stage
> Production use-case: nightly 50M-row log sort for analytics (external + parallel merge).

## 1. Scenario
- Pipeline: 50M events/day must be time-ordered before sessionize join.
- Constraint: 32GB box, 30-min window, stable (same-ms keeps ingest seq).
- Choice: external merge sort (64MB runs) + parallel k-way merge; in-memory `Arrays.sort` per run.
- Keys: `(ts, seq)` composite; spill to SSD; checksum per run.

## 2. Architecture
```
shards → per-shard sort (parallel) → run files → k-way heap merge → sessionize
```
- Run size tuned to L3/page-cache; direct buffers for merge.
- Shuffle not needed (merge has no pivot risk); 3-way quick for in-mem skewed keys.
- Progress + skew metrics per shard (straggler alert).

## 3. War-Story
- Incident: single-threaded quicksort (no shuffle) on sorted-by-producer input → O(n²) stall, window blown by 3×.
- Symptom: one shard at 100% CPU, rest idle; p99 run-sort 22min vs 2min typical.
- Root cause: producer-ordered input = quick worst; no shuffle/median fallback.
- Fix: shuffle + 3-way + run-size cap + skew alert; parallel merge across 8 cores.
- Lesson: adversary is your own upstream order; derandomize by default.

## 4. Metrics (per night, 50M rows)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Sort stage | 94min (blown) | 11min | −88% |
| Slowest shard | 22min | 2.1min | −90% |
| Spill I/O | 210GB | 120GB | −43% |
| Stability violations | 900/day | 0 | −100% |
| Cost/run | $18 | $4.2 | −77% |

## 5. Prevention Checklist
- [ ] Shuffle/median-of-3 default in every quick path.
- [ ] Duplicate-heavy fixture in perf suite.
- [ ] Sorted/reverse inputs in regression (adversarial).
- [ ] Run-size + parallelism autotuned, logged.
- [ ] Stability `(ts,seq)` key enforced + tested.
- [ ] Straggler alert on shard skew >2× median.
- [ ] Stdlib-first for in-mem (`Arrays.sort`/`parallelSort`).
- [ ] Spill checksums + resume on failure.

## 6. What "Good" Looks Like
- 11min stable nightly; no shard >2× median; zero stability tickets.

## 7. Stretch
- Columnar (Parquet) sort keys; radix for integer timestamps.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Java sort/parallelSort behavior: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Quicksort worst-case + mitigations: https://en.wikipedia.org/wiki/Quicksort
