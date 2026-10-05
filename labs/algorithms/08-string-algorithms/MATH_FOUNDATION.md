# MATH_FOUNDATION — String Algorithms
> Recurrences, Master theorem, amortized analysis for KMP / Rabin-Karp / Trie.

## 1. Recurrences (tailored)
- KMP: prefix `π` built in `Θ(m)`, search `Θ(n)` — failure-link walk, no divide recurrence.
- Z-box: `Θ(n)` with window `[l,r]`; each step extends `r` or copies.
- Rabin-Karp: rolling hash `O(1)` per slide → `Θ(n+m)` expected, `Θ(nm)` worst (spurious hits).
- Trie insert/search: `O(L)` per word (length, not alphabet) — depth recurrence `T(d)=T(d-1)+O(1)`.
- Suffix-array doubling: `T(n)=T(n/2-ish)+O(n log n)` → `O(n log²n)` naive; SA-IS linear (beyond scope).

## 2. Master Theorem (scope)
- Rarely direct in strings; KMP/Z are linear scans, not splits.
- Applies to D&C string multiply / FFT-based matching (`2T(n/2)+n` → `n log n`).
- Parallel prefix (doubling) analysis uses Master-like halving.
- State trap: `T(n)=T(n-1)+1` (Trie depth) unrolls, not Master.
- Contrast example included to show recognition skill.

## 3. Linear-Time Proofs
- KMP amortized: failure pointer only moves back ≤ forward moves → `≤2n` steps.
- Z: `r` never decreases → `O(n)` total window work.
- Aho-Corasick: BFS-built fail links; scan `O(n + matches)`.

## 4. Amortized Analysis (core)
- KMP `q` (matched length): each char bumps `q` ≤ once forward; fallbacks drop it — aggregate `O(n)`.
- Potential `Φ=q` (current match length); mismatch pays via `Φ` decrease.
- Rolling hash: rehash `O(1)` amortized per slide; worst-case verification charged to hits.
- Dynamic string buffer growth: doubling `O(1)` amortized append (same as array).

## 5. Hashing Math
- Mod `M` collision prob `≈1/M` per compare (uniform); double-hash / verify to kill FPs.
- Precompute powers `p^i mod M`; overflow-safe `long` mult.
- Base/mod choice: large prime `1e9+7/9`; dual mod for safety.

## 6. Worked Numbers
- Text `n=10⁶`, pattern `m=10³`: naive worst 10⁹; KMP ~10⁶; RK ~10⁶ + verifications.
- Alphabet 26, words 10⁵ avg len 8: trie nodes ≤ 8·10⁵.

## 7. Exercises
- [ ] KMP potential-method proof (`Φ=q`).
- [ ] Z-window `r`-monotone proof.
- [ ] Expected RK cost with `k` spurious hits.
- [ ] Show Trie `O(L)` by depth unrolling.
