# Math Foundation — Graph Coloring

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Greedy Δ+1 bound

When colouring vertex v, at most Δ of its neighbours are coloured, so at most Δ colours are forbidden. One of the Δ+1 colours {1,…,Δ+1} is free; assign it.

The bound cannot be improved in general: K_{Δ+1} and odd cycles (Δ=2) both need Δ+1.

## Bipartite iff no odd cycle

If G has an odd cycle, its vertices alternate colours around the cycle and the last vertex conflicts with the first — no 2-colouring exists. Conversely, if G has no odd cycle, BFS from any root assigns colour = depth-parity; a conflicting edge would create an odd cycle.

So G is bipartite ⟺ G is 2-colourable ⟺ G has no odd cycle.

## Brooks' theorem (statement)

Every connected graph G with maximum degree Δ satisfies χ(G) ≤ Δ, unless G is a complete graph or an odd cycle, in which case χ(G) = Δ+1.

The proof is a structural induction on the block-cut tree and the existence of a spanning tree whose leaves are coloured last.

## DSATUR ordering

At each step colour the uncoloured vertex with the largest saturation degree DS(v) = |{colours used by N(v)}|. Saturation is a tight upper bound on the eventual constraint at v, so the vertex with the highest DS is the most constrained and is decided first.

This maximises the information per decision — the same principle as MRV in CSP.

## Greedy can be arbitrarily bad

There exist bipartite graphs (χ=2) on which a greedy colouring uses Θ(n/2) colours: the standard example is a path-like "tree" whose bad ordering forces the greedy pass to keep introducing new colours.

So greedy is a heuristic, not an approximation scheme with a constant ratio.
