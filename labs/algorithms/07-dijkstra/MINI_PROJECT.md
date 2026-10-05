# MINI_PROJECT — Dijkstra: City Router + Heap Shootout
> Implement + benchmark + visualize. ~4 hours.

## Goal
Route on a city grid graph, draw settled-wavefront animation, and benchmark binary-heap
vs naive O(V²) vs early-exit single-target.

## Build Steps
1. `Router.java`: grid→graph (4-neighborhood, random weights 1–9), Dijkstra + prev[].
2. Visualize: ASCII wavefront per 10% settled (`·` settled, `?` frontier, `*` path).
3. Path overlay + total cost; unreachable test (walled district → INF).
4. Benchmark: grids 50²/100²/200² heap vs naive; single-target early-exit saving %.
5. Negative demo: inject one −5 edge; show wrong answer + reroute to Bellman-Ford.

## Benchmark Table (fill)
| grid | heap ms | naive ms | early-exit save | dist |
|------|---------|----------|-----------------|------|
| 50² | | | % | |
| 100² | | | % | |
| 200² | | | % | |

## Visualize
```
S·······
·*****·?
·······T  (* = route, cost=42)
```

## Acceptance
- [ ] Wavefront frames + path overlay included.
- [ ] Stale-skip counter printed (duplicates observed).
- [ ] Negative-breaker documented with correct dispatch.

## Extensions
- Bidirectional Dijkstra; A* with Manhattan heuristic.
