# MATH_FOUNDATION — Divide and Conquer
> Recurrences, Master theorem, amortized analysis for D&C.

## 1. Recurrences (tailored)
- Merge/counting: `T(n)=2T(n/2)+Θ(n)` → `Θ(n log n)`.
- Binary search: `T(n)=T(n/2)+Θ(1)` → `Θ(log n)`.
- Karatsuba: `T(n)=3T(n/2)+Θ(n)` → `Θ(n^{log₂3})≈n^{1.585}`.
- Strassen: `7T(n/2)+Θ(n²)` → `Θ(n^{log₂7})≈n^{2.81}`.
- Quickselect avg: `T(n)=T(3n/4)+Θ(n)` → `Θ(n)` (geometric shrink).

## 2. Master Theorem (full)
- `T(n)=aT(n/b)+f(n)`, `c=log_b a`: f=O(n^{c−ε})→case1 Θ(n^c); f=Θ(n^c log^k)→case2 Θ(n^c log^{k+1}); f=Ω(n^{c+ε})+regularity→case3 Θ(f).
- Merge: case 2 (k=0) → `n log n`. Binary: case 2 edge → `log n`.
- Karatsuba: `3` vs `2^1` → case 1 → `n^{1.585}`.
- Strassen: case 1 vs `n²` → `n^{2.81}`.
- Regularity: `a·f(n/b) ≤ c·f(n)` check for case 3 (e.g., `T=2T(n/2)+n²` holds).

## 3. Trees + Substitution + Akra–Bazzi
- Tree: sum `level-cost × height`; uneven `T(n)=T(n/3)+T(2n/3)+n` → `O(n log n)` (longest path bounds).
- Substitution: guess, induction with constants (show merge example).
- Akra–Bazzi: `Σ a_i b_i^p=1` → `Θ(n^p(1+∫f/n^{p+1})))`; handles quickselect-like fractions.

## 4. Amortized Analysis
- D&C buffer reuse: temp array allocated once, charged across levels (not per call).
- Recurrence with resizing: combine Master + doubling aggregate (e.g., parallel merge buffers).
- Potential across recursion: `Φ` = pending merges; each level drains exactly one layer.
- Accounting: charge `O(n)` combine to elements (each pays `O(log n)` over root path).

## 5. Parallel / Cache Notes
- Span (critical path): merge span `T∞=T∞(n/2)+O(log n)` → `O(log²n)` naive, `O(log n)` pipelined.
- Work-span: parallelism = work/span; affects weak scaling predictions.
- Cache: D&C blocking improves locality vs naive scans (brief).

## 6. Worked Numbers
- n=2²⁰≈10⁶: merge `20M` units; Karatsuba crossover vs naive at hundreds of digits.
- Quickselect `n + 3n/4 + … = 4n` → `Θ(n)` constant 4.
- Strassen wins only for large n (constants!).

## 7. Exercises
- [ ] Classify 6 recurrences via Master.
- [ ] Akra–Bazzi on `T(n/3)+T(2n/3)+n`.
- [ ] Substitution proof for merge.
- [ ] Span recurrence for parallel merge.
