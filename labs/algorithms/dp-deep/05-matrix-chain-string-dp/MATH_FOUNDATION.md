# Math Foundation — Matrix Chain & String DP

The `Θ(n³)` accounting, the Master theorem for the recurrence tree, greedy counterexample arithmetic, and the `Θ(n³) → Θ(n²)` transitions.

---

## 1. The state/transition accounting

**States:** intervals `[i, j]` with `0 ≤ i ≤ j < n` ⇒ `Θ(n²)`.

**Transitions per state:** split points `k ∈ [i, j-1]` ⇒ `Θ(n)`.

**Total inner iterations:**

```
T(n)  =  Σ_{len=2}^{n}  (n − len + 1) · (len − 1)
```

Substitute `m = len − 1`, so `m = 1..n−1`:

```
T(n)  =  Σ_{m=1}^{n-1}  (n − m) · m
      =  n·Σm − Σm²
      =  n·(n−1)n/2  −  (n−1)n(2n−1)/6
      =  n(n−1)[ n/2 − (2n−1)/6 ]
      =  n(n−1)[ (3n − 2n + 1)/6 ]
      =  n(n−1)(n + 1)/6
      =  (n³ − n) / 6
```

**So the constant is `1/6`, not 1.** A rectangular `for i, for j, for k` loop that runs all `n³` triples does **6× the necessary work**.

| `n` | `(n³−n)/6` inner iterations | Java (≈ 3 ns each) |
|-----|---------------------------|---------------------|
| 100 | 166 650 | 0.5 ms |
| 500 | 20 833 250 | **60 ms** |
| 1000 | 166 666 500 | **500 ms** |
| 2000 | 1 333 333 000 | **4 s** |
| 5000 | 20 833 333 250 | **60 s** ✗ |
| 10 000 | 1.67·10¹¹ | **8 minutes** ✗ |

**Space:** `Θ(n²)` for `cost[i][j]` plus `Θ(n²)` for `split[i][j]`. At `n = 5000` that is 2 × `25·10⁶` ints = **200 MB** — memory becomes the binding constraint before time does.

---

## 2. Master theorem for the interval recurrence

The recurrence is not of the form `aT(n/b) + f(n)` in `n`; it is a **two-parameter** DP. But the *tree* has a clean shape.

For matrix chain, the computation is a **binary tree over the `n−1` gaps** between matrices. The DP explores all `C_{n-1}` Catalan parenthesisations to find the minimum.

```
Number of parenthesisations of n matrices = Catalan(n−1) = (1/n)·binom(2n−2, n−1) ~ 4^(n−1) / (n^1.5 sqrt(pi))
```

| `n` | `C_{n-1}` |
|-----|----------|
| 10 | `4 862` |
| 15 | `9 694 845` |
| 20 | `1 767 263 190` |
| 25 | `3 814 986 502 092` |

**So the naive "try all parenthesisations" is `Θ(4ⁿ)`.** The DP's entire contribution is memoisation over `Θ(n²)` sub-intervals:

```
Θ(4ⁿ)   ->   Θ(n²) states x Θ(n) splits   =   Θ(n³)
```

**Speedup at `n = 20`:** `1.77·10⁹` → `6 650` inner iterations. **266 000×.**

This is the exact same memoisation story as `fib` (lab `01`) — the subproblem count is polynomial in `n` even though the tree is exponential.

---

## 3. The greedy counterexample, computed exactly

Dimensions `(10, 100, 5, 50)` ⇒ `A₁: 10×100`, `A₂: 100×5`, `A₃: 5×50`, `A₄: 50×50`.

| parenthesisation | multiplications | total |
|------------------|---------------|-------|
| `(((A₁A₂)A₃)A₄)` | `10·100·5 = 5 000`; `10·5·50 = 2 500`; `10·50·50 = 25 000` | **32 500** |
| `((A₁(A₂A₃))A₄)` | `100·5·50 = 25 000`; `10·100·50 = 50 000`; `10·50·50 = 25 000` | **100 000** |
| `((A₁A₂)(A₃A₄))` | `10·100·5 = 5 000`; `5·50·50 = 12 500`; `10·5·50 = 2 500` | **20 000** ← optimum |
| `(A₁((A₂A₃)A₄))` | `100·5·50 = 25 000`; `100·50·50 = 250 000`; `10·100·50 = 50 000` | **325 000** |
| `(A₁(A₂(A₃A₄)))` | `5·50·50 = 12 500`; `100·5·50 = 25 000`; `10·100·50 = 50 000` | **87 500** |

