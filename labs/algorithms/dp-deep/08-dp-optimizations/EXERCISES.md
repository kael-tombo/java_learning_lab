# EXERCISES — DP Optimizations

## Level 1 — Sliding Window Warm-Up

### 1.1 Sliding-window minimum, from scratch
Given `int[] a` and window `W`, output `min(a[i−W+1..i])` for every `i`. Implement with:
1. Brute force (`O(nW)`)
2. Sparse table (`O(n log n)`)
3. Monotone deque (`O(n)`)

**Trace (`a = [5,2,8,1,9,3], W = 3`):** windows `[5,2,8]→2`, `[2,8,1]→1`, `[8,1,9]→1`,
`[1,9,3]→1`. Answer `[2,1,1,1]`.
Deque trace: push 5 (deque `5`); push 2 (pop 5, deque `2`); push 8 (deque `2,8`); push 1 (pop 8, pop 2,
deque `1`); push 9 (deque `1,9`); push 3 (pop 9, deque `1,3`). Fronts: `2,2,1,1,1,1` ✓.

### 1.2 Minimum cost to make a string palindrome by deletions
`min deletions`. Naive interval DP `Θ(n²)`; note the transition window has width 1 → try the
in-place single-array sweep.

**Trace (`"abcda"`):** remove `b`, `c`, `d` → `3` deletions? Actually `aba` needs deleting `c`,`d`
then `b`: answer `2`.

### 1.3 "Constrained" edit distance with a window
Edit distance where at most `W` consecutive characters of `B` may be skipped. Transition:
`D[i][j] = min(D[i][j−1] + 1, D[i−1][j] + 1, D[i−1][j−1] + cost, min over t in [j−W, j−1] D[i−1][t])`.
The last term is a sliding-window min over the previous row. Naive `Θ(nmW)` → `Θ(nm)`.

## Level 2 — Deque with a Real Cost

### 2.1 Min cost path with a bounded number of turns
`D[i][j] = D[i−1][j] + a[i]` (no turn) or `min over t ≤ j of (D[t][j] + cost) + b` (turn).
Maintain one monotone deque **per column** `j`. Prove the total pushes across all columns is `Θ(n)`.

### 2.2 Longest subarray with at most K distinct
Not a DP, but the same technique: sliding window + a frequency array, two pointers.
Contrast with the DP formulation to see when the "window" framing wins.

**Trace (`[1,2,1,2,3], K=2`):** longest is `[1,2,1,2]` length 4.

### 2.3 Deque failure case
Construct an `A[t] + f(t,j)` transition where popping from the back is **wrong**, because the
ordering inverts as `j` grows. Then show a segment-tree replacement achieving `O(n log n)`.
This exercise exists to prevent over-confident deque use.

## Level 3 — Knuth

### 3.1 Merge cost DP
`D[i][j]` = min cost to merge `i..j` into one, merging adjacent, cost = size merged.
Naive `Θ(n³)`. Apply Knuth with `w(i,j) = (j − i + 1)²`.
Verify conditions: (1) `w(b,c) ≤ w(a,d)` since `b≥a, c≤d` so `c−b+1 ≤ d−a+1` ✓;
(2) quadrangle — verify algebraically, then compute the split count for `n = 10`.

### 3.2 Optimal BST
`D[i][j]` = min expected search cost for keys `i..j` with successful-search probabilities `p_i`.
`w(i,j) = −Σ p_k` (or `Σ p_k` weighted by depth). Compute in `O(n²)` with Knuth.
**Trace (n = 3, p = 0.2 each):** best root = key 2, cost `= 0.2·1 + 0.2·2 + 0.2·2 = 1.0`.

### 3.3 Matrix chain / polygon triangulation
Triangulate a convex polygon of `n` vertices minimising `Σ triangle_area`-ish product.
`O(n³)` → `O(n²)` with Knuth (here `w(i,j) = 0`, so conditions hold trivially).

### 3.4 RNA folding (Nussinov)
`D[i][j]` = max number of non-crossing complementary pairs in `i..j`.
`w(i,j) = −(number of possible pairs between i and j)` satisfies Knuth. Implement `O(n²)`.
**Trace (`"GCAUC"`, G-C and A-U pairs):** pairs `(G1,C3)`, `(A2,U4)`, `(C3,U4)` — non-crossing
max is `2` (`G1-C3`, `A2-U4`? C3 and U4 both used with C3; try `(G1,C3)` and `(A2,U4)` = 2).
Non-crossing requires `i < k < l < j`; `(1,3)` and `(2,4)` cross → max is `1`? Choose `(1,3)` alone
or `(2,4)` alone → **1**. Good edge case.

## Level 4 — Divide & Conquer Optimisation

