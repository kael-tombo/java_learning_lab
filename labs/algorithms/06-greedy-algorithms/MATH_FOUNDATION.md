# MATH_FOUNDATION — Greedy Algorithms
> Recurrences, Master theorem, amortized analysis for greedy choice.

## 1. Recurrences (tailored)
- Activity selection: `T(n)=T(n-1)+O(1)` after `O(n log n)` sort → `Θ(n log n)` total.
- Huffman: `n-1` merges × `log n` PQ → `Θ(n log n)`; recurrence `T(n)=T(n-1)+O(log n)`.
- Kruskal (greedy): sort `Θ(E log E)` + `E·α(V)` — no divide recurrence.
- Interval partition: sort + PQ `Θ(n log n)`.
- Generic greedy loop: `T(n)=T(n-1)+O(g(n))` unrolled directly (Master rarely applies).

## 2. Master Theorem (scope)
- Greedy rarely fits `aT(n/b)+f`; its recurrence shrinks by constant, not fraction.
- Contrast: D&C `2T(n/2)+n` → `Θ(n log n)` vs greedy `T(n-1)+log n` → `Θ(n log n)` by sum.
- Useful for greedy subroutines (e.g., Huffman PQ ops, MST sort analysis).
- State the trap: forcing Master onto `T(n-1)` is invalid (b=1).
- Summation rule replaces Master: `Σ_{i} g(i)` bounds.

## 3. Greedy-Choice Proofs
- Exchange argument: swap optimal's first choice with greedy's without worsening.
- Stay-ahead: greedy never behind (activity count, partition).
- Matroid characterization: independent sets + exchange ⟺ greedy optimal (Kruskal).
- Counter-proofs: knapsack-0/1 ratio fails — exhibit gap instance.

## 4. Amortized Analysis
- PQ merges (Huffman/Prim): each op `O(log n)` worst; total via `n` ops direct sum.
- DSU in Kruskal: `α(V)` amortized per union — textbook amortized structure.
- Charging: activity-scan charges each interval once (reject or take).
- Potential for incremental greedy (e.g., dynamic Huffman) — brief note.

## 5. Approximation Bounds
- Set cover greedy: `H_n = ln n + O(1)` approximation (harmonic series).
- Knapsack-value greedy + best-single: `1/2`-approx; FPTAS for `(1−ε)`.
- Scheduling `LPT`: `4/3 − 1/(3m)` makespan bound.

## 6. Worked Numbers
- Activities `n=10⁵`: sort ~1.7M cmps + linear scan.
- Huffman 256 symbols: 255 merges × `log` ≈ trivial.
- Set cover `n=1000`: `H_n≈7.5` worst ratio bound.

## 7. Exercises
- [ ] Unroll `T(n-1)+log n` to `Θ(n log n)`.
- [ ] Exchange proof for activity selection.
- [ ] Matroid check for Kruskal.
- [ ] Harmonic bound derivation for set cover.
