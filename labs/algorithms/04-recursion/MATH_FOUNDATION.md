# MATH_FOUNDATION — Recursion
> Recurrences, Master theorem, amortized analysis for recursive algorithms.

## 1. Recurrences (tailored)
- Factorial/countdown: `T(n)=T(n-1)+Θ(1)` → `Θ(n)`.
- Fib naive: `T(n)=T(n-1)+T(n-2)+Θ(1)` → `Θ(φⁿ)`, `φ≈1.618`.
- Binary recursion: `T(n)=2T(n/2)+Θ(1)` → `Θ(n)` (visit all).
- Merge-style: `T(n)=2T(n/2)+Θ(n)` → `Θ(n log n)`.
- Tail recursion: `T(n)=T(n-1)+Θ(1)` convertible to loop (no stack growth with TCO).

## 2. Master Theorem
- Statement `aT(n/b)+f(n)`, three cases + regularity.
- `2T(n/2)+1` → case 1 → `Θ(n)` (tree: leaves dominate).
- `2T(n/2)+n` → case 2 → `Θ(n log n)`.
- `T(n/2)+1` → case 2 edge → `Θ(log n)`.
- Non-applicable: `T(n-1)` (b=1), `T(n-1)+T(n-2)` (two sizes) — use tree/substitution.
- Akra–Bazzi generalization note for `T(n)=T(n/3)+T(2n/3)+n` → `Θ(n log n)`.

## 3. Recursion Trees + Substitution
- Draw levels, sum per level, bound height; guess + induction verify.
- Fib tree: leaves `~F(n)` → exponential; memo prunes to `n` distinct nodes.
- Induction template: assume `≤c·g(k) k<n`, prove for `n`.

## 4. Amortized Analysis
- Recursion overhead amortized: each call `O(1)` frame; total = nodes × frame.
- Memoization: each state computed once → `O(states × transition)` aggregate.
- Reference: table-doubling potential `Φ=2n−cap` for push buffers in traversals.
- Stack space: depth = longest root-leaf path; tail calls `O(1)` with optimization (Java lacks TCO — loop manually).

## 5. Probabilistic / Depth Notes
- Randomized quickselect `T(n)=T(3n/4)+n` expected → `Θ(n)` (geometric series).
- Recursion depth w.h.p. `O(log n)` with random pivots.
- Java stack ~10⁴ frames — depth analysis is engineering, not just theory.

## 6. Worked Numbers
- Fib(50) naive `~20B` calls vs memo 51 states.
- `T(n)=2T(n/2)+n`, n=1024: 10 levels × 1024 = 10240 units.
- Countdown depth 10⁵ → overflow; loop mandatory.

## 7. Exercises
- [ ] Solve all §1 recurrences by tree.
- [ ] Substitution proof for `2T(n/2)+n`.
- [ ] Akra–Bazzi sketch for uneven split.
- [ ] Aggregate memo cost on DAG states.
