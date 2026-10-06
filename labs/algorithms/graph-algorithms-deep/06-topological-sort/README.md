# 06 — Topological Sort

<div align="center">

**Kahn's Algorithm · DFS-Based Ordering · DAG Recognition · Cycle Check**

</div>

---

## Learning Objectives

- Prove a topological order exists iff the graph is a DAG
- Implement Kahn's BFS in-degree reduction and explain its Θ(V+E) cost
- Implement the DFS-based topological order (reverse post-order)
- Use a topological order to evaluate a DAG of dependencies
- State why a cycle makes a topological order impossible
- Recognise problems that are really "order a DAG of prerequisites"

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Topological Sort

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| Kahn's algorithm | Θ(V+E) | Θ(V) | in-degree queue |
| DFS post-order | Θ(V+E) | Θ(V) | reverse post-order |
| Cycle detection via Kahn | Θ(V+E) | Θ(V) | unoutputted vertices |
| DAG longest path | Θ(V+E) | Θ(V) | relax in topo order |
| Dependency build order | Θ(V+E) | Θ(V) | the topological order itself |

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

