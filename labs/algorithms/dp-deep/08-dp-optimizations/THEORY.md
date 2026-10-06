# THEORY — DP Optimizations

## 0. The Shape of the Problem

A DP `D[i][j]` is expensive when its transition enumerates a range:

```
D[i][j] = agg over k in [L(i,j), R(i,j)] of ( D[i'][j'] + cost(...) )
```

The four classic accelerations each attack a *different* reason the enumeration is wasteful:

| Technique | What it exploits | Naive → fast |
|-----------|------------------|--------------|
| Sliding window / monotone deque | the range is contiguous and the score is monotone in `k` | `O(nW)` → `O(n)` |
| D&C optimisation | the argmin `opt[i][j]` is monotone in `j` | `O(n²)` → `O(n log n)` |
| Knuth | the argmin is monotone in *both* endpoints | `O(n³)` → `O(n²)` |
| SMAWK / monotone | totally monotone matrix of transitions | `O(n²)` → `O(n)` |

And one orthogonal axis: **memory**, since `D` is often only read one or two layers back.

## 1. Sliding Window and the Monotone Deque

### The canonical form
```
D[j] = min over t in [j-W, j-1] of ( A[t] + B[j] )
```
`B[j]` does not depend on `t`, so it factors out and the transition is a sliding-window **min** of
the array `A`. A `TreeMap` floor/ceiling or a sparse table gives `O(n log n)`; a **monotone
deque** gives amortised `O(n)`.

### The deque invariant
The deque holds indices in *increasing* index order and *strictly increasing* `A` value order.
When adding `t`, pop from the **back** every index `u` with `A[u] ≥ A[t]` — those can never win
again, because (i) `t` is newer so it leaves the window later, and (ii) `A[t] ≤ A[u]`.
When querying for window `[j−W, j−1]`, pop from the **front** every index `< j−W`.

**Correctness.** The deque front is always the minimum of the current window. *Proof.* Suppose
the true window minimum at index `m` was popped from the back by some later `t`. Then
`A[t] ≤ A[m]` and `t > m`, so `t` is in the window whenever `m` is, and `A[t] ≤ A[m]`. So `m`
was never the minimum after `t` arrived — no loss. Front pops only remove indices outside the
window. Hence the front is always a true window minimum. ∎

**Amortised bound.** Each index is pushed once, popped at most once (from either end).
Total pops `≤ n`, total pushes `= n`, so total `O(n)` for the whole scan. This is the
"potential function" argument: the potential is `|deque|`, which starts and ends at `0` and
never exceeds `n`; every operation changes it by `O(1)` and there are `n` pushes.

### When a deque does *not* apply
If `A[t] + f(t, j)` with `f` depending on both `t` and `j`, the popped element may become optimal
again later (because `f` changes the ordering). Then the deque is wrong. Correct alternatives:
- sparse table / segment tree → `O(n log n)`
- "monotone" only if `f` is separable or the ordering provably never inverts

## 2. Divide & Conquer Optimisation

**Assumption (quadrangle / Monge cost):** the optimal split point is monotone:
`opt[i][j] ≤ opt[i][j+1]`.

**Mechanism.** Instead of filling `D[i][·]` left to right, fill it recursively. For a row
segment `[L, R]`, compute the midpoint `M`, searching `k` only in
`[opt[i][L−1], opt[i][R+1]]`. Then recurse left with a tightened left bound and right with a
tightened right bound.

**Why it costs `O(n log n)`.** At recursion depth `d`, the searches for the `2^d` sub-segments
cover disjoint (or barely overlapping) ranges totalling `O(n + 2^d)` candidates. Summing over
`log n` depths: `O(n log n + 2^n)` → the linear term dominates until the last couple of levels,
giving `O(n log n)`.

**Where the assumption comes from.** It holds when the cost is **Monge**:
`cost(a, c) + cost(b, d) ≤ cost(a, d) + cost(b, c)` for `a ≤ b ≤ c ≤ d`. Splitting `cost` into
a base term plus a convexity-respecting term (e.g. `(x−y)²`, `|x−y|`, `x·y` with `x ≤ y`) makes
Monge easy to verify by direct algebra.

## 3. Knuth's Optimisation

**Setting.** Interval DP: `D[i][j]` = optimum over partitions of `[i..j]`, with
`D[i][j] = min over k in [i, j-1] of ( D[i][k] + D[k+1][j] + w(i, j) )` — note `w` does *not*
depend on `k`.

**Conditions** (for `a ≤ b ≤ c ≤ d`, `w` on intervals):
1. **Monotone**: `w(b, c) ≤ w(a, d)`
2. **Quadrangle**: `w(a, c) + w(b, d) ≤ w(a, d) + w(b, c)`

Then the **optima** satisfy `opt[i][j−1] ≤ opt[i][j] ≤ opt[i+1][j]`.

**Mechanism.** Fill `D` for increasing interval length `L = 1..n`. For `D[i][j]` of length `L`,
search `k` only in `[opt[i][j−1], opt[i+1][j]]`.

