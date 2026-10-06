# 02 — Number Theory Advanced

<div align="center">

**Euclid · Extended GCD · Modular Exponentiation · CRT · Miller–Rabin · Sieves**

</div>

---

## Learning Objectives

- Prove gcd(a,b)=gcd(b, a mod b) and use it to compute gcd in Θ(log min(a,b))
- Derive Bézout coefficients via the extended Euclidean algorithm
- Implement fast modular exponentiation and argue its Θ(log e) multiplications
- State Euler's theorem and apply it to reduce a huge exponent mod φ(n)
- Solve a system of congruences with the Chinese Remainder Theorem
- Explain why Miller–Rabin is probabilistic and what "k rounds" means

## Prerequisites

- Recursion, Big-O, and the preceding labs in this track

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Core Idea

# Theory — Number Theory Advanced

## Complexity Snapshot

| Algorithm / Structure | Time | Space | Note |
|---|---|---|---|
| gcd | Θ(log min(a,b)) | Θ(1) | halves the larger argument within two steps |
| xgcd/Bézout | Θ(log min(a,b)) | Θ(1) | carries (x,y) through the recursion |
| modPow | Θ(log e) multiplies | Θ(1) | reduce after every multiply |
| Sieve to n | Θ(n log log n) | Θ(n) | start marking at p² |
| Miller–Rabin | Θ(k·log³ n) | Θ(1) | error ≤ 4⁻ᵏ |
| CRT, r moduli | Θ(r²) | Θ(r) | pairwise inverse via extended Euclid |

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

