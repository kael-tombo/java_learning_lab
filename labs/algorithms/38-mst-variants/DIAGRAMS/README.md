# Diagrams — Lab 38: Minimum Spanning Tree Variants

Diagrams for the MST family in this lab: **Kruskal**, **Prim**, **Borůvka**, **cut and cycle properties**, **bottleneck spanning trees**, and **degree-constrained (second-order) MST**.

All diagrams are terminal-renderable ASCII. Each entry names the section of `../THEORY.md` it illustrates and gives a construction recipe for a rendered version.

---

## Diagram inventory

| # | File / construct | Purpose | Format |
|---|-----------------|---------|--------|
| M1 | `mst-worked-example.md` | One 8-vertex graph, edge weights, full Kruskal trace | ASCII |
| M2 | `kruskal-dsu-merge-tree.md` | Which DSU components merge on each accepted edge | ASCII sequence |
| M3 | `prim-growth-tree.md` | Prim's frontier with a priority queue | ASCII |
| M4 | `boruvka-phases.md` | Two-phase rounds, components halving each round | ASCII rounds |
| M5 | `cut-property.md` | The cut `(S, V\S)` and its lightest crossing edge | ASCII |
| M6 | `cycle-property.md` | An MST plus a heavier edge forming a cycle | ASCII |
| M7 | `mst-from-flow.md` | Maximising a spanning tree = minimising `Σ w(e)(d(e)-1)` | ASCII + formula |
| M8 | `bottleneck-mst.md` | Bottleneck `max_e w(e)` minimised by *any* MST | ASCII |
| M9 | `degree-constrained-mst.md` | Second-best MST by an edge-swap argument | ASCII |
| M10 | `mst-in-systems.md` | Where MSTs appear in production (link aggregation, cabling, clustering) | ASCII architecture |

---

## The picture that carries the whole lab (M1)

```
vertices:  0 1 2 3 4 5 6 7
edges (sorted by weight ascending):

  w=1   0-1   3-4
  w=2   1-2   4-5   0-6
  w=3   2-3   5-6   6-7
  w=4   1-7
  w=5   2-7
  w=9   3-7

Kruskal trace:

  #  edge  weight  DSU before                DSU after              accepted?
  1  0-1     1    {{0},{1},{2},{3},{4},{5},{6},{7}}
                             ->{{0,1},{2},{3},{4},{5},{6},{7}}      YES  (m=1)
  2  3-4     1    ->{{0,1},{2},{3,4},{5},{6},{7}}                  YES  (m=2)
  3  1-2     2    ->{{0,1,2},{3,4},{5},{6},{7}}                    YES  (m=3)
  4  4-5     2    ->{{0,1,2},{3,4,5},{6},{7}}                      YES  (m=4)
  5  0-6     2    ->{{0,1,2,6},{3,4,5},{7}}                        YES  (m=5)
  6  2-3     3    ->{{0,1,2,3,4,5,6},{7}}                          YES  (m=6)
  7  5-6     3    both ends in the same component                  REJECT (cycle)
  8  6-7     3    ->{{all 8}}                                       YES  (m=7)  STOP

  MST weight = 1+1+2+2+2+3+3 = 14
  adjacency:  0:{1,6}  1:{0,2}  2:{1,3}  3:{2,4}  4:{3,5}  5:{4}  6:{0,7}  7:{6}

The rejected edge 5-6 (w=3) closes the cycle
  5 - 4 - 3 - 2 - 1 - 0 - 6 - 5        (all other edges have weight <= 3)
```

**Why the rejection is safe:** the cycle contains the edge `2-3` of weight 3 as well; by the **cycle property**, the *heaviest* edge in a cycle is excluded from every MST, and ties can be broken arbitrarily. Kruskal processes in weight order, so when it sees `5-6` every edge in its cycle has already been accepted or is heavier — hence rejection is optimal.

---

## Recommended diagram exercises

1. Draw M1 fully (weight labels, greedy choices, DSU state) and then re-derive the MST with **Prim** from vertex 0. The two must produce the same *weight*, but usually a different *edge set* when there are ties. Note which.
2. Draw M4's Borůvka on M1: round 1 every vertex picks its cheapest incident edge; how many components survive? Verify the claim "the number of components at least halves each round ⇒ `⌈log₂ n⌉` rounds ⇒ `Θ(m log n)`".
3. Draw M5's cut property for the cut `(S={0,1,2}, V\S)`. Find the lightest crossing edge, then *prove* no MST uses only the other edges on the cut. Do the same for three different cuts.
4. Draw M8: take any MST, find its heaviest edge, then show there exists a *different* spanning tree with the same weight but a *smaller* bottleneck — and prove that impossible for an MST (the theorem: **every MST is a minimum-bottleneck spanning tree**).
5. Draw M9: delete one edge of the MST, re-run Kruskal on the remaining edges, add back the removed edge and the cheapest replacement. Explain why this yields a **spanning tree within 2× optimal** for the degree-constrained variant, and why that factor matters for link aggregation (you want the minimum of the *sum* of active links).

---

## Related files

- `../THEORY.md` — cut and cycle properties, the proofs, Kruskal/Prim/Borůvka, bottleneck trees, degree-constrained MST, matroid structure.
- `../MATH_FOUNDATION.md` — `O(m log m)` from sorting, `O(m α(m))` from DSU, Borůvka's `⌈log₂ n⌉` rounds, and the 2-approximation bound.
- `../BENCHMARK/` — where the ASCII tree renderers live; the weights in M1 are reproducible there.