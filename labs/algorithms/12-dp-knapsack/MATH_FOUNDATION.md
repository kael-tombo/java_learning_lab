# MATH_FOUNDATION — 0/1 Knapsack
> Recurrences, Master theorem, amortized analysis for knapsack DP.

## 1. Recurrences (tailored)
- 0/1: states `n(W+1)`, `O(1)` transition → `Θ(nW)` (pseudo-polynomial, not Master).
- Brute force: `T(n)=2T(n-1)+O(1)` → `Θ(2ⁿ)` (enumerate subsets).
- Unbounded: same `Θ(nW)` with ascending loop (different transition reuse).
- Fractional: sort `2T+T` → `Θ(n log n)` + greedy linear (exchange proof).
- Meet-in-middle: `Θ(2^{n/2})` split + sort + combine.

## 2. Master Theorem (scope)
- Knapsack DP recurrence indexes `i` (count) and `w` (capacity) — 2-D, not `aT(n/b)+f`.
- Master applies only to sort step (`n log n`) and D&C helpers.
- Recognition drill: `2T(n-1)+1 → 2ⁿ` (unroll) vs `2T(n/2)+n → n log n` (Master).
- State trap explicitly: "O(nW) by Master" is wrong; it's state counting.

## 3. Pseudo-Polynomial + Hardness
- Input size `Θ(n log W)` bits; `W` magnitude exponential in bits → `nW` exponential in size.
- NP-hard (partition/subset-sum reduction sketch); no `poly(n,log W)` known.
- FPTAS: scale values by `K=ε·vmax/n` → `O(n³/ε)` for `(1−ε)` approx.
- Parameterized: `O(nW)` is FPT in `W`; meet-middle FPT in `n/2`.

## 4. Amortized Analysis
- 1-D descending: each item touches `W` cells once → aggregate `nW` (charge per cell).
- Reconstruction walk `O(n+W)` after fill — dominated, not extra order.
- Sparse (few reachable capacities): reachable-set DP charges only live states.
- Table reuse across queries (same items, varying W): prefix rows amortize.

## 5. Approximation Math
- Greedy ratio unbounded gap for 0/1 (craft gap →∞ with `W+1` trick).
- Best-of (greedy, max-single) is `1/2`-approx; proof via fractional upper bound.
- Scaling proof: rounding loses ≤ `nK` → `(1−ε)` guarantee.

## 6. Worked Numbers
- `n=100,W=10⁵` → 10⁷ ops (~0.1s Java); `W=10⁹` → 10¹¹ (infeasible).
- `n=34` meet-middle `2·2¹⁷≈262k` subsets — trivial.
- FPTAS `ε=0.01,n=100` → ~10⁸ scaled ops (borderline, tune).

## 7. Exercises
- [ ] Unroll brute `2T(n-1)+1`.
- [ ] Prove `Θ(nW)` by state counting.
- [ ] Gap instance for ratio-greedy (compute ratio →∞).
- [ ] FPTAS scaling derivation (1 page).
