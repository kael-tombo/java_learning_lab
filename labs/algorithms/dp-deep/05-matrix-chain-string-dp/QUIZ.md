# Quiz — Matrix Chain & String DP

15 questions. Each key gives the reason.

---

## Q1
State the matrix-chain recurrence and count the inner iterations exactly.

<details><summary>Answer</summary>

```
cost[i][j] = 0                                                   if i == j
cost[i][j] = min over i <= k < j of ( cost[i][k] + cost[k+1][j] + d[i]·d[k+1]·d[j+1] )
```

**Inner iterations:** `Σ_{len=2}^{n} (n−len+1)(len−1) = (n³ − n)/6`.

**The constant is `1/6`, not 1** — a rectangular `for i, for j, for k` loop over all `n³` triples does **6× the necessary work**.

`n = 500` ⇒ `2.1·10⁷` ≈ 60 ms. `n = 2000` ⇒ `1.3·10⁹` ≈ 4 s. `n = 5000` ⇒ `2·10¹⁰` ✗.
</details>

## Q2
Why does greedy fail for matrix chain? Give the arithmetic.

<details><summary>Answer</summary>

The cost at split `k` is `d[i]·d[k+1]·d[j+1]` — it depends on **`i`, `k`, and `j` simultaneously**, so the decision at one level constrains every other level. No local rule is correct.