### 4.1 1D/1D DP with convex cost
`D[j] = min over i < j of ( D[i] + C(j) − C(i) )` where `C` is convex.
Show the optima are monotone, then compute in `O(n log n)` by recursion.
**Trace (`C = x²`, `D[0] = 0`):** `D[j] = min_{i<j}(D[i] + j² − i²)`. This is "min cost to split
points on a line", a classic segmentation. Check `n = 5` by brute force and match.

### 4.2 Verify monotonicity empirically
For a small random instance, compute the full `opt` table by brute force and print it.
**Confirm it is monotone.** Then flip one cost to break convexity and watch `opt` zig-zag —
this is the empirical test that tells you whether the optimisation is safe for your instance.

### 4.3 Cost of the restricted search
Instrument the D&C version to count how many `k` candidates it tries. Show it is `O(n log n)`,
not `O(n²)`, by printing the count for `n = 2^10, 2^12, 2^14`.

## Level 5 — SMAWK / Monotone Opt

### 5.1 Row minima via SMAWK
Given an implicit `M[i][j] = D[i][j] + cost(i,j)` that is totally monotone, compute all row minima
in `O(n)`. Implement `reduce` (column reduction) + `recurse` + `interpolate`.
Verify the output matches brute-force row minima for `n = 8`.

### 5.2 Monotone pointer walk
When optima are *strictly* monotone, replace the recursive search with:
```java
int k = optPrev;
for (int j = 1; j < n; j++) { while (k + 1 < j && better(k + 1, j)) k++; opt[j] = k; }
```
Show it is `Θ(n)` because `k` only increases, total increments `≤ n`.

### 5.3 Decide: when is SMAWK worth it?
Write up a decision rule: measure row-search time; if it's `> 30%` of total and the cost function
is cleanly totally monotone, go SMAWK. Otherwise D&C.

## Level 6 — Memory and Bitsets

### 6.1 In-place LCS
Rewrite standard `Θ(nm)`-time / `Θ(m)`-space LCS as a single in-place array. Determine the
correct sweep direction by finding a recurrence where the naive direction breaks.

### 6.2 Second-order linear memory
`D[i][j] = max(D[i−1][j], D[i−2][j] + a[i])` — keep 2 rows. Show memory `O(m)` and that a
1-row version is wrong (needs `i−2`).

### 6.3 Bitset subset DP
Implement subset-sum reachability with a `long[]` bitset: `bits |= bits << v` per item.
`Θ(n·S/64)` vs `Θ(n·S)` boolean.
**Trace (items 3, 5, 17, target 22):** after 3: bit 3. after 5: bits 3,5,8. after 17:
bits 3,5,8,17,20,22,25 → target 22 reachable ✓.

### 6.4 Polynomial / FFT knapsack
Show that counting subset sums of multiplicity is a convolution of the polynomial
`Π(1 + x^{w_i})`, computable in `Θ(n log n)` via FFT — and that the *boolean* version
(saturating) cannot use FFT, which is why the bitset trick exists.

## Level 7 — Aliens Trick

### 7.1 Partition into `k` segments
Minimize `Σ (segment_cost)` for exactly `k` segments; then find the `k` that minimises
`cost + λk`. Binary search `λ` on integers.
**Trace (a = [1,2,3,4,5,6], k = 3):** segments `[1,2],[3,4],[5,6]` → `1+1+1 = 3`;
alternatives `[1],[2,3],[4,5,6]` → `1+1+1 = 3`. Best `= 3`.

### 7.2 Convexity check
On a small instance, compute `cost(k)` for all `k` and plot. Verify convexity; then break it
(a crafted instance) and observe the binary search fail.

## Level 8 — Edge Cases (all must pass)

| Case | Trap |
|------|------|
| Window `W` larger than `n` | Deque never front-pops; result = global min |
| `W = 1` | Deque degenerates to identity |
| All-equal `A` | Pop-with-`≥` vs `>` changes which index survives but not the value |
| Knuth `i == j` base | `opt` undefined; handle `L = 1` separately |
| `n = 0` / `n = 1` | Empty DP must return the identity element (0 or `∞`) |
| Negative costs | `-∞` init instead of `0` |
| `n` non-power-of-two in D&C | Midpoint recursion still correct; don't assume `2^k` |
| In-place sweep wrong direction | Silent wrong answers, not crashes |

## Level 9 — Stretch

9.1 **Combine**: windowed transitions *and* Knuth on one problem. Show the multiplicativity of
      the savings.
9.2 **Proof obligation**: write out the full correctness proof that the deque's front is the
      window min, including the "newer element dominates" lemma.
9.3 **Regression harness**: build a random-instance tester that compares every optimisation
      against the naive `O(n³)` reference for `n ≤ 12`, 10 000 trials. This is the only way to
      trust these implementations.