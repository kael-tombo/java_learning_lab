# Diagrams — Lab 37: Graph Coloring & Clique

Diagrams for the colouring and clique families in this lab: **greedy colouring**, **DSATUR**, **k-colouring decision**, **clique/independent-set duality**, and **branch-and-bound maximum clique**.

All diagrams are terminal-renderable ASCII so they survive a diff and an IDE preview. Each entry names the section of `../THEORY.md` it illustrates and gives the construction recipe for a rendered version.

---

## Diagram inventory

| # | File / construct | Purpose | Format |
|---|-----------------|---------|--------|
| C1 | `greedy-colouring-order.md` | Same graph, six vertex orders → six different colour counts | ASCII grid |
| C2 | `dsatur-priority-queue.md` | Saturation-degree selection, step by step | ASCII sequence |
| C3 | `chromatic-number-vs-clique.md` | `χ ≥ ω`, and the four-vertex graphs where `χ > ω` | ASCII gallery |
| C4 | `clique-independent-set.md` | The duality `α(G)·χ(G) ≥ n` and complement mapping | ASCII |
| C5 | `max-clique-branch-bound.md` | The search tree with `|C| + |P| ≤ ω*` pruning | ASCII tree |
| C6 | `greedy-k-colouring-proof.md` | The `Δ+1` guarantee proof, diagrammatically | ASCII |
| C7 | `list-colouring-degree-list.md` | Per-vertex lists and feasibility | ASCII |
| C8 | `colouring-in-systems.md` | Where graph colouring appears in production | ASCII architecture |
| C9 | `chordal-perfect.md` | A chordal graph and its perfect elimination ordering | ASCII |
| C10 | `five-colour-theorem.md` | Planar triangulation → `χ ≤ 5`; K₅ as the tight example | ASCII |

---

## The picture that carries the whole lab (C1)

```
Graph:   a--b      h is adjacent to {a, b, c, f}
         |  |      i is adjacent to {d, e}
         a--c      j is adjacent to {a, d, e}
         |  |      k is adjacent to {b, c, d, e, f, i, j}   <- maximum degree
         b--d      hmm, use this one instead:
         c--e      h--i, i--j, j--k, k--f
         d--f

  degree: a=2 b=2 c=2 d=2 e=2 f=2 g=2 h=1 i=2 j=2 k=2

Six orders, six colourings:

order  a,b,c,d,e,f   colours: a1 b2 c3 d3 e4 f4   -> 4 colours
order  k,f,e,d,c,b   colours: k1 f2 e2 d3 c4 b4   -> 4 colours
order  a,c,b,d,e,f   colours: a1 c2 b3 d3 e3 f2   -> 3 colours   <-- better
order  f,d,e,c,b,a   colours: f1 d2 e3 c4 b3 a1   -> 4 colours
order  b,a,c,d,e,f   colours: b1 a2 c3 d3 e3 f4   -> 4 colours
order  a,b,d,c,e,f   colours: a1 b2 d3 c4 e4 f3   -> 4 colours
```

**The point:** greedy colouring produces a *valid* colouring whose quality depends entirely on the order, and no local rule guarantees optimality. `DSATUR` and branch-and-bound exist to fix that.

---

## Recommended diagram exercises

1. Draw C1 for the **Grötzsch graph** (11 vertices, triangle-free but `χ = 4`) — greedy gives 4, and no algorithm is wrong.
2. Draw C3's gallery: `C₅` (odd cycle, `χ=3, ω=2`), `C₇`, `K₃₃`, `K₅`, and the Grötzsch graph. Fill in `(χ, ω, α)` for each and verify `χ ≥ ω` and `α·χ ≥ n`.
3. Draw C5's branch-and-bound tree for a 12-vertex graph and mark every pruned node with the bound value that justified it. Then verify: **no pruned node could contain a larger clique** — that is the correctness obligation of the diagram.
4. Draw C9's perfect elimination ordering for a chordal graph and confirm that each vertex's later neighbours form a clique.

---

## Related files

- `../THEORY.md` — mechanisms: greedy, `Δ+1`, Brooks' theorem, DSATUR, `k`-colouring, clique search, chordal/perfect graphs.
- `../MATH_FOUNDATION.md` — the `Δ+1` proof sketch, `α·χ ≥ n`, the four-colour theorem, and the `O(n^3)` matroid partition characterisation.
- `../BENCHMARK/` — colour counts and DSATUR versus greedy on the same graphs; the numbers quoted in C1 come from there.