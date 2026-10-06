# 04 — Geometry Algorithms

<div align="center">

**Cross Products · Convex Hull · Line Intersection · Point-in-Polygon · Closest Pair**

</div>

---

## Learning Objectives

- Classify orientation of three points with the sign of a 2D cross product
- Implement Andrew's monotone-chain convex hull in Θ(n log n)
- Derive the orientation test and robust predicate from integer coordinates
- Define point-in-polygon and the ray-casting parity rule
- State the closest-pair divide-and-conquer Θ(n log n) merge
- Recognise degenerate cases: collinear points, duplicate points, horizontal segments

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Computational Geometry

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| Orientation predicate | Θ(1) | Θ(1) | exact with long arithmetic |
| Monotone-chain hull | Θ(n log n) | Θ(n) | sort + linear scan |
| Segment intersection test | Θ(1) | Θ(1) | four orientation signs |
| Point-in-polygon | Θ(n) | Θ(1) | one pass over edges |
| Closest pair | Θ(n log n) | Θ(n) | divide and conquer |
| All-pairs hull | Θ(n²) | Θ(n) | gift wrapping baseline |

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

