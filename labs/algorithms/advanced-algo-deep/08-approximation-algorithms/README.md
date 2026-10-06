# 08 — Approximation Algorithms

<div align="center">

**Greedy · PTAS · FPTAS · Set Cover · Vertex Cover · Metric TSP**

</div>

---

## Learning Objectives

- Define α-approximation for minimisation and maximisation
- Prove greedy set cover is a Θ(log n)-approximation
- Show the 2-approximation for vertex cover via maximal matching
- Explain the metric TSP 2-approximation from the MST doubling
- Distinguish PTAS from FPTAS and when an FPTAS exists
- State that no polynomial-time PTAS exists for the general TSP (P≠NP)

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Approximation Algorithms

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| Greedy set cover | Θ(|U|·|S|) | Θ(log n) approximation | tight unless P=NP |
| Vertex cover, matching | Θ(V+E) | 2-approximation | gap 2 |
| Metric TSP, MST-doubling | Θ(E log V) | 2-approximation | Christofides: 1.5 |
| Knapsack FPTAS | Θ(n²/ε) | (1-ε)-approximation | value-scaling DP |
| Knapsack exact DP | Θ(n·W) | pseudo-polynomial | not polynomial in log W |
| Set cover lower bound | no (1-o(1))ln n | — | unless P=NP |

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