**Greedy "compute the cheapest single product first"** picks `A₁A₂` (5 000), then among the remaining it faces a choice; it ends at `(((A₁A₂)A₃)A₄)` = **32 500**, which is **62.5% above the optimum of 20 000.**

**Greedy "pair the matrices with the smallest combined inner dimension first"** picks `A₃A₄` (dimension 5×50, cost 12 500) — correct here, giving 20 000. But on the *three*-matrix case:

`A₁: 10×100`, `A₂: 100×5`, `A₃: 5×50`:

| | multiplications | total |
|---|---|---|
| `(A₁A₂)A₃` | `5 000`; `10·5·50 = 2 500` | **7 500** ← optimum |
| `A₁(A₂A₃)` | `25 000`; `10·100·50 = 50 000` | **75 000** |

**Greedy by "smallest inner dimension"** sees `A₂`'s output dimension 5, `A₁`'s 100, `A₃`'s 50, and pairs `A₂A₃` (inner dimension 50 is not smallest...) — the standard formulation pairs `A₁,A₂` because their shared dimension 100 is largest, or pairs the two whose *product* is cheapest, which is `A₁A₂` at 5 000 → **correct**.

**The unambiguous counterexample for "smallest output dimension first"** is `A₁: 30×10`, `A₂: 10×60`, `A₃: 60×30`:
- `(A₁A₂)A₃`: `30·10·60 = 18 000` then `30·60·30 = 54 000` ⇒ **72 000**
- `A₁(A₂A₃)`: `10·60·30 = 18 000` then `30·10·30 = 9 000` ⇒ **27 000**

Both single products cost 18 000, so no "cheapest first" rule distinguishes them; the tie-break decides, and one tie-break is 2.67× worse. **The lesson is that the cost `d[i-1]d[k]d[j]` is not decomposable into pairwise decisions — the whole interaction matters.**

---

## 4. `Θ(n³) → Θ(n²)`: when precomputation suffices

The `Θ(n³)` shape has `Θ(n²)` states and `Θ(n)` transitions. If the transition predicate is **precomputable in `Θ(n²)`**, the total drops to `Θ(n²)`.

### Palindrome partitioning

```
naive:   cut[i] = min over j with s[j..i-1] palindrome of ( cut[j-1] + 1 )
         testing palindrome is Θ(i-j)  ->  Θ(n³)

precomputed:
   pal[i][j] = s[i]==s[j] && (j-i<=1 || pal[i+1][j-1])        Θ(n²)
   cut[i]    = min over j with pal[j][i-1] of ( cut[j-1]+1 )     Θ(n²)
   total     Θ(n²)
```

**Speedup: `n`.** At `n = 5000`: `2·10¹¹` vs `2·10⁷` — **10 000×**.

### Optimal BST (Knuth's optimisation)

```
naive:  opt[i][j] = min over i<k<=j of ( opt[i][k-1] + opt[k+1][j] + w(i,j) )   Θ(n³)

Knuth:  opt[i][j] = min over opt[i][j-1] <= k <= opt[i+1][j] of ( ... )        Θ(n²) amortised
```

**Why it works:** the cost function satisfies the **quadrangle inequality**
`w(a,c) + w(b,d) <= w(a,d) + w(b,c)` for `a ≤ b ≤ c ≤ d` and the **monotonicity** `w(b,c) <= w(a,d)`.

The amortised argument: the number of `k` examined in the window `[opt[i][j-1], opt[i+1][j]]` telescopes across the whole table, giving `Θ(n²)` total because

```
Σ_{i<j} (opt[i+1][j] - opt[i][j-1])  =  Θ(n²)
```

because each `opt[i][j]` appears **twice** — once as a lower bound and once as an upper bound — and cancels with its neighbours.

**Quadrangle inequality in `Θ(n²)` form:**

```
             Monge:            Quadrangle:
  a\ b   0    1    2            a\ b   0    1    2
   0     0    1    2             0     0    1    2
   1    -1    0    1             1    -1    0    1
   2    -2   -1    0             2   -3   -2    0
```

