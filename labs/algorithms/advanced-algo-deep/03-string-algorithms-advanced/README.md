# 03 — String Algorithms Advanced

<div align="center">

**KMP · Rabin–Karp · Z-function · Suffix Automaton · Manacher**

</div>

---

## Learning Objectives

- Explain why the KMP failure function keeps the matched prefix, not zero progress
- Argue KMP runs in Θ(n) by a potential argument on the matched length
- Implement Rabin–Karp rolling hash and bound the false-positive rate
- Compute the Z-array in Θ(n) and use it for pattern matching
- Recognise a palindrome linear scan with Manacher's centre expansion
- State what a suffix automaton accepts and its Θ(n) construction

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — String Algorithms Advanced

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| KMP search | Θ(n+m) | Θ(m) | text pointer never retreats |
| Rabin–Karp search | Θ(n+m) expected | Θ(1) | hash confirm on hit |
| Z-array build | Θ(n) | Θ(n) | right-edge window moves only right |
| Manacher | Θ(n) | Θ(n) | mirror palindrome reuse |
| Suffix automaton build | Θ(n) alphabet-dependent | Θ(n) | ≤ 2n-1 states |
| Naive matching | Θ(n·m) | Θ(1) | the baseline to beat |

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

