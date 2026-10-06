# MATH_FOUNDATION — DP Optimizations

## 1. Why the Master Theorem Mostly Does Not Apply

The Master theorem characterises `T(n) = aT(n/b) + f(n)`. Only a few of these techniques
(interval DP viewed recursively) have that shape. Sliding windows, monotone deques, and SMAWK are
all **iterative / amortised**, so the right tools are:

1. **Potential functions** — for the amortised deque bound.
2. **Summing over levels** — for D&C optimisation.
3. **Direct counting of movements** — for Knuth.

## 2. Amortised Analysis of the Monotone Deque

**Potential method.** Let `Φ(S) = |deque|`, the number of live indices. Facts:
- `Φ ≥ 0` always.
- `Φ(S_final) ≤ n` (at most `n` pushes, no other growth).
- For each operation, `ΔΦ` is: push `+1`; front-pop `−1`; back-pop loop `−k` for `k ≥ 0`.

The back-pop loop is the one that needs care. Amortised cost of a back-pop is charged to the
element being popped: each element is pushed once and popped at most once, so

```
Σ (cost of all operations) = Σ over elements (1 push + ≤1 pop) = O(2n) = O(n)
```

**Equivalently, per-operation amortised cost.** Total work `W ≤ 2n`, number of operations
`m ≥ n` (at least one push per element), so `W/m ≤ 2n/n = 2` — amortised `O(1)` per operation.

**Contrast with the naive sliding window:** `Θ(nW)`. For `W = Θ(n)` that is `Θ(n²)` vs `Θ(n)` —
a factor of `n`.

**Lower bound sanity check.** Any sliding-window minimum must at least read every element
(change one element, change the answer), so `Ω(n)` — the deque is asymptotically optimal.

## 3. D&C Optimisation: Summing Over Recursion Levels

Consider one row with `n` candidate splits. The recursive procedure computes row segment `[L,R]`
at midpoint `M`, searching only `[opt[L−1], opt[R+1]]`.

**Level accounting.** At recursion depth `d` there are `2^d` sub-segments. Because optima are
non-decreasing, the search ranges of *sibling* segments are ordered and their union length is
`opt[R+1] − opt[L−1] ≤ n`. Sibling segments' ranges are disjoint except at boundaries, so total
candidates at depth `d` is `≤ n + 2^d·O(1)`:

```
T(n) = 2·T(n/2) + O(n)   per level
```

Applying the Master theorem with `a = 2, b = 2, f(n) = n`: `n^(log_b a) = n^1 = n`, and
`f(n) = n = Θ(n)`, so case 2 applies: **`T(n) = Θ(n log n)`**. ✓

**Total across the DP:** the row search is `Θ(n log n)`, repeated for `n` rows would be
`Θ(n² log n)` — worse than `Θ(n²)`. So in practice D&C optimisation is applied to the
*transposed* formulation (one column at a time, or a single long dimension), giving
`Θ(n²)` → `Θ(n log n)` overall. Important nuance: the `log` is only a win when the DP is a
"one long dimension, one short" shape. For a genuinely square `n × n` DP, D&C optimisation must
be applied so the long axis is what gets halved.

## 4. Knuth: Counting Split Candidates

At length `L`, cells are `(i, i+L−1)` for `i = 1..n−L+1`. Cell `(i,j)` searches
`[opt[i][j−1], opt[i+1][j]]`.

Define `S_L` = total candidates tried at length `L`. Since `opt` is non-decreasing along a row,
the search pointer for consecutive `i` values at fixed `L` only moves right:

```
S_L = Σ_i (opt[i+1][i+L−1] − opt[i][i+L−2] + 1)
```

Telescope! Setting `f(i) = opt[i+1][i+L−1]`, note `opt[i][i+L−2]` is the same quantity shifted,
so `Σ_i (f(i) − f(i−1)) = f(last) − f(first)`:

```
S_L ≤ (opt[n−L+2][n] − opt[1][L]) + (n − L + 1) ≤ n + (n − L + 1) ≤ 2n
```

Therefore `S_L = O(n)` per length, and

```
Total = Σ_{L=1}^{n} O(n) = O(n²)
```

versus the naive `Σ_L (n−L+1)·Θ(L) = Θ(n³)`. **The telescoping is the whole argument** — it is
why the double monotonicity (`opt[i][j−1] ≤ opt[i][j] ≤ opt[i+1][j]`) is exactly the right
hypothesis: it makes the sum telescope.

**Refined bound.** `Σ_L S_L = Θ(n²)` is tight in general (optimal BST is `Θ(n²)` and no
sub-`n²` algorithm is known for general weights).

## 5. Proving Monge from a Convex Function

Let `c(x, y) = g(y) − g(x)` for a convex, non-decreasing `g` (a "prefix-sum" cost). For
`a ≤ b ≤ c ≤ d`:

