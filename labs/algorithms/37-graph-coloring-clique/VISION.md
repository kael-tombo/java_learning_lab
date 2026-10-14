# VISION — Graph Coloring and Cliques
> Direction: from coloring-by-feel to bracketed answers — a lower bound from cliques, an upper bound from a real coloring, and the gap stated aloud.

## Where this sits
- Greedy uses at most Delta+1 colors; order decides how close to optimal. Welsh-Powell (degree order) is the cheap upgrade; DSATUR (saturation order) the next step.
- Bron-Kerbosch enumerates maximal cliques; max-clique size omega lower-bounds chromatic number chi. 3-colorability is NP-complete, so brackets beat exactness at scale.
- Register allocation, timetabling, and frequency assignment are the same picture with different labels.

## 4-week direction
- Week 1: hand-color the reference graph in order 0..4 and in degree order; reproduce both outputs.
- Week 2: finish MINI_PROJECT; run all four test graphs and fill the bracket table.
- Week 3: find an order that makes greedy strictly worse than WP on some graph; keep it as a regression test.
- Week 4: REAL_WORLD_PROJECT review; whiteboard omega <= chi and the Delta+1 bound in 10 minutes.

## Done criteria
- Prove the Delta+1 bound from the greedy rule without notes.
- Explain why the reference graph has chi exactly 3 (clique below, coloring above).
- Choose greedy vs WP vs exact search for a given (n, density, deadline) triple.

## Non-coverage
- This lab does not implement DSATUR, branch-and-bound coloring, or pivoted BK (named as next steps with reasons).
- No approximation-ratio theorems; the bracket is empirical per instance.
- Perfect-graph theory is referenced, not developed.

## Pitfalls
- Reporting colors without the clique bound; a number without a bracket is marketing.
- Assuming degree order is optimal; it is a heuristic with known failures.
- Letting BK run exact on dense 500-vertex graphs; guard and label substitutions.

## Adjacent labs
- Pair with 38-mst-variants for the exchange-argument proof style and 32-exact-exponential for BK as exponential enumeration done right.
- Revisit before hand-coloring any conflict problem; the bracket habit replaces optimism.

## Weekly drills
- Prove Delta+1 from the greedy rule aloud in under 2 minutes.
- Reproduce both reference colorings and the clique {0,1,2} from memory.
- State omega <= chi and apply it to pin chi on a fresh small graph.

## Anti-roadmap
- Do not publish colors without the clique bound on the same page.
- Do not run exact clique search on dense large graphs without a guard and a labeled fallback.
