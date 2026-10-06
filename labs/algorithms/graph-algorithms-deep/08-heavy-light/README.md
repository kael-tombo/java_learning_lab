# 08 — Heavy-Light Decomposition

<div align="center">

**HLD · Path Queries · Segment Trees on Trees · LCA · Chain Heads**

</div>

---

## Learning Objectives

- Define a heavy edge and the heavy-light decomposition of a rooted tree
- Prove each root-to-node path crosses O(log n) light edges
- Reduce path queries to O(log n) segment-tree queries on the base array
- Implement LCA via heavy-light in O(log n)
- Distinguish path queries from subtree queries and pick the right structure
- State the complexity of HLD path-aggregate queries: Θ(log² n)

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Heavy-Light Decomposition

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| HLD construction | Θ(n) | Θ(n) | two DFS passes |
| Path query (HLD+segtree) | Θ(log² n) | Θ(log² n) | O(log n) segments × O(log n) range query |
| LCA via HLD | Θ(log n) | — | chain jumps |
| Subtree query via Euler tour | Θ(log n) | Θ(log n) | one range query |
| Binary-lifting LCA (alternative) | Θ(log n) | — | Θ(n log n) preprocess |

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

