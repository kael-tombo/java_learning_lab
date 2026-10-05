# MINI_PROJECT — Backtracking: Queens Visualizer + Counter
> Implement + benchmark + visualize. ~3 hours.

## Goal
Animate queen placements, count 4/8-queens exactly, and measure prune power (naive vs
bitsets vs ordering) with node counts.

## Build Steps
1. `Queens.java`: bitset place/remove + ASCII board per depth (n=4 full trace).
2. Counters: nodes visited, prunes; assert counts 4→2, 8→92.
3. Benchmark: naive sets vs bitmask vs +symmetry on n=8..10 (nodes + ms).
4. Visualize: board snapshots + search-tree excerpt (`r0:c1 → r1:××pruned`).
5. Subsets sidecar: enumerate 2ⁿ for n=16 with take/skip trace sample.

## Benchmark Table (fill)
| n | naive nodes/ms | bitset nodes/ms | +sym nodes/ms |
|---|----------------|-----------------|---------------|
| 8 | / | / | / |
| 9 | / | / | / |

## Visualize
```
.Q..  (r0 c1)
...Q  (r1 c3 ✗ diag → backtrack)
```

## Acceptance
- [ ] Exact counts asserted. [ ] Node-count reduction quantified.
- [ ] Undo (not copy-per-node) evidenced by design + profile.

## Extensions
- Sudoku propagation sidecar; Held-Karp memo on 12-city TSP.