**Complexity.** Let `s(L)` be the total number of `k` candidates tried at length `L`. By the
monotonicity bound, `s(L) ≤ s(L−1) + n` (each `opt` value can be crossed by at most `n` splits
over the diagonal). Summing:
`Σ_{L=1}^{n} s(L) ≤ Σ (n + L) = O(n²)`. Since `opt[i][j−1] ≤ opt[i][j] ≤ opt[i+1][j]` and the
`opt` values along a row are non-decreasing, the total movement of the search pointer is bounded
by the number of cells, `Θ(n²)`. So `O(n²)` total instead of `O(n³)`.

**The key insight:** Knuth is D&C optimisation specialised to interval DP, exploiting monotonicity
in *both* endpoints simultaneously. That double monotonicity is what turns `log n` factors into
nothing.

**Classic `w` that satisfy Knuth** (with `i ≤ j`):
| Problem | `w(i,j)` |
|---------|----------|
| Optimal BST | `p_i · depth` sum |
| Matrix chain | `0` (i.e. `w(i,j) = 0`) — trivially Knuth |
| RNA folding | `−(# matched pairs)` for complementarity |
| Merge cost | `# elements` = `j − i + 1` (convex in length) |
| Merge stones | `S[j] − S[i]` (linear ⇒ both conditions trivially) |

## 4. SMAWK and Totally Monotone Matrices

**Definition.** A matrix `M` of size `n × n` is **totally monotone** if for all `i < i'`
and `j ≤ j'`: `M[i][j'] ≤ M[i][j]` implies `M[i'][j'] ≤ M[i'][j]`. Equivalently, if the
leftmost row-minimum of a submatrix is never strictly right of the leftmost row-minimum of a
super-matrix containing it.

**Theorem (SMAWK, 1987).** Every row-minimum of an `n × n` totally monotone matrix can be found
in `O(n)` evaluations of the matrix — while the matrix itself has `Θ(n²)` entries.

**Why that is possible.** You never materialise the matrix. DP transition matrices are
*implicit*: `M[i][j] = D[i][j'] + cost(i,j)` evaluated on demand in `O(1)`. Only `O(n)` evaluations
are ever needed because the structure forces the answers.

**Practical advice.** SMAWK is rare outside competitive-programming libraries. The monotone-opt
version (walk the pointer directly when the optima are strictly monotone) captures most of the
benefit at a fraction of the implementation risk. Know SMAWK; reach for it only when profiling
shows the `O(n log n)` row search is your bottleneck.

## 5. Memory: Linear-Space Rolling

If `D[i][·]` depends only on `D[i−1][·]` and `D[i−2][·]` (common: second-order state), keep two
rows, not `n`. If the transition is in-place-safe (reads a cell before overwriting), use one
array and sweep in the correct direction.

**Direction matters.** For `D[i][j] = min(D[i][j−1], D[i−1][j] + c)`, sweeping `j` **forward**
in a single array is correct: `D[j−1]` has already been overwritten with row `i` (which is what
we want) while `D[j]` still holds row `i−1` (also what we want). Both reads are correct by
construction — this is the classic in-place trick.

**Counter-example:** `D[i][j] = max(D[i][j−1], D[i−1][j−1])` (LCS-style). Forward sweep destroys
`D[i−1][j−1]` before it is read. Must sweep **backward** or keep two rows.

## 6. Bitset / Algebraic Speedups

When the DP state is boolean over a small domain, pack it into machine words:

- **Subset DP** (`Θ(n·2^k)` → `Θ(n·2^k/64)`): `dp |= dp << s` replaces the inner loop.
  Classic: longest common subsequence of *all* short strings, or subset-sum reachability.
- **Numeric-state DP**: only helps for booleans; `long` arithmetic cannot be "widened" this way.
- **FFT / polynomial multiplication**: knapsack / subset-sum over GF(2) or via counting
  convolution — `Θ(n log n)` instead of `Θ(n·W)`.

## 7. The Aliens (Lagrangian) Trick

When the DP has an extra parameter `k` (number of segments, tracks, groups) and `k` appears
only in the transition as a penalty `λ` per group:

```
F(λ) = min over all k of ( cost(k) + λ·k )      computable in Θ(n)
```

`F(λ)` is convex and decreasing in `λ`. Binary-search `λ` for the smallest value where the
optimal `k` jumps to at most the target, then read off the answer (possibly interpolating for
the fractional boundary). This replaces `Θ(nk)` with `Θ(n log V)` where `V` is the numeric range.

**Caveat:** requires the `cost(k)` curve to be convex in `k`. Non-convex cases break the
binary search — check convexity on small instances first.

## 8. When No Optimisation Applies

Honest failure cases:
- The argmin is genuinely non-monotone (verify with a brute-force `opt` table on small input —
  if it zigzags, neither D&C nor Knuth applies).
- The transition cost is neither Monge nor separable.
- `n` is small; `O(n²)` already runs in milliseconds and the optimised version risks bugs.
- The DP is inherently exponential (`Θ(n²2ⁿ)` TSP); windowing does not help because the
  `2ⁿ` term dominates.

**Rule of practice:** only optimise after profiling. Every optimisation here trades a proof you
must verify for constant factors — and each has at least one silent wrong-answer mode.