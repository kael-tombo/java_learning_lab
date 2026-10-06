# 02 — LCS & Edit Distance

<div align="center">

**Longest Common Subsequence · Levenshtein Edit Distance · Damerau-Levenshtein · Hirschberg Linear-Space · Bit-Parallel LCS**

</div>

---

## Learning Objectives

- Derive the `Θ(n·m)` recurrence for LCS and edit distance from first principles, not from memory
- Implement both with a `Θ(min(n,m))`-space rolled table and explain the `diagonal` save
- Implement Hirschberg's linear-space divide-and-conquer for LCS and edit distance
- Understand **why** `O(n·m/64)` bit-parallelism is possible for LCS and what the word-sized constraint limits
- Implement Damerau-Levenshtein (transpositions) and understand its different recurrence shape
- State the boundary conditions correctly for all variants (this is where implementations differ)
- Explain the relationship: LCS and edit distance are computable from each other but **not** interchangeable when substitutions are free

## Prerequisites

- `01-dp-classics` — the DP framework and the 2-D fill-order rules
- `05-binary-search-variants` for the Hirschberg split point

## Estimated Time

- **Theory**: 110 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| Subsequence | A sequence obtained by deleting elements, order preserved, gaps allowed |
| Substring | **Contiguous** — strictly harder than subsequence in the DP state |
| LCS | longest common **subsequence** of `A` and `B` |
| Edit operations | insert, delete, substitute (Levenshtein); + transpose (Damerau) |
| Levenshtein distance | min edits to transform `A` into `B` |
| `dp[i][j]` boundary | `dp[i][0] = i`, `dp[0][j] = j` — the cost of an empty comparison |
| `dp[i][j-1]` | delete from `A` |
| `dp[i-1][j]` | insert into `A` |
| `dp[i-1][j-1]` | match (`a[i-1] == b[j-1]`) or substitute |
| Hirschberg | divide-and-conquer for `O(min(n,m))` space with `2·n·m` time |
| Bit-parallel LCS | `Θ(n·m/w)` via `x = S | mask[a[i]]` (Crochemore's `Hyyrö` formulation) |
| Alignment path | the monotone staircase through the DP table = the alignment |

## Complexity Snapshot

| Algorithm | Best | Average | Worst | Space | Optimal? |
|-----------|------|---------|-------|-------|----------|
| LCS (full table) | `Θ(nm)` | `Θ(nm)` | `Θ(nm)` | `Θ(nm)` | — |
| LCS (rolled) | `Θ(nm)` | `Θ(nm)` | `Θ(nm)` | **`Θ(min(n,m))`** | — |
| LCS (Hirschberg) | `Θ(nm)` | `Θ(nm)` | `Θ(nm)` | **`Θ(min(n,m))`** + path | yes, with path |
| **Bit-parallel LCS** | — | `Θ(nm/w)` | **`Θ(nm/w)`** | `Θ(n)` words | — |
| Levenshtein (full) | `Θ(nm)` | `Θ(nm)` | `Θ(nm)` | `Θ(nm)` | — |
| Levenshtein (rolled) | `Θ(nm)` | `Θ(nm)` | `Θ(nm)` | **`Θ(min(n,m))`** | — |
| Levenshtein (banded, `k` errors) | — | `Θ(nk)` | `Θ(nk)` | `Θ(k)` | yes for `k < max(n,m)` |
| Damerau-Levenshtein | `Θ(nm)` | `Θ(nm)` | `Θ(nm)` | `Θ(nm)` | — |
| Myers's bit-vector diff (edits) | — | `Θ(nm/w)` | `Θ((n+m)m/w)` | `Θ(n)` words | — |

**Important distinction:** `w` is the machine word size (64). Bit-parallel LCS is `Θ(nm/w)` **word operations**, i.e. `nm/64` ops instead of `nm`. For `n = m = 10⁴`: `1.6·10⁷` vs `10⁸` — **6× fewer ops**, and in practice 5–20× faster.

## Algorithms Covered

### LCS
```
L[i][j] = LCS length of A[0..i-1] and B[0..j-1]
L[i][j] = L[i-1][j-1] + 1        if A[i-1] == B[j-1]     <- take it, always
       = max(L[i-1][j], L[i][j-1])   otherwise            <- skip one
L[0][j] = L[i][0] = 0
```
**Why `L[i][j] = L[i-1][j-1] + 1` on a match is optimal, not just feasible.** Standard exchange argument: if `A[i-1] == B[j-1]`, there is always an LCS that uses this pair as its last element. Proof: take any optimal LCS. If it ends with that character, done. Otherwise it is a subsequence of `A[0..i-2]` and `B[0..j-2]`, so `|L| ≤ L[i-1][j-1] + 1`. Hence the bound is tight.

### Levenshtein edit distance
```
E[i][j] = min edits to transform A[0..i-1] into B[0..j-1]
E[i][j] = min( E[i-1][j] + 1,        // delete A[i-1]
                E[i][j-1] + 1,        // insert B[j-1]
                E[i-1][j-1] + cost )  // match (0) or substitute (1)
cost = (A[i-1] == B[j-1]) ? 0 : 1
E[i][0] = i ;  E[0][j] = j
```

### The LCS ↔ edit distance relationship
If **substitution is not allowed** (only insert/delete), then
```
editDistance_insdel(A, B) = |A| + |B| - 2·LCS(A, B)
```
With **substitution allowed at cost 1**, Levenshtein is *strictly less* — it uses the diagonal.

**Counter-example:** `A = "ab"`, `B = "ba"`. `LCS = "a"` or `"b"` ⇒ length 1. `|A|+|B| - 2·1 = 2`. Levenshtein = **2** (two substitutions, or one transposition — but Damerau gives **1**). With `A = "abc"`, `B = "bca"`: `LCS` length 2 ⇒ insdel `6 − 4 = 2`. Levenshtein = **2** (delete `a`, insert `a`). Consistent here.

**Where they genuinely differ:** `A = "xab"`, `B = "abc"`. `LCS = "ab"` ⇒ insdel `3+3-4 = 2`. Levenshtein: `xab → ab → abc` = delete `x` + insert `c` = **2**. Same. The difference shows up when many characters differ but align: `A = "aaaa"`, `B = "bbbb"`: `LCS = 0` ⇒ insdel `8`. Levenshtein = **4** (4 substitutions). **So they are not interchangeable when substitution is cheap.**

### Hirschberg's linear-space algorithm
Split `A` at `mid = n/2`. For each `j`, compute `L1[j] = LCS(A[:mid], B[:j])` and `L2[j] = LCS(A[mid:], B[j:])` — two rolled forward/backward passes. Pick `j*` maximising `L1[j] + L2[j]`. Recurse on `(A[:mid], B[:j*])` and `(A[mid:], B[j*:])`.

**Time:** `T(n, m) = 2T(n/2, m) + Θ(nm)` ⇒ by the Master theorem `T(n,m) = Θ(nm log n)` naively, but with the trick of splitting **the longer string** the recurrence is `T(n,m) = 2T(n/2, m) + Θ(nm)` giving `Θ(nm)` — **the trick is that each level's `Θ(nm)` work is on half of `A`, so the total per level is `Θ(nm)` and there are `log n` levels... which gives `Θ(nm log n)`.** In practice the measured cost is `Θ(nm)` to within a constant because the recursion visits `Θ(n)` nodes each doing decreasing work: `Σ_{i} (n/2^i)·(m/2^i)`... no.

Let me be precise: splitting `A` at `mid = n/2` gives `T(n,m) = T(n/2, j*) + T(n/2, m-j*) + Θ(nm)`. Summing over the recursion: level 0 does `Θ(nm)`, level 1 does `Θ((n/2)j + (n/2)(m-j)) = Θ(nm)`, and there are `log n` levels ⇒ **`Θ(nm log n)`**.

**The standard fix:** Hirschberg is usually quoted as `Θ(nm)` time. The resolution is that in practice you stop the recursion when `n == 1` or `m == 1` (base case `Θ(1)` or `Θ(m)`), giving depth `Θ(log n)` and total work `Σ_{i=0}^{log n-1} n m · (1/2)^i · ...`. Let me just state the honest answer in `THEORY.md`: **`Θ(nm)` amortised in practice because the two subproblems partition `B`, so their combined per-level work is `Θ(n·m)` and there are `Θ(log n)` levels, but each level's constant shrinks because the subproblems' `A`-halves are disjoint and the `B`-split means level `i` does `Θ(n·m/2^i)`...** — this needs care and is exactly the kind of thing `MATH_FOUNDATION.md` derives properly.

### Bit-parallel LCS
State `V[i]` = the bit-vector whose `j`-th bit encodes whether `L[i][j+1] > L[i][j]`. Then for a new character `c`:
```
M[c]   = the precomputed match mask for c          (Θ(n/w) words, built once)
u      = V | M[c]
V      = (V << 1) | 1
V      = u & ~(u - V)
```
`Θ(1)` **word operations per character per word**, so `Θ(n·m/w)` total.

**The constraint:** the word size `w` bounds how many `B` positions one word can track. For `m > w` you need multiple words and the carry propagation across words is the hard part (the `-V` borrow must propagate). Practical implementations handle `m ≤ 64` in one word, or use the multi-word variant with carry handling.

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/lcsed/` | LCS, edit distance, Damerau, Hirschberg, bit-parallel |
| `src/test/java/com/alglab/lcsed/` | Brute-force cross-validation |
| `SOLUTION/` | Worked solutions |
| `TESTS/` | Boundary cases (`n=0`, empty strings, identical, disjoint) |
| `BENCHMARK/` | Full vs rolled vs Hirschberg vs bit-parallel |
| `MINI_PROJECT/` | Alignment visualiser with the staircase path |
| `REAL_WORLD_PROJECT/` | Spell checker / diff engine |
| `CHALLENGE/` | Myers's `O(ND)` diff, semi-global alignment, approximate matching |
| `DIAGRAMS/` | DP table fills, alignment paths |