# MATH_FOUNDATION — Advanced Sorting
> Recurrences, Master theorem, amortized analysis for merge/quick/heap.

## 1. Recurrences (tailored)
- Merge: `T(n)=2T(n/2)+Θ(n)` (split + linear merge).
- Quick (avg): `T(n)=T(k)+T(n-k-1)+Θ(n)`, random pivot → `Θ(n log n)` expected.
- Quick worst: `T(n)=T(n-1)+Θ(n)` → `Θ(n²)` (sorted + bad pivot).
- Heap build: `Σ h·(n/2^{h+1})` → `Θ(n)`; sort: `n` extracts × `log n`.
- Recurrence tree: merge level `i` has `2^i` nodes × `n/2^i` = `n` per level × `log n` levels.

## 2. Master Theorem
- Form `T(n)=aT(n/b)+f(n)`; compare `f` vs `n^{log_b a}`.
- Merge: `a=2,b=2,f=n` → `n^{1}=n`, case 2 → `Θ(n log n)`.
- Binary-search-like partition scan: `T(n)=T(n/2)+Θ(1)` → case 1 → `Θ(log n)`.
- Strassen-style (contrast): `7T(n/2)+Θ(n²)` → `Θ(n^{log₂7})`.
- Quick avg not direct Master (random split) — use linearity of expectation / tree.
- Pitfall: floors/ceilings ignored asymptotically; verify regularity for case 3.

## 3. Counting Proof Sketches
- Merge lower: each level touches all `n` elements (merge scans both halves).
- Comparison lower bound: `log₂(n!) = Θ(n log n)` (Stirling) — merge/quick optimal class.
- Inversions: insertion `Θ(n+I)`; merge counts inversions in same pass.

## 4. Amortized Analysis
- Dynamic-array resizes (buffer for merges): aggregate `Σ2^k = O(n)` → `O(1)` amortized push.
- Potential method: `Φ = 2·size − capacity` (table doubling) — quick refresher.
- Sift-down chain: each extract `O(log n)` worst; build-heap `O(n)` via leaf-heavy sum.
- Accounting: charge merge copies to output positions (each level `n` charges).

## 5. Probabilistic Notes
- Random pivot: expected comparison count `2n ln n ≈ 1.39n log₂n`.
- Shuffling (Fisher–Yates) makes worst-case prob `1/n!` — practical derandomization.
- Tail recursion + shuffle → depth `O(log n)` w.h.p.

## 6. Worked Numbers
- `n=10⁶`: `n log₂n ≈ 20M` comparisons; `n²` = 10¹² (infeasible).
- Merge levels `⌈log₂n⌉=20`; per-level `n` work → 20M units.
- Heap build `≈2n` sifts vs naive `n log n`.

## 7. Exercises
- [ ] Solve `2T(n/2)+n` by tree + substitution.
- [ ] Show quick-worst `Θ(n²)` via unrolling.
- [ ] Prove build-heap sum converges (`Σ h/2^h = 2`).
- [ ] Aggregate-method proof for push-doubling.
