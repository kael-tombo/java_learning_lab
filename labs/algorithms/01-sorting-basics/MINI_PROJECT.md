# MINI_PROJECT — Sorting Basics: Sort Lab + Benchmark + Visualize
> Implement + benchmark + visualize. ~3 hours.

## Goal
Build a CLI that runs bubble/insertion/selection on random/nearly-sorted/reverse arrays,
prints ASCII bars per pass, and reports a timing table proving `Θ(n²)` scaling.

## Build Steps
1. `SortLab.java`: `bubble()`, `insertion()`, `selection()` with swap/compare counters.
2. Generator: random (seed 42), nearly-sorted (10 swaps), reverse, all-equal.
3. Visualize: after each outer pass print bar row, e.g. `▇▇▃▅ (pass 3)`.
4. Benchmark: n=1k,2k,4k,8k × 3 trials, best-of; compute doubling ratios.
5. Stability check: sort pairs `(key,id)`; assert original order for equal keys (insertion stable).

## Benchmark Table (fill)
| n | bubble ms | insertion ms | selection ms | ratio (2n/n) |
|---|-----------|--------------|--------------|--------------|
| 1000 | | | | — |
| 2000 | | | | ~4.0 expected |
| 4000 | | | | ~4.0 |
| 8000 | | | | ~4.0 |

## Visualize (example output to reproduce)
```
pass 1: ▅▃▇▂▅
pass 2: ▃▅▂▅▇
sorted: ▂▃▅▅▇ comps=10 swaps=6
```

## Acceptance
- [ ] Ratios ≈4× (quadratic signature) + insertion wins nearly-sorted.
- [ ] ASCII trace for n=12 included in README snippet.
- [ ] Stability verdict documented per algorithm.

## Extensions
- Cutover demo: insertion for n<32 inside merge (preview advanced lab).
- Export CSV + plot curve (quadratic fit).
