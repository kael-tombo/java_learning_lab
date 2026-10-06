# 01 — Bit Manipulation Advanced

<div align="center">

**Two's Complement · Brian Kernighan · SWAR · XOR Tricks · Integer.bitCount**

</div>

---

## Learning Objectives

- State why x & (x-1) clears the lowest set bit and prove it from two's complement
- Implement Brian Kernighan popcount and derive its Θ(number of set bits) bound
- Use XOR to cancel duplicated values and justify masked-set updates
- Explain signed vs unsigned right shift and when masking is required
- Apply SWAR to count/parity-check packed fields without per-bit loops
- Recognise the overflow pitfalls in masks built from 1 << n with signed int

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Bit Manipulation Advanced

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| x & (x-1) update loop | Θ(k) | k = popcount(x) | ≤ 32 (int) / 64 (long) iterations |
| Brian Kernighan popcount | Θ(k) | k = set bits | ≤ word-width iterations |
| SWAR popcount | Θ(1) | word = 32 or 64 bits | 5 field folds, branch-free |
| XOR cancel duplicated odd-one-out | Θ(n) | Θ(1) extra space | only for pairwise (2k) duplicates |
| M & -M isolate lowest set bit | Θ(1) | Θ(1) | single-bit mask |
| Bit test/set/clear/toggle | Θ(1) | Θ(1) | one mask operation each |

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

