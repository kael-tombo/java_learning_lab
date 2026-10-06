# 07 — Cycle Detection

<div align="center">

**DFS Three-Colour · Union-Find · Floyd's Tortoise-Hare · SCC Decomposition**

</div>

---

## Learning Objectives

- Detect a cycle in a directed graph with the three-colour DFS
- Detect a cycle in an undirected graph with Union-Find
- Explain Floyd's tortoise-hare phase argument and the entry-point formula
- Distinguish back edges from cross/forward edges in a DFS
- Relate cycle detection to the SCC decomposition (Tarjan/Kosaraju)
- Recognise when "cycle detection" is really "dependency deadlock" detection

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Cycle Detection

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| Three-colour DFS | Θ(V+E) | Θ(V) | directed graphs |
| Union-Find scan | Θ(E·α(V)) | Θ(V) | undirected graphs |
| Floyd tortoise-hare | Θ(t+L) | Θ(1) | functional graphs |
| Tarjan SCC | Θ(V+E) | Θ(V) | SCCs = cycles |
| Kosaraju SCC | Θ(V+E) | Θ(V) | two DFS passes |

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

