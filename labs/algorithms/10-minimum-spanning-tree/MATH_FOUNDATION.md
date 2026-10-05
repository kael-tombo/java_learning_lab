# MATH_FOUNDATION — Minimum Spanning Tree
> Recurrences, Master theorem, amortized analysis for Kruskal / Prim / DSU.

## 1. Recurrences (tailored)
- Kruskal: sort `T(E)=2T(E/2)+Θ(E)` → `Θ(E log E)` + `E` DSU ops.
- Prim (binary heap): `V` extracts + `E` decreases → `Θ(E log V)` (no Master; sum of heap ops).
- Prim naive: `V` scans `Θ(V)` → `Θ(V²)`.
- Borůvka phases: components halve per round → `O(log V)` rounds × `O(E)` → `O(E log V)`.
- DSU find: `T(h)=T(h/2-ish)+O(1)`-ish with compression (amortized, not Master).

## 2. Master Theorem
- Direct hit: sorting step `2T(n/2)+n → Θ(n log n)` (Kruskal dominant).
- Borůvka halving `T(V)=T(V/2)+O(E)` → `O(E log V)` by unrolling (Master with f=E constant-in-V).
- Prim heap-sum not Master form — summation of `log` terms.
- Contrast binary-search `T(n/2)+1 → log n` for pattern fluency.
- Regularity/case notes as in D&C (brief).

## 3. Cut/Cycle Proofs (math core)
- Cut property via exchange: swap heavier crossing edge, weight non-increasing.
- Cycle property dual; uniqueness with distinct weights by strict exchange.
- Number of MSTs from tie components (product of choices) — counting note.

## 4. Amortized Analysis (DSU focus)
- Union by rank: tree height `O(log n)` worst without compression.
- Path compression: Tarjan `O(m·α(n))` for `m` ops — inverse Ackermann ≤5 practical.
- Potential: rank-sum / Strahler-like `Φ`; each find flattens (pays future).
- Aggregate: `E` finds + `V-1` unions → near-linear after sort.

## 5. Probabilistic / Randomized
- Karger-Klein-Tarjan linear expected MST (random sampling + verification) — mention only.
- Random edge order + early Borůvka contraction (brief).

## 6. Worked Numbers
- `E=10⁶`: sort ~20M cmps; DSU ~10⁶×α ≈ 10⁶ ops (negligible).
- Dense `V=10⁴,E~10⁸`: Prim `V²=10⁸` beats sort-based.
- α(10⁹) ≤ 5 — effectively constant.

## 7. Exercises
- [ ] Master-classify Kruskal sort step.
- [ ] Unroll Borůvka rounds to `E log V`.
- [ ] Rank-height `log n` proof.
- [ ] α-concept + why "almost constant" is amortized not worst-case.
