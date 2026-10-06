# Exercises — LCS & Edit Distance

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.lcsed`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Fill the LCS table by hand

`A = "ABCBDAB"`, `B = "BDCABA"`. Fill the full `7 × 6` table.

```
        ""  B  D  C  A  B  A
   ""     0  0  0  0  0  0  0
   A      0  0  0  0  1  0  1
   B      0  1  0  0  1  2  1
   C      0  0  0  1  1  2  1
   B      0  1  0  1  1  3  2
   D      0  1  1  1  1  3  2
   A      0  1  1  1  2  3  3
   B      0  1  1  1  2  4  3
```

Answer = **4**. Now backtrack, always preferring `L[i-1][j]` on ties, and write out the alignment. You should get `"BCBA"` or `"BDAB"` — **both length 4; the tie-break decides which.**

**Then:** change the tie-break to prefer `L[i][j-1]` and confirm you get the other one. Write one sentence on why both are optimal.

---

## Exercise 2 — The rolled DP, and its three bugs

Implement `lcsLen` rolled. Then find the **smallest** input for each bug:

| bug | change |
|-----|--------|
| R1 | omit `diagonal = up;` |
| R2 | `dp[0] = 0;` at the top of the outer loop *and* no `diagonal` init (set `diagonal = dp[0]` before overwriting) |
| R3 | `if (a.length < b.length) swap` removed |
| R4 | `dp[j] = (a[i-1]==b[j-1]) ? diagonal + 1 : Math.max(dp[j-1], dp[j])` (diagonal not read on mismatch — harmless?) |

For R1, verify: **the first row is always correct.** Write the smallest failing instance and explain why row 1 escapes.

For R3, explain the memory implication and construct a case where R3 uses `Θ(n)` instead of `Θ(min(n,m))`.

---

## Exercise 3 — Edit distance, full and rolled

Fill the Levenshtein table for `A = "kitten"`, `B = "sitting"` (6×7). Answer **3**.

Then produce the edit script by backtracking and verify it transforms `kitten` → `sitting` in 3 operations.

**Now the important experiment:** compute `|A| + |B| - 2·LCS(A,B)` for these inputs and compare to the true Levenshtein:

| `A` | `B` | LCS | insdel formula | Levenshtein | equal? |
|-----|-----|-----|---------------|-------------|--------|
| `kitten` | `sitting` | 4 | `12 - 8 = 4` | 3 | **no** |
| `aaaa` | `bbbb` | 0 | 8 | **4** | **no** |
| `abc` | `bca` | 2 | `6-4 = 2` | 2 | yes |
| `xab` | `abc` | 2 | 2 | 2 | yes |
| `abab` | `baba` | 3 | `8-6 = 2` | 2 | yes |

**Answer in writing:** when exactly are the two metrics equal? (They coincide when no substitution is used in an optimal script — equivalently when the alignment has no diagonal moves with cost 1.) Give a 4-line proof.

---

## Exercise 4 — Bit-parallel LCS

1. Implement `lcsBitParallel` for `m ≤ 64`.
2. **Trace it by hand** for `a = "abc"`, `b = "bac"`:
   - Build `M['a']`, `M['b']`, `M['c']` as 3-bit values.
   - Show `V` after each of the three characters.
   - Confirm the final `popcount` is 2.
3. Fuzz against `lcsLen` for 100 000 random `(a, b)` with `m ∈ [0, 64]` and alphabets of size 1, 2, and 26.
4. **Test the boundary `m = 63` and `m = 64` explicitly** — the sign-bit case. Find whether `m = 64` works; if not, document the workaround.
5. Benchmark: `n = m = 10⁴`, `n = 10⁵`, `n = m = 10⁵` (mask memory: `256 × 1563 × 8 = 3.2 MB`). Report the crossover where bit-parallel beats the rolled DP, and note where the mask memory becomes the bottleneck.
6. Implement the multi-word version and report how much of the speedup survives. **Then answer in writing whether it is worth shipping.**

---

## Exercise 5 — Hirschberg: correctness and the time bound

1. Implement `lcsHirschberg` (split `A` only) and assert `returned.length == lcsLen(a, b)` for 50 000 random pairs with `|a|,|b| ≤ 12`.
2. Instrument it: count total cell-visits for `n = m ∈ {16, 32, 64, 128, 256}` and fit the exponent. **Predict `nm log n` before running.**
3. Implement `lcsHirschbergFast` (split the longer string) and repeat. **Predict `nm` before running.** Plot both on log-log axes.
4. Demonstrate that `n = m = 10⁵` is impossible with the full table (`10¹⁰` ints = 40 GB) but works with Hirschberg. Report wall-clock.
5. **Answer:** why does splitting only `A` give `Θ(nm log n)` while splitting the longer string gives `Θ(nm)`? (One paragraph, referencing the level-by-level work decay.)

---

## Exercise 6 — Damerau / OSA

1. Implement `osa` and verify:
   - `osa("ca","ac") == 1`, `osa("ab","ba") == 1`
   - `osa` agrees with Levenshtein whenever no transposition helps
2. **Find a pair where OSA and unrestricted Damerau-Levenshtein differ.** (Hint: `"CA"` → `"ABC"` → `"AC"` style chains. Search exhaustively over all strings of length ≤ 3 over `{A,B,C}` and report the smallest witness.)
3. **Prove the triangle-inequality violation** for OSA with a brute-force search: find `A, B, C` with `osa(A,C) > osa(A,B) + osa(B,C)`. Report the smallest such triple.
4. **Consequence:** implement a BK-tree over OSA distances and show it returns a wrong nearest neighbour on that triple, while the same BK-tree over true Levenshtein is correct. This is a real bug you would ship.

---

## Exercise 7 — Myers's `O(ND)`

1. Implement Myers with parent recording so you can extract the script without replay.
2. **Instrument `D`** for inputs: identical, one edit, prefix change, suffix change, interleaved moves, random 10%, random 50%, random.
3. Measure `Θ((n+m)D)` vs the `Θ(nm)` DP for `n = m = 10⁴` at `D = 10, 100, 1000, 10⁴`. **Find the crossover: predict `D* = min(n,m)/2 = 5000`.**
4. Implement the **production hybrid**: common prefix strip → common suffix strip → Myers with a `D` cap → `Θ(nm)` fallback. Measure the whole hybrid on `n = m = 10⁶` with a random single-line edit. Report speedup over pure `Θ(nm)` (**expect 100–1000×**).
5. **Answer:** why does real `diff` need the `D` cap? What is the pathological input, and what does `git diff` do about it?

---

## Exercise 8 — Banded / `k`-mismatch

Implement `withinK(a, b, k)`. Validate against `editDistance(a,b) <= k` for 100 000 random pairs with `k ∈ {0,1,2,5}` and lengths ≤ 20.

Then benchmark: `n = 10⁶`, `k ∈ {1, 2, 4, 8}` against the full DP. **Predict `Θ(nk)` and the crossover.**

Finally: implement the **Ukkonen k-mismatch algorithm for multiple patterns**, which gives `Θ(n · m/w)` for all patterns of one length (not `Θ(nk)` per pattern). Show that for 100 patterns of length 20 it is faster than 100 banded searches.

---

## Exercise 9 — Substring vs subsequence vs prefix

Implement three problems and confirm they differ:

| problem | state | `A = "ABCBDAB"`, `B = "BDCABA"` |
|---------|-------|-----------------------------------|
| LCS (subsequence) | prefixes | 4 |
| Longest common **substring** | prefixes + `else 0` | 2 (`"BC"`? compute it) |
| Longest common **prefix** | prefixes, only `dp[i][i]` | 0 |
| Longest common **subsequence with no adjacent gap** | 2-D state | compute |

Then implement the **suffix-automaton LCS**: build a suffix automaton for `A` in `Θ(|A|)` and answer LCS(`A`, `B`) in `Θ(|B|)`. Benchmark against the `Θ(nm)` DP for `|A| = 10⁵`, `|B| = 10³`, many queries.

**Answer:** when is one-suffix-many-queries the right shape? (Answer: many LCS queries against the same reference — bioinformatics, plagiarism detection against a corpus, `diff` over a tree of revisions.)

---

## Exercise 10 — Debugging drills

1. `lcsLen` with `dp[j] = Math.max(dp[j], dp[j-1])` in the **match** branch too — what does it compute?
2. `editDistance` with `dp[0] = 0` per row (the LCS boundary) — find the smallest failing input.
3. `lcsTable` with `L[i][j] = Math.max(L[i-1][j], L[i][j-1], L[i-1][j-1] + (a[i-1]==b[j-1] ? 1 : 0))` — is it wrong? By how much? (This is the "always take max including the diagonal" variant — measure the gap.)
4. Hirschberg with `split` used as `B[0, split-1]` — find the smallest failing input.
5. `lcsBitParallel` with `M` built as `1L << (j + 1)` — what is wrong?
6. `osa` rolled to **one** row — find the smallest failing input.
7. Myers with `k += 2` replaced by `k++` — what happens? (State count doubles; correctness?)
8. `withinK` with the band `|i-j| < k` instead of `≤ k` — find the smallest failing input.

---

## Exercise 11 — Deliverable

`MINI_PROJECT/AlignViz.java`: render the `n × m` DP table for two short strings, colour-coding each cell by which transition produced it (diagonal / up / left), and overlay the backtracked alignment path.

Then `BENCHMARK/SimilarityRace.java` producing a markdown table: full-table / rolled / Hirschberg / HirschbergFast / bit-parallel / Myers-hybrid / banded, for `(n,m) ∈ {(10²,10²), (10³,10³), (10⁴,10⁴), (10⁵,10⁵)}` and edit distances `{0, 1% , 10%, 50%}`.

**Answer in writing:** for each `(n, m, D)` regime, which algorithm wins, and what single property of the input decides it? (Expected answer: `D/n` — the edit distance relative to the length. That ratio is the hidden parameter that selects the algorithm.)