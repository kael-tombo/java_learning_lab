# 06 — Parallel Algorithms

<div align="center">

**Work · Span · Brent's Theorem · Prefix Sums · Amdahl's Law · Race Conditions**

</div>

---

## Learning Objectives

- Define work T₁ and span T∞ and prove Brent's bound T_p ≤ T₁/p + T∞
- Derive the span of parallel prefix sum (Θ(log n)) and its work
- State Amdahl's law and its consequence for speedup ceilings
- Recognise a race condition and the minimal fix (lock, atomic, or reduction)
- Choose between fork/join, streams, and parallel arrays for a workload
- Compute the parallelism T₁/T∞ and what it bounds

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Parallel Algorithms

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| Work T₁ | — | — | total operations on one processor |
| Span T∞ | — | — | longest dependency chain |
| Brent T_p | T₁/p + T∞ | Θ(T₁) | ≤ that bound |
| Parallel scan | Θ(n) | Θ(log n) span | up-sweep + down-sweep |
| Parallel merge sort | Θ(n log n) | Θ(n) / Θ(log³ n) span | merge dominates |
| Amdahl speedup | 1/(f+(1-f)/p) | — | ceilings at 1/f |

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

