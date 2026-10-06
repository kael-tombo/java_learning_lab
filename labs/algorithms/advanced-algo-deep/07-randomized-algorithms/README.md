# 07 — Randomized Algorithms

<div align="center">

**Random Quicksort · Randomized Selection · Miller–Rabin · Monte Carlo vs Las Vegas**

</div>

---

## Learning Objectives

- Prove the expected running time of randomised quicksort is Θ(n log n)
- Derive the expected Θ(n) bound for randomised selection (quickselect)
- Distinguish Monte Carlo (bounded error probability) from Las Vegas (always correct)
- State why a random pivot avoids the Θ(n²) worst case of sorted input
- Apply reservoir sampling to stream a uniform sample of unknown size
- Explain randomised hash tables' expected Θ(1) operations via hashing

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Randomized Algorithms

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| Randomised quicksort | Θ(n log n) expected | Θ(n log n) span | Θ(n²) worst, improbable |
| Quickselect | Θ(n) expected | Θ(1) | recursive on one side |
| Miller–Rabin | Θ(k·log³ n) | Θ(1) | error ≤ 4⁻ᵏ |
| Reservoir sampling | Θ(n) | Θ(k) | one pass, unknown n |
| Randomised hash ops | Θ(1) expected | Θ(n) worst | universal hashing |
| Freivalds' verify | Θ(n²) | Θ(1) | Monte Carlo matrix check |

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

