# Flashcards — Matrix Chain & String DP

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | The shared DP shape | **interval state `dp[i][j]` + split transition over `k`** |
| 2 | Interval DP states | `Θ(n²)` |
| 3 | Interval DP transitions | `Θ(n)` per state ⇒ **`Θ(n³)` total** |
| 4 | Exact inner-iteration count | **`(n³ − n)/6`** — a `6×` saving over a rectangular triple loop |
| 5 | Fill order | **increasing interval length** |
| 6 | Alternative valid order | `i` descending, `j` ascending (each sub-interval differs in one axis) |
| 7 | Invalid order | `i` ascending, `j` descending |
| 8 | Matrix chain recurrence | `min over k of ( cost[i][k] + cost[k+1][j] + d[i]·d[k+1]·d[j+1] )` |
| 9 | Matrix chain greedy counterexample | dims `(10,100,5,50)`: greedy `32 500` vs optimum **`20 000`** |
| 10 | Why greedy fails | the split cost depends on `i`, `k`, **and** `j` together — no local rule |
| 11 | Naive matrix chain | Catalan `C_{n−1} ≈ 4ⁿ/n^1.5`; memoisation gives `266 000×` at `n = 20` |
| 12 | Matrix chain in Java | needs **`long`** — `int` overflows for `d` in the hundreds |
| 13 | Polygon triangulation | **identical recurrence** to matrix chain, `Θ(n³)` |
| 14 | Hu–Shing | `Θ(n log n)` polygon triangulation |
| 15 | Burst balloons (LC 312) | same shape, `max` instead of `min`, sentinels at both ends |
| 16 | Palindrome table | `pal[i][j] = s[i]==s[j] && (j−i<=1 \|\| pal[i+1][j−1])` |
| 17 | Palindrome fill order | `i` **descending**, `j` ascending |
| 18 | Palindrome partitioning | **`Θ(n²)`** with the precomputed table (`Θ(n³)` without) |
| 19 | Palindrome partitioning, `O(n)` space | centre expansion; answer is `dp[n] − 1` (pieces vs cuts) |
| 20 | Manacher's algorithm | `Θ(n)` palindrome detection — `n²` at `n = 10⁶` on `"aaaa…a"` is `5·10¹¹` palindromes |
| 21 | String edit distance | `Θ(nm)` with **separable costs**, per pair of strings |
| 22 | Penney game matrix | `Θ(n⁴)` to build (`n·m` entries × `Θ(len²)` DP each) |
| 23 | Penney game equilibrium | **`HRRRRR…R`** — same form for every alphabet |
| 24 | Penney game significance | DP + linear algebra ⇒ a structural theorem about *timing* not symbols |
| 25 | Word break existence, naive | **`Θ(n³)`** — `substring` inside the inner loop |
| 26 | Word break, `HashSet` | `Θ(n²)` |
| 27 | Word break, trie | `Θ(n·L)` |
| 28 | **Word break, Aho–Corasick** | **`Θ(S + n + matches)`** — the right algorithm |
| 29 | Word break output size | up to `2^{n−1}` segmentations — **must cap** (DoS) |
| 30 | RNA Nussinov | `Θ(n³)`, constant `≈ 1/6`, halved by pairability |
| 31 | RNA practical limit | `n ≈ 500` for Nussinov, `n ≈ 200` for MFE (~30× constant) |
| 32 | RNA in production | SIMD (2–5×) + `O(n³/logn)` parallel + `O(n²)` approximations |
| 33 | Quadrangle inequality | `w(a,c) + w(b,d) <= w(a,d) + w(b,c)` for `a<=b<=c<=d` |
| 34 | Monotonicity condition | `w(b,c) <= w(a,d)` for `a<=b<=c<=d` |
| 35 | Knuth's optimisation | restricts `k` to `[opt[i][j−1], opt[i+1][j]]`; `Θ(n³) → Θ(n²)` |
| 36 | SMAWK | `Θ(rows + cols)` comparisons for all row minima |
| 37 | D&C optimisation | `Θ(n²)` inner → `Θ(n log n)` |
| 38 | The three attacks on `Θ(n³)` | precompute the predicate · monotonicity of `opt` · exploit problem structure |
| 39 | Memory wall | `Θ(n²)` ints × 2 tables at `n = 5000` = **200 MB** |
| 40 | Reconstruction | record `split[i][j] = k`; `Θ(n²)` extra space |
| 41 | Interval-DP oracle | Catalan enumeration for `n ≤ 8` — validates fill order and indices |
| 42 | Coin change | unbounded knapsack by value (lab 01/04) |
| 43 | Rod cutting | `Θ(n²)` interval-free split DP (lab 01) |
| 44 | Matrix chain in production | you usually do **not** need it — the JIT inlines small chains |
| 45 | When you do need it | strings/trees/intervals, `n > 30`, or you need the parenthesisation itself |
| 46 | NP-hardness | **none** of these problems are NP-hard — "give up" is never right |
| 47 | Empty-input conventions | `minCuts("") = 0`, `maxPairs` of `n < 2` = 0, `cost[i][i] = 0` |
| 48 | The `k == i+1` RNA case | `dp[i+1][k−1] = dp[i+1][i] = 0` by the lower-triangle-zero convention |
| 49 | Substring cost | `Θ(i−j)` — the trap in word break and in string-metric inner loops |
| 50 | Hoist loop invariants | cost functions like `delete(x[i−1])` are `j`-invariant — hoist, `2×` win |

## Self-test (one line each)

1. The shared DP shape and its exact size? → **`dp[i][j]` over intervals with a split `k`: `Θ(n²)` states × `Θ(n)` splits, exactly `(n³−n)/6` inner iterations**
2. Why greedy fails for matrix chain? → **The split cost `d[i]·d[k+1]·d[j+1]` couples `i`, `k` and `j`, so no local rule works** (`(10,100,5,50)`: greedy 32 500 vs optimum 20 000)
3. How does palindrome partitioning reach `Θ(n²)`? → **Precompute `pal[i][j]` in `Θ(n²)` so the split predicate is `O(1)`**
4. The right algorithm for word break with a big dictionary? → **Aho–Corasick: `Θ(S + n)` instead of `Θ(n²)` or the `Θ(n³)` substring trap**
5. The two attacks that turn `Θ(n³)` into `Θ(n²)`? → **Precompute the split predicate, and exploit monotonicity of `opt` (Knuth/SMAWK) via the quadrangle inequality**