**Monotone:** `w(b,c) = g(c) − g(b) ≤ g(d) − g(a) = w(a,d)` since `g(c) ≤ g(d)` and `g(b) ≥ g(a)`. ✓

**Quadrangle:**
```
w(a,c) + w(b,d) = (g(c) − g(a)) + (g(d) − g(b))
w(a,d) + w(b,c) = (g(d) − g(a)) + (g(c) − g(b))
```
Both sides are **identical**. So the quadratic inequality holds with **equality** for every
prefix-sum cost. Hence every "merge stones"-style DP (`w(i,j) = S[j] − S[i]`) is Knuth-eligible,
which is why the technique generalises so widely.

## 6. SMAWK's Complexity

Column reduction halves the number of columns per recursion level. At depth `d` the matrix is
`(n − d) × n/2^d`-ish. The recursion has `Θ(log n)` levels and each level does linear work:

```
T(n) = T(n/2) + O(n)   ⟹   T(n) = O(n log n)
```

The extra `log n` is removed by the observation that column reduction does *strictly* more work
than the simple halving (it discards columns that can never be row minima, so subsequent levels
shrink faster), yielding `T(n) = O(n)` overall. SMAWK is constructive: the "hard part" is that
each column reduction permanently eliminates columns, so the total number of *evaluations* over
the whole run is `Θ(n)`, matching the lower bound of `Ω(n)` (each row minimum must be
distinguished from at least one neighbour).

## 7. Bitset Arithmetic

Packing `S` booleans into `⌈S/64⌉` machine words and doing `bits |= bits << v` performs `S`
boolean updates in `S/64` word operations. This is a legitimate `Θ(w/64)` speedup because a
64-bit word op is a *single* CPU instruction while a boolean update also costs one op — the win
comes from doing 64 of them per instruction.

**Complexity:** `Θ(n·S/64)` vs `Θ(n·S)`. Formally `Θ(nS)` since 64 is a constant — the honest
claim is a **64× constant-factor speedup** (real, but not asymptotic). Always state it that way.

**Why FFT cannot replace it:** FFT computes polynomial products over a *ring*, requiring
multiplication and addition. Boolean reachability uses OR, and more importantly is not
associative-compatible with the shift-and-OR recurrence in a way that admits polynomial
convolution. The *counting* version (how many subsets give sum `s`) *is* a convolution and *can*
use FFT at `Θ(n log n)`.

## 8. The Aliens Trick

Define `G(k) = cost(k)` (optimum with exactly `k` segments) and
`F(λ) = min_k (G(k) + λk)`.

**Claim (convex duality).** If `G` is convex, `F` is convex and non-increasing in `λ`, and its
lower convex envelope is `G`. *Proof sketch.* `F` is the pointwise minimum of the family of
lines `{G(k) + λk}_k` — a minimum of affine functions is concave in `λ`, hence convex where it
is finite. And `F(λ) ≤ G(k) + λk` for all `k`, with equality at the minimiser. For convex `G`,
the supporting-line duality of convex analysis (Fenchel–Moreau) guarantees that some `λ`
recovers each `G(k)` as `F(λ) − λk`. ∎

**Consequence.** Instead of computing all `n` values of `G` (cost `Θ(n²)` for a `Θ(nk)` DP), you
binary-search `λ` over integers in `[0, V]`:
`O(log V)` evaluations, each `Θ(n)` by folding the `k` dimension into a 1-D DP → `Θ(n log V)`.

**Boundary handling.** When `F(λ)` and `F(λ+1)` return optimal `k` values straddling your
target `k*`, recover the answer by linear interpolation:
`cost(k*) = (k_+ − k_*)·F(λ)/k_+ ...` — concretely `G(k*) = F(λ) − λk*` computed with the
fractional step, which is why implementations usually return a rational/real value there.

**Failure mode.** If `G` is non-convex, `F` is no longer convex, its minimiser in `λ` is not
monotone, and binary search returns a wrong `k` **with no error**. Always verify convexity of
`G` on small instances first.

## 9. Summary Table of Speedups

| Technique | Recurrence | Before | After | Proof tool |
|-----------|-----------|--------|-------|------------|
| Monotone deque | sliding window | `Θ(nW)` | `Θ(n)` amortised | potential `|deque|` |
| Knuth | interval DP | `Θ(n³)` | `Θ(n²)` | telescoping sum of `opt` |
| D&C | 1D/1D convex | `Θ(n²)` | `Θ(n log n)` | Master, case 2 |
| SMAWK | totally monotone | `Θ(n²)` | `Θ(n)` | column reduction counting |
| Rolling rows | any layered | `Θ(nk)` space | `Θ(k)` space | dependency depth |
| In-place | special recurrences | `2Θ(m)` | `Θ(m)` | read-before-overwrite ordering |
| Bitset | boolean subset | `Θ(nS)` | `Θ(nS/64)` | word-parallelism (constant factor!) |
| Aliens | `k`-parameter DP | `Θ(nk)` | `Θ(n log V)` | convex duality |