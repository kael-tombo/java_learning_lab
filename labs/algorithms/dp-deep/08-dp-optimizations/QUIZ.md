# QUIZ — DP Optimizations

1. What is the time complexity of a sliding-window minimum over `n` elements with window `W`, using a monotone deque, and why is it amortised rather than worst case?
2. When you insert index `t` into the deque, which end do you pop from and what is the exact pop condition?
3. Why is popping from the back safe — i.e. why can the popped element never be the future window minimum?
4. Give a counter-example where a monotone deque is *incorrect* for the transition `D[j] = min_t (A[t] + f(t, j))`.
5. State the two conditions Knuth's optimisation requires of an interval cost `w`.
6. What monotonicity relation do the optimal split points satisfy under Knuth?
7. What does the quadratic inequality `w(a,c) + w(b,d) ≤ w(a,d) + w(b,c)` mean intuitively?
8. Knuth optimisation turns `O(n³)` interval DP into what complexity, and why (the amortised split count)?
9. What extra structure does divide & conquer optimisation assume that Knuth does not need?
10. Define a totally monotone matrix precisely.
11. What does SMAWK compute, and in how many matrix evaluations, for an `n × n` matrix?
12. Why is SMAWK applicable to DP at all, given DP transition matrices have `Θ(n²)` entries?
13. For the recurrence `D[i][j] = max(D[i][j−1], D[i−1][j−1])`, which sweep direction is safe for in-place single-array computation?
14. Why does `D[i][j] = min(D[i][j−1], D[i−1][j] + c)` allow a *forward* in-place sweep?
15. The aliens trick replaces `O(nk)` with what, and what structural hypothesis does it require?

---

## Answers

1. **`O(n)` amortised.** Each index is pushed exactly once and popped at most once (from either
   end), so total pushes `= n` and total pops `≤ n`. Amortised because a single element *can*
   linger in the deque for many query steps, but each element's total cost is bounded by its one
   push plus its one pop. Equivalently, with potential `Φ = |deque|`, every operation changes `Φ`
   by `O(1)` and `Φ ≥ 0`, so the total is `O(n)`.
2. **The back.** Pop from the back every index `u` with `A[u] ≥ A[t]` (using `≥` keeps the
   *newest* of equal values, which leaves the window later and is therefore strictly better).
3. **Two facts combine:** (a) `A[t] ≤ A[u]`, so `u` is never strictly better; (b) `t > u`, so
   whenever `u` is still inside a future window, `t` is also inside it (windows slide forward, so
   newer indices expire later). Therefore any future window containing `u` also contains a value
   no larger — `u` can never be the unique minimum.
4. Any `f` whose effect on the ordering of `A[t] + f(t, j)` *changes with `j`*. Concrete:
   `A = [0, 100, 0]`, `f(t, j) = −t·j`. At `j = 1` the scores are `−1, 98, −3`, so index 2 wins.
   But index 2 (`A = 0`, same as index 0) would have been popped when index 2 arrived under a
   deque that assumes a fixed order — yet at `j = 2` the scores are `0, −100, −6` and index 1 wins,
   which the deque already discarded. Correct data structure: segment tree, `O(n log n)`.
5. For all `a ≤ b ≤ c ≤ d`:
   (i) **Monotone**: `w(b, c) ≤ w(a, d)`
   (ii) **Quadrangle inequality**: `w(a, c) + w(b, d) ≤ w(a, d) + w(b, c)`
6. `opt[i][j−1] ≤ opt[i][j] ≤ opt[i+1][j]` — the optimal split point is non-decreasing in *both*
   endpoints. That double monotonicity is precisely what makes the restricted search valid.
7. It says the cost is **superadditive across a "crossing" decomposition**: splitting the outer
   interval `[a,d]` and the inner `[b,c]` costs no more than splitting `[a,c]` and `[b,d]`.
   Equivalently, the interval cost is "convex" in the sense that enlarging the interval by the
   same amount at both ends costs proportionally more. This is what makes the optimal split
   behave monotonically.
8. **`O(n²)`.** At each interval length the searches are confined to
   `[opt[i][j−1], opt[i+1][j]]`, and the total pointer movement along the length-`L` diagonal is
   `O(n + L)`; summing over `L = 1..n` gives `O(n²)`. The naive version tries all `Θ(n)` splits
   at each of `Θ(n²)` cells → `Θ(n³)`.
9. Knuth needs the *specific* pair of conditions (monotone + quadrangle) on the cost function.
   D&C optimisation only needs **monotonicity of the argmin**, `opt[i][j] ≤ opt[i][j+1]` — often
   provable more directly (e.g. any Monge cost satisfies both, but so does "the cost decreases
   with segment length", which is not a Knuth condition). D&C gives `O(n log n)`, weaker than
   Knuth's `O(n²)` from `O(n³)` in ratio terms but applicable to more problems.
10. A matrix `M` is totally monotone if for all `i < i'` and `j ≤ j'`:
    `M[i][j'] ≤ M[i][j]` ⟹ `M[i'][j'] ≤ M[i'][j]`. Equivalently, the leftmost row-minimum index
    is non-decreasing as you take super-matrices — i.e. it is preserved under arbitrary row and
    column deletion.
11. **Every row-minimum**, in `O(n)` evaluations (and `O(n)` total time) of the `n × n` matrix.
    Naively computing all row minima costs `Θ(n²)` evaluations. SMAWK's output uses `Θ(log n)`
    evaluations per row but only `O(n)` in aggregate due to column reduction.
12. Because the DP transition matrix is **implicit**: `M[i][j]` is a formula
    (`D[i][j'] + cost(i,j)`) evaluable in `O(1)` without being stored. SMAWK's algorithm only
    ever queries `O(n)` entries, so the `Θ(n²)` "size" is never paid. This is the key insight —
    total monotonicity makes most entries irrelevant.
13. **Backward** (decreasing `j`). `D[i][j−1]` must be the *current* row's value, so `j−1` must
    already be computed — hence descending `j`. And `D[i−1][j−1]` must still be the *previous*
    row's value, which it is because we have not yet reached `j−1` in the descending sweep. A
    forward sweep would overwrite `D[j−1]` with row `i` before row `i`'s cell `j` reads it,
    silently producing wrong answers (no exception, no `ArrayIndexOutOfBounds`).
14. Sweeping `j` ascending: when computing `D[j]` we read `D[j−1]`, which the current sweep has
    *already* written with the row-`i` value — correct, because the recurrence wants `D[i][j−1]`.
    We also read `D[j]`, which has not yet been touched this row and therefore still holds
    `D[i−1][j]` — also correct. Both reads land on exactly the row the recurrence specifies, so
    one array suffices. This "each read finds the value the recurrence wanted by construction"
    is the whole trick, and it fails whenever the recurrence reads a cell *behind* the pointer
    that belongs to the previous row (see Q13).
15. **`O(n log V)`**, where `V` is the range of the penalty parameter. The trick: define
    `F(λ) = min_k (cost(k) + λ·k)`, computable in `O(n)` by folding the `k` dimension away
    entirely; binary search `λ` for the boundary. It requires the `cost(k)` curve to be
    **convex** in `k` so that `F` is convex and monotone and the binary search is valid. If
    `cost(k)` is non-convex, `F` is non-convex and the search silently returns the wrong `k`.