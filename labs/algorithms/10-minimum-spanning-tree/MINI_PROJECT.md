# MINI_PROJECT — MST: Cheapest Network + Shootout
> Implement + benchmark + visualize. ~3 hours.

## Goal
Wire mock cities cheapest (Kruskal vs Prim agree), draw MST overlay on ASCII map,
and report $ savings vs star-from-capital baseline.

## Build Steps
1. `Network.java`: random cities (x,y), complete graph (Euclidean weights).
2. Kruskal + Prim + validator (V−1 edges, acyclic, weight equal).
3. Visualize: ASCII map with `*` MST edges vs `·` skipped; print total + baseline.
4. Benchmark: sparse (E≈5V) vs dense (complete 500 nodes) Kruskal-vs-Prim ms.
5. Tie/negative tests: uniform-weight + one −5 edge (must be taken).

## Benchmark Table (fill)
| graph | Kruskal ms | Prim ms | MST weight | star weight | saved % |
|-------|------------|---------|------------|-------------|---------|
| sparse 10⁴ | | | | | |
| dense 500 | | | | | |

## Visualize
```
A---*B
| ···|
D---*C  (* = MST, total=3.2 vs star 5.1)
```

## Acceptance
- [ ] Weight agreement + validator green. [ ] Savings % computed.
- [ ] Dense/sparse winner differs with reason (sort vs heap).

## Extensions
- Second-best MST edge-swap; clustering by cutting k−1 longest MST edges.
