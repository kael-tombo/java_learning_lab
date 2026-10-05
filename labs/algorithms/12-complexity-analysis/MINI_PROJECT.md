# MINI_PROJECT — Complexity Analysis: Profiler + Doubling Lab
> Implement + benchmark + visualize. ~3 hours.

## Goal
Build the timing harness (warmup + best-of) and classify 3 unknowns (log/linear/quadratic)
 purely from doubling ratios + curves.

## Build Steps
1. `Profiler.java`: `timeMs` + `doubling()` (see CODE_DEEP_DIVE).
2. Unknowns: binary-search / scan / bubble at n=10k..80k (labels hidden, classify by ratio).
3. Visualize: ASCII ratio chart (`n: ms ratio→verdict`).
4. Amortized demo: push-doubling 10⁶ (avg ns/op flat) vs no-reserve linked inserts.
5. Report: verdict table + one-paragraph method note (warmup/reps/DCE guard).

## Benchmark Table (fill)
| unknown | 10k | 20k | 40k | 80k | ratio→verdict |
|---------|-----|-----|-----|-----|---------------|
| A | | | | | ~1 → O(log n) |
| B | | | | | ~2 → O(n) |
| C | | | | | ~4 → O(n²) |

## Visualize
```
A: ▁▁▁▁ ratio 1.1 → log   B: ▁▃▅█ ratio 2.0 → linear
```

## Acceptance
- [ ] All three classified correctly with ratio evidence.
- [ ] Amortized-flat curve included. [ ] DCE guard documented.

## Extensions
- JMH single-benchmark comparison (note overhead delta).
