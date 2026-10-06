# 05 — Graph Coloring

<div align="center">

**Greedy Coloring · Brooks' Theorem · Bipartite 2-Coloring · DSATUR · Chromatic Number**

</div>

---

## Learning Objectives

- State why a greedy colouring uses at most Δ+1 colours
- Prove a graph is bipartite iff it is 2-colourable iff it has no odd cycle
- Apply DSATUR to improve greedy colouring in practice
- Recognise when chromatic number is NP-hard to compute
- State Brooks' theorem and its exceptions
- Use colouring as a model for scheduling with conflict constraints

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Graph Coloring

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| Greedy colouring | Θ(V+E) | Θ(V+E) | any fixed order |
| DSATUR | Θ((V+E)·log V) with a heap | Θ(V) | saturation-degree order |
| Bipartite test | Θ(V+E) | Θ(V) | BFS 2-colouring |
| χ computation | NP-hard | — | 3-colourability is NP-complete |
| Interval-graph greedy | Θ(E log V) | Θ(V) | optimal for interval graphs |

## Files

| File | Purpose |
|------|---------|
| `src/main/java/...` | Reference implementation |
| `src/test/java/...` | Cross-validation tests |
| `SOLUTION/` | Worked exercise solutions |
| `TESTS/` | Boundary-value suites |
| `BENCHMARK/` | Benchmarks |
| `MINI_PROJECT/` | Small project |
| `REAL_WORLD_PROJECT/` | End-to-end project |
| `CHALLENGE/` | Hard variants |
| `DIAGRAMS/` | Visual guides |

