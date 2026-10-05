# REAL_WORLD_PROJECT — Divide and Conquer in Production: Parallel Sessionize Pipeline
> Production use-case: 50M events → sorted sessions via parallel D&C (sort + count).

## 1. Scenario
- Analytics must sessionize 50M sorted events + count inversions (disorder metric).
- Constraint: 8 cores, 15-min window; work/span budgeted upfront.
- Choice: parallel mergesort (buffer-once) + inversion combine; ForkJoin halves.
- Output: sessions + disorder score per shard.

## 2. Architecture
```
shards → parallel sort/count (ForkJoin, cutoff 32k) → k-way merge → sessions
```
- Buffer allocated once per shard (not per call); cutoff tuned by sweep.
- Span `O(log²n)` naive → `O(log n)` pipelined merge (documented).
- Inversion `long` (5·10⁹+ at scale); `<=` stability documented.

## 3. War-Story
- Incident: per-call buffer alloc → 8× memory (256GB attempted), GC death spiral.
- Symptom: 15-min window → 2h + OOM kills on 3 workers.
- Root cause: `new int[n]` inside recursion (O(n log n) space); no cutoff (task storm).
- Fix: buffer-once + cutoff 32k + task-cap; span measured, not guessed.
- Lesson: D&C space discipline (buffer-once) matters as much as time recurrence.

## 4. Metrics (50M events, 8 cores)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Sessionize | 2h+ (OOM) | 9min | −92% |
| Peak mem | 256GB (ask) | 18GB | −93% |
| Speedup | 0.6× (slower) | 5.8× | 9.7× |
| Inversion exact | overflow (int) | exact (long) | fixed |
| Task count | 3.2M | 4k | −99.9% |

## 5. Prevention Checklist
- [ ] Buffer-once (alloc audit in review).
- [ ] Cutoff sweep recorded (8/16/32k).
- [ ] `long` counts + overflow test.
- [ ] Span measured (not just work).
- [ ] Task-cap + work-stealing notes.
- [ ] Stability (`<=`) test.
- [ ] Brute-oracle fuzz (small n).
- [ ] Overflow-safe mid (`>>>1`).

## 6. What "Good" Looks Like
- 9min stable; 5×+ speedup; disorder metric exact.

## 7. Stretch
- Strassen/Karatsuba note for big-int session keys (not default).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- ForkJoin + parallel sort utilities: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Divide-and-conquer work/span model: https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm
