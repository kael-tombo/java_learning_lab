# 05 — Combinatorial Algorithms

<div align="center">

**Binomial Coefficients · Catalan · Inclusion–Exclusion · Stirling · Meet in the Middle**

</div>

---

## Learning Objectives

- Compute binomial coefficients in Θ(n·k) with Pascal's recurrence
- Apply the Catalan closed form C_n = (1/(n+1))·C(2n,n) to valid-parentheses counts
- Count via inclusion–exclusion and decide when to use it over direct counting
- State Stirling numbers of the second kind and the surjection count
- Explain meet-in-the-middle and where it replaces brute-force 2^n
- Enumerate subsets of a bitmask in Θ(3^k) total by the submask loop

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Combinatorial Algorithms

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| Binomial via Pascal | Θ(n·k) | Θ(k) | rolling row |
| Catalan closed form | Θ(n) | Θ(1) | one binomial computation |
| S(n,k) Pascal-style | Θ(n·k) | Θ(k) | rolling row |
| Inclusion–exclusion, k props | Θ(2^k) | Θ(k) | only for small k |
| Meet in the middle | Θ(2^{n/2}·n) | Θ(2^{n/2}) | halves the exponent |
| Submask enumeration, all masks | Θ(3^k) | Θ(1) | amortised over masks |

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

