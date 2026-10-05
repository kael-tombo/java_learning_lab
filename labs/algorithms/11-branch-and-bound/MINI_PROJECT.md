# MINI_PROJECT — Branch and Bound: Packing Optimizer
> Implement + benchmark + visualize. ~4 hours.

## Goal
Build best-first knapsack B&B with fractional bounds, plot gap-vs-nodes curve, and beat
plain backtracking on correlated instances with timeout guardrails.

## Build Steps
1. `PackOpt.java`: ratio presort, frac bound, PQ best-first, greedy-seeded best.
2. Instrument: nodes explored, fathoms by rule (bound/leaf/infeasible).
3. Visualize: ASCII branch excerpt (`take→ub=12.5 | skip→ub=9.0 ✂ prune`).
4. Benchmark: random vs correlated n=30..60 B&B nodes/ms vs brute (to n=25).
5. Guardrails: timeout + incumbent gap % reported (production pattern).

## Benchmark Table (fill)
| instance | B&B nodes/ms | brute ms | gap closed | winner |
|----------|--------------|----------|------------|--------|
| random 40 | / | — | | B&B |
| correlated 40 | / | — | | B&B |

## Visualize
```
[ub=15.2]─┬take(ub=13.1)─┬take(ub=11.0)★
          └skip(ub=9.0)✂ (bound ≤ best=10)
```

## Acceptance
- [ ] Optimal value matches DP/brute on small (assert).
- [ ] Gap curve included. [ ] Timeout path tested.

## Extensions
- DFS-LIFO vs best-first node-count comparison.
