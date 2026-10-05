# MINI_PROJECT — Bellman-Ford + Floyd: Negative-Aware Lab
> Implement + benchmark + visualize. ~3 hours.

## Goal
Detect a negative cycle (arbitrage triangle), contrast BF vs Dijkstra on negatives,
and render FW distance-matrix heatmap evolution over k.

## Build Steps
1. `NegLab.java`: BF with detection + FW k-outer with matrix snapshots.
2. Arbitrage: 3-currency rates → −log weights; negative diagonal = profit loop.
3. Visualize: print `d` matrix at k=0,1,n (use `∞` glyph); highlight improved cells.
4. Benchmark: sparse chain BF vs Dijkstra (non-negative) + FW n=50..200 curve (V³).
5. Wrong-order demo: FW with i-outer on crafted graph → wrong cell (assert diff).

## Benchmark Table (fill)
| n (FW) | ms | ratio (~8× per 2n) |
|--------|----|--------------------|
| 50 | | — |
| 100 | | ~8 |
| 200 | | ~8 |

## Visualize
```
k=1: [0,3,∞] [∞,0,2] … k=2: [0,3,5] improved (0,2)
```

## Acceptance
- [ ] Arbitrage cycle printed + verified (product >1).
- [ ] k-order bug demoed. [ ] V³ ratio ≈8× observed.

## Extensions
- Johnson sketch timing on sparse 500-node graph.