If `M[a][c] + M[b][d] <= M[a][d] + M[b][c]` for all `a ≤ b ≤ c ≤ d`, the matrix is **Monge**, and the row minima are **monotone in the column index** — which is exactly what SMAWK and Knuth exploit.

---

## 5. SMAWK — the `Θ(n²)` total algorithm

**Total monotone matrices** admit finding all row minima in `Θ(rows + cols)` comparisons. Applied to a `Θ(n²)` DP with `Θ(n²)` transitions, that gives **`Θ(n²)` total**.

```
Naive row-minimum scan:   rows x cols comparisons
SMAWK:                    O(rows + cols) comparisons
```

**For a DP with `n` states and `n` candidates each:** `Θ(n²)` candidates and `Θ(n)` rows ⇒ SMAWK finds all the minima in `Θ(n)` comparisons *per row*, so `Θ(n)` total per row ⇒ **`Θ(n²)` total for the whole DP** instead of `Θ(n³)`.

**Where it applies:** any DP of the form `dp[j] = min over i ( M(i,j) + dp[i] )` where `M` is totally monotone — e.g. LeetCode 1135 (minimum cost of connecting all points), the "aliens"/WQS family, and `Θ(n²)` LCS-with-restrictions.

**The caveat:** the constant factor of SMAWK is large (it involves recursive row/column reduction with `Θ(log)` depth), so in practice the constant-factor `n³/6` DP often beats SMAWK for `n ≤ 500`. **Measure.**

---

## 6. Divide-and-conquer optimisation (the `Θ(n log n)` inner loop)

Many DPs have `opt[i][j] ∈ [opt[i][j−1], opt[i][j+1]]` — the optimal split moves monotonically with `j`.

**Mechanism:** solve `dp[*][mid]` for the middle column by scanning all splits; the bounds for `dp[*][mid−1]` and `dp[*][mid+1]` are then read off the just-computed column. Recurse.

```
Cost:  T(n) = T(n/2) + O(n)   ->  O(n log n)   for the whole triangle of columns
       instead of O(n²)        ->  O(n²)  for the whole DP
```

Applied to the **LCS-with-restrictions** family, this is the `Θ(nm)` → `Θ(nm log n)`-inner-loop family.

---

## 7. RNA folding accounting

```
Inner iterations:
N[i][j] = max over k in [i, j-2] with pairable(i,k) of ...
T(n)  =  Σ_{len=3}^{n} (n - len + 1)(len - 2)
      ≈  n³/6  - n²/2 + ...
```

| `n` | inner iterations | Java |
|-----|------------------|------|
| 100 | 166 650 | 0.5 ms |
| 500 | 20 833 250 | **60 ms** |
| 1000 | 166 666 500 | **500 ms** |
| 2000 | 1 333 333 000 | **4 s** |
| 5000 | 2·10¹⁰ | **60 s** ✗ |

**With only 4 pairable base pairs (A-U, C-G), roughly half of all `(i,k)` pairs are skipped**, giving a constant-factor `~2×` improvement — still `Θ(n³)`.

**MFE (minimum free energy)** multiplies the constant by the number of states: an MFE DP needs ~30 states per interval (hairpin, bulge, interior loop, stack, dangle × 5), so the constant is ~30× — **`n ≈ 200` practical**. Real tools use:
- **SIMD** — ViennaRNA reports 2–5× from hand-vectorised inner loops.
- **`O(n³ / log n)` parallel** — message passing over `Θ(n²)` cells, `Θ(n)` stages.
- **`O(n²)` grammar/non-crossing approximations** — for very long sequences.

---

## 8. Word break accounting

| Implementation | Time | Note |
|---|---|---|
| Naive with `s.substring` | **`Θ(n³)`** | substring copies are `Θ(i−j)` |
| `HashSet` of substrings, cached hashes | `Θ(n²)` | `O(1)` membership |
| Trie walk from each start | **`Θ(n·L)`** | `L` = longest word length |
| Aho–Corasick + DP | **`Θ(S + n)`** | the *right* algorithm |

**Aho–Corasick for word break:** build an automaton over the dictionary, scan `s` once, and at each position collect the lengths of all words ending there. Then `can[i]` is set for each such start. Total `Θ(S + n + matches)`.

**That is a genuinely important observation:** word break is **not** fundamentally `Θ(n²)`. With Aho–Corasick it is `Θ(S + n)`, where `S = Σ|word|`. For a large dictionary this is the difference between `n²` and `n + S`.