**Counterexample** with dims `(10,100,5,50)`:
- `((A1A2)A3)A4` = `5 000 + 2 500 + 25 000 = 32 500` (greedy's answer)
- `(A1A2)(A3A4)` = `5 000 + 12 500 + 2 500 = ` **`20 000`** (optimum)

**62.5% above optimal.** And on `(30×10, 10×60, 60×30)` both single products cost `18 000`, so no "cheapest first" rule distinguishes them — one tie-break gives `27 000`, the other `72 000`.
</details>

## Q3
What fill order does an interval DP require, and which other orders work?

<details><summary>Answer</summary>

**Increasing interval length** always works.

**`i` descending with `j` ascending** also works, and the reason is instructive: `dp[i][k]` needs the same `i` and a *smaller* `j` (j ascending supplies it), while `dp[k+1][j]` needs a *larger* `i` (i descending supplies it).

**`i` ascending with `j` descending works for neither** — it breaks one of the two.

Understanding *why* each order works (which axis each sub-interval differs in) generalises to every interval DP.
</details>

## Q4
Why is palindrome partitioning `Θ(n²)` and not `Θ(n³)`?

<details><summary>Answer</summary>

Because the split predicate `pal(j, i−1)` can be **precomputed in `Θ(n²)`**:

```
pal[i][j] = s[i]==s[j] && (j−i <= 1 || pal[i+1][j−1])
```

The naive version tests each `(i, j)` in `Θ(i−j)` ⇒ `Θ(n³)`. With the table, the transition is `O(1)` ⇒ `Θ(n²)`.

**General lesson:** a `Θ(n³)` split DP becomes `Θ(n²)` whenever the "can these combine?" predicate has an `Θ(n²)` precomputation.
</details>

## Q5
The Penney game. What is the equilibrium, and how is it computed?

<details><summary>Answer</summary>

The probability B wins against A's string `X` is a linear function of the **overlap matrix** `M[i][j] = δ(suffix of X of length |X|−i, prefix of Y of length j)`, each entry computed by the `Θ(len²)` edit-distance DP. Solving the linear system is `Θ(n³)`.

**Theorem (Penney 1974 / Conway 1983):** in the best-response game every symbol except the first is the same, and the optimal string is `HRRRRR…R` — **the same form for every alphabet.** So the game is entirely about *timing*, not symbol variety.

Counter-intuitive, and a beautiful demonstration of DP plus linear algebra producing a structural theorem.
</details>

## Q6
Word break: what are the three complexities, and which is "right"?

<details><summary>Answer</summary>

| implementation | time |
|---|---|
| `HashSet` + `s.substring` in the inner loop | `Θ(n³)` — `substring` copies |
| trie walk | `Θ(n·L)`, `L` = longest word |
| **Aho–Corasick** | **`Θ(S + n + matches)`**, `S = Σ|word|` |

**Aho–Corasick is right** because the DP's inner loop asks "which dictionary words end here?" — exactly what a multi-pattern automaton answers in `O(1)` amortised per position with output links. At `n = 10⁴` and `|dict| = 10⁴` that is `10⁵` instead of `10⁸`: a **1000×** win.
</details>

## Q7
Why must all-segmentations be capped, and what is the output size?

<details><summary>Answer</summary>

`s = "a"×40` with dictionary `{a, aa, aaa, aaaa}` has `2³⁹ ≈ 5.5·10¹¹` segmentations. The output is exponential and the algorithm is **output-optimal** — but an uncapped implementation is a **denial-of-service vector**, not merely a slow path.

A 40-byte input can exhaust all memory. Production code must cap the per-index list size and fail loudly.
</details>

## Q8
State the RNA Nussinov recurrence and its fill-order justification.

<details><summary>Answer</summary>

```
N[i][j] = 0                                                    if j <= i+1
N[i][j] = max( N[i+1][j],
               max over i <= k <= j−2 with pairable(i,k)
                   of ( 1 + N[i+1][k−1] + N[k+1][j] ) )
```

**Fill by increasing length:** `N[i+1][k−1]` has length `k−i−1 < j−i` ✔ and `N[k+1][j]` has length `j−k < j−i` ✔.

`Θ(n³)`, `Θ(n²)` space, constant `≈ 1/6` halved by pairability (only `A-U`, `C-G`). **Practical limit `n ≈ 500`; real RNA is `n = 10³–10⁵`, which is why ViennaRNA uses SIMD and `O(n³/logn)` parallel folding.**
</details>

## Q9
Prove burst balloons and matrix chain are the same algorithm shape.

<details><summary>Answer</summary>

Both have:
- **States:** intervals `[i, j]` ⇒ `Θ(n²)`.
- **Transitions:** split at `k ∈ (i, j)` ⇒ `Θ(n)` each.
- **Time:** `Θ(n³)`; **space:** `Θ(n²)`.
- **Fill:** increasing interval length.

They differ only in the combine function (`min` of `d[i]d[k+1]d[j+1]` vs `max` of `nums[i]nums[k]nums[j]`) and in the boundary handling (sentinels vs dimension indices). LeetCode 1031, 312, and 1130 are all this shape.

**Recognising the shape is the transferable skill; memorising three recurrences is not.**
</details>

## Q10
What is the general structure shared by every problem in this lab, and what are the three ways to attack it?

<details><summary>Answer</summary>

**State graph:** `Θ(n²)` interval states, `Θ(n³)` edges ⇒ `Θ(n³)`.

Attack the `Θ(n)` transitions-per-state factor:
1. **Precompute the predicate** — `Θ(n³) → Θ(n²)` (palindrome table).
2. **Exploit monotonicity of `opt`** — Knuth's optimisation (`Θ(n²)`) or divide-and-conquer (`Θ(n log n)` inner loop), both requiring the quadrangle inequality.
3. **SMAWK** — `Θ(rows + cols)` comparisons for all row minima ⇒ `Θ(n²)` total.

Attack the state count with rolling arrays (space only). Lab `08-dp-optimizations` is the systematic treatment of (1)–(3).
</details>

## Q11
What is the quadrangle inequality, and what does it buy?

<details><summary>Answer</summary>

For a cost function `w`, the **quadrangle inequality** is `w(a,c) + w(b,d) ≤ w(a,d) + w(b,c)` for `a ≤ b ≤ c ≤ d`. Together with monotonicity `w(b,c) ≤ w(a,d)`, it implies the **Monge property**, hence that row minima are monotone in the column index.

**Buys:** Knuth's optimisation restricts the split to `[opt[i][j−1], opt[i+1][j]]`, and the windows telescope so the total is `Θ(n²)` instead of `Θ(n³)`. Optimal BST is the canonical example.

**Caveat:** the constant factor of these optimisations is real; for `n ≤ 500` the plain `n³/6` DP often wins. Measure.
</details>

## Q12
Why does the naive word-break implementation become `Θ(n³)`?

<details><summary>Answer</summary>

`s.substring(j, i)` allocates and copies `i − j` characters. Inside the `Θ(n²)` DP loop, that adds `Θ(Σ (i−j)) = Θ(n³)`.

Fixes: `HashSet` with precomputed substring hashes (`O(1)` lookup), a trie (`Θ(n·L)`), or Aho–Corasick (`Θ(S + n)`).

**At `n = 5000` the difference is `1.25·10¹¹` character copies versus `Θ(S + n)` — this is not a micro-optimisation, it is a different complexity class in practice.**
</details>

## Q13
In production, do you need the matrix-chain DP? Why or why not?

<details><summary>Answer</summary>

**Usually not.** For fixed chains of small matrices the JIT's escape analysis and inlining optimise the parenthesisation away entirely; the cost is a compile-time constant.

You need the DP when:
- the "matrices" are really **strings, trees, or intervals** (palindrome partitioning, RNA, game scoring),
- the chain is large enough that the constant matters (`n > 30`),
- you need the **optimal parenthesisation itself**, not the numeric result (e.g. to emit it).

**The DP is a teaching vehicle and a general-purpose tool. Its recurrence is what transfers.**
</details>

## Q14
`Θ(n³)` for `n = 10⁴`. What are the real-world responses, in order of preference?

<details><summary>Answer</summary>

1. **Specialise the constant.** Only `~25%` of RNA `(i,k)` pairs are pairable, so a pairability filter is `2×`. SIMD on the inner loop is `2–5×` (ViennaRNA reports both).
2. **Go parallel.** The `Θ(n²)` cells partition cleanly by anti-diagonal: `Θ(n)` stages, each `Θ(n²/p)` per thread ⇒ `O(n³/logn)`.
3. **Exploit structure.** Quadrangle inequality ⇒ Knuth/SMAWK to `Θ(n²)`. Problem-specific structure ⇒ `Θ(n log n)` (Hu–Shing).
4. **Approximate.** `O(n²)` grammar-based or probabilistic folding for very long sequences.

**None of these problems are NP-hard**, so "declare it NP-hard" is never the answer here — the answer is always "exploit the structure", which is lab `08`'s subject.
</details>

## Q15
State the one sentence that would prevent the most bugs in this family.

<details><summary>Answer</summary>

**"The fill order is part of the specification, and the fill order is by increasing interval length — not by increasing `i`, not by increasing `j`."**

And the corollary for the combine function: **the `Θ(n²)`-space version with a recorded split index is the reference; any fill-order claim you cannot verify by checking that both sub-intervals are ready is a bug you have not found yet.**
</details>