**All-segmentations output size:** the number of segmentations of `"aaaa…a"` with all lengths in the dictionary is `2^{n−1}`. So the `Θ(output)` term is exponential and unavoidable — the algorithm is output-optimal, and the practical mitigation is to cap the number of returned segmentations.

---

## 9. Complexity summary

| Problem | Time | Space | Constant |
|---------|------|-------|----------|
| Matrix chain | `Θ(n³)` | `Θ(n²)` | `1/6` with the triangular loop |
| Matrix chain (naive enumeration) | `Θ(4ⁿ)` | `Θ(n)` | Catalan |
| Polygon triangulation | `Θ(n³)` | `Θ(n²)` | `1/6` |
| Hu–Shing polygon triangulation | **`Θ(n log n)`** | `Θ(n)` | complex constant |
| Palindrome partitioning | **`Θ(n²)`** | `Θ(n²)` or `Θ(n)` | precompute `pal` |
| Palindrome counting | `Θ(n²)` | `Θ(n)` | — |
| Optimal BST (naive) | `Θ(n³)` | `Θ(n²)` | — |
| Optimal BST (Knuth) | **`Θ(n²)`** | `Θ(n²)` | quadrangle inequality |
| SMAWK-DP | **`Θ(n²)`** | `Θ(n)` | big constant |
| D&C-optimised DP | `Θ(n²)` total | `Θ(n²)` | — |
| RNA folding (Nussinov) | `Θ(n³)` | `Θ(n²)` | `1/6`, halved by pairability |
| RNA folding (MFE) | `Θ(n³)` | `Θ(n²)` | **~30× constant** |
| Word break, `substring` | `Θ(n³)` | `Θ(n)` | trap |
| Word break, `HashSet` | `Θ(n²)` | `Θ(n)` | — |
| **Word break, Aho–Corasick** | **`Θ(S + n)`** | `Θ(S)` | the right one |
| All segmentations | `Θ(n² + output)` | output | output can be `2ⁿ` |
| String metrics matrix | `Θ(n⁴)` | `Θ(n²)` | for the Penney game |

---

## 10. Quick reference

| Quantity | Value |
|----------|-------|
| Interval DP states | `Θ(n²)` |
| Split points per state | `Θ(n)` |
| Total inner iterations | **`(n³ − n)/6`** |
| Constant vs rectangular triple loop | **`6×` saving** |
| Fill order | **increasing interval length** |
| Matrix-chain naive enumeration | Catalan `C_{n−1} ~ 4ⁿ/n^1.5` |
| Memoisation speedup at `n = 20` | `1.77·10⁹ → 6 650` = **266 000×** |
| Greedy counterexample | dims `(10,100,5,50)`: greedy 32 500 vs optimum **20 000** |
| Three-matrix counterexample | `(30×10, 10×60, 60×30)`: 72 000 vs **27 000** |
| Precompute-a-predicate saving | `Θ(n³) → Θ(n²)` = **`n×`** |
| Knuth's condition | quadrangle inequality + monotonicity of `w` |
| Knuth result | `Θ(n³) → Θ(n²)` amortised |
| SMAWK result | `Θ(rows + cols)` comparisons per row-minimum pass |
| D&C optimisation result | `Θ(n²)` inner → `Θ(n log n)` |
| Hu–Shing | `Θ(n log n)` polygon triangulation |
| Practical `n` limit, `Θ(n³)` | **`n ≈ 500`** (60 ms), `n ≈ 2000` (4 s) |
| Practical `n` limit, `Θ(n³)` MFE | `n ≈ 200` |
| Word break, best known | **`Θ(S + n)`** with Aho–Corasick |
| Word-break output size | up to `2^{n−1}` segmentations |
| Memory wall at `n = 5000` | `Θ(n²)` ints × 2 tables = **200 MB** |

## Sources

- Timoshenko (1969), Gotoh (1969) — the `Θ(n³)` matrix-chain DP.
- Hu & Shing (1982) — `Θ(n log n)` polygon triangulation.
- Knuth (1971) — the optimisation named for him.
- Monge (1887) / SMAWK (Aggarwal, Klawe, Moran, Shor, Wilber, 1987).
- Nussinov (1970) — RNA secondary structure.
- Penney (1974), Conway (1983) — the string-matching game.