# Theory — LCS & Edit Distance

These two problems look like separate algorithms and are not. Both are `Θ(n·m)` grid DPs on the same rectangle, and the difference between them is exactly which cells of the grid the transition is allowed to read. Understanding that gets you: Levenshtein, Damerau, LCS, semi-global alignment, banded alignment, Hirschberg, bit-parallel LCS, and Myers's diff.

---

## 1. The shared grid

For strings `A` (length `n`) and `B` (length `m`), build a table of size `(n+1) × (m+1)`. Rows index prefixes of `A`, columns index prefixes of `B`.

```
        B[j-1]
      j →  0   1   2   3   4
   i        A[0] A[1] A[2] A[3]
   0   ─────────────────────────────────
   0        0   1   2   3   4
   1  A[0]  ...
   2  A[1]
   3  A[2]
   4  A[3]
```

**The boundaries are the first decision.** For LCS: `L[0][j] = L[i][0] = 0` (an empty string shares nothing). For edit distance: `E[0][j] = j` and `E[i][0] = i` (you must insert/delete everything).

Getting the boundary wrong is the most common LCS/Levenshtein bug and produces answers that are off by a constant — visible only at small sizes.

---

## 2. LCS

### State

> `L[i][j]` = the length of the longest common subsequence of `A[0..i-1]` and `B[0..j-1]`.

The definition must mention **subsequence**, not substring, and must specify the **half-open** prefix convention. Both details are load-bearing: writing `A[1..i]` (1-based) and then indexing `a[i-1]` is a bug generator.

### Transition

```
                   ⎧ L[i-1][j-1] + 1          if A[i-1] == B[j-1]
   L[i][j]  =       ⎨
                   ⎩ max(L[i-1][j], L[i][j-1])  otherwise
```

### Why the match case is *optimal*, not merely feasible

This is the crux and it is usually skipped.

**Claim.** If `A[i-1] == B[j-1]`, then `L[i][j] = L[i-1][j-1] + 1`.

**Proof.** (≥) Feasibility: take an LCS of `A[0..i-2]` and `B[0..j-2]` and append `A[i-1]`. It is a common subsequence of the longer prefixes, so `L[i][j] ≥ L[i-1][j-1] + 1`.

(≤) Let `S` be an LCS of `A[0..i-1]` and `B[0..j-1]`, with `|S| = L[i][j]`.
- If `S` uses `A[i-1]` and `B[j-1]` (i.e. its last element is that character), then `|S| = |S'| + 1` where `S'` is a common subsequence of `A[0..i-2]` and `B[0..j-2]`, so `|S| ≤ L[i-1][j-1] + 1`.
- If `S` does **not** use `A[i-1]`, then `S` is a common subsequence of `A[0..i-2]` and `B[0..j-1]`, so `|S| ≤ L[i-1][j] ≤ L[i-1][j-1] + 1` (the second inequality because appending one more character of `A` can increase the LCS by at most 1). Symmetrically if it does not use `B[j-1]`.

Either way `|S| ≤ L[i-1][j-1] + 1`. ∎

**The consequence that matters:** you never take `max(L[i-1][j], L[i][j-1])` on a match. Greedily taking the diagonal is *provably optimal*, not a shortcut.

### Backtracking and the alignment path

Walk backwards from `L[n][m]`:

```
while i > 0 and j > 0:
    if A[i-1] == B[j-1]:   emit MATCH; i--; j--
    else if L[i-1][j] >= L[i][j-1]: emit DELETE_A; i--
    else:                              emit INSERT_B; j--
```

The emitted path is a monotone staircase from `(n, m)` to `(0, 0)`, and it *is* the alignment. Note the tie-break `L[i-1][j] >= L[i][j-1]` — the other choice is equally optimal but gives a different (equally long) alignment, which matters if you are diffing and want stability.

### LCS is not a substring problem

| | State | Complexity |
|---|---|---|
| LCS | prefixes of both | `Θ(nm)` |
| Longest common **substring** | **contiguous** runs in both | `Θ(nm)` too, but with a different transition: |

```
S[i][j] = (A[i-1]==B[j-1]) ? S[i-1][j-1] + 1 : 0
answer  = max over i,j of S[i][j]
```

The `else 0` (instead of a `max`) is what makes it *substring* rather than subsequence. Same grid, one-character transition difference.

---

## 3. Levenshtein edit distance

### State

> `E[i][j]` = the minimum number of single-character operations needed to transform `A[0..i-1]` into `B[0..j-1]`.

### Transition

```
   E[i][j]  =  min(  E[i-1][j]   + 1,                // delete A[i-1]
                     E[i][j-1]   + 1,                // insert B[j-1]
                     E[i-1][j-1] + cost(i,j) )       // match or substitute

   cost(i,j) = 0 if A[i-1] == B[j-1] else 1
   E[0][j] = j ;  E[i][0] = i
```

**Why the three cases are exhaustive.** Take an optimal edit sequence. Its last operation either (a) deletes `A[i-1]`, leaving a transformation of `A[0..i-2]` to `B[0..j-1]`; (b) inserts `B[j-1]` last, leaving `A[0..i-1]` to `B[0..j-2]`; or (c) it is neither, in which case the last operation acts on both `A[i-1]` and `B[j-1]` — a match (cost 0) or substitution (cost 1). These are the only ways an alignment can end.

### The `min` and ties

Unlike LCS, Levenshtein **always** takes the `min` of three cells, even on an exact match (`cost = 0`). And on a match, `E[i-1][j-1]` is always ≤ the other two, so the `min` is redundant but harmless. Do **not** "optimise" it to a conditional — the Damerau variant needs the full `min`.

---

## 4. The relationship between LCS and Levenshtein

### Insert/delete-only distance

If you forbid substitution (only insert and delete, each cost 1), then:

```
d_insdel(A, B)  =  |A| + |B| - 2 · LCS(A, B)
```

**Proof sketch.** Any common subsequence of length `L` can be preserved: delete the `|A| - L` non-matching characters of `A` and insert the `|B| - L` non-matching characters of `B`. Conversely, an insert/delete-only script preserves some subsequence of common elements (the ones never deleted), which is a common subsequence of length `≤ LCS`. So the minimum is exactly `|A| + |B| - 2L`.

### When substitution is cheap they are **not** interchangeable

| `A` | `B` | LCS | insdel dist | Levenshtein |
|-----|-----|-----|-------------|-------------|
| `aaaa` | `bbbb` | 0 | `8` | **`4`** (4 substitutions) |
| `ab` | `ba` | 1 | `2` | **`2`** |
| `xab` | `abc` | 2 | `2` | `2` |
| `abc` | `bca` | 2 | `2` | `2` |

The first row is the discriminator: with 100% substitutions, Levenshtein halves the distance. **If your metric treats a substitution as cheap, using `|A|+|B|-2·LCS` is wrong by a factor of 2 in the worst case.**

**Deduplication insight:** many implementations compute `LCS` and derive the distance, because LCS is easier to bit-parallel (bit-parallel Levenshtein needs `Θ(m)` bits plus carries, which is more complex). So `editDistance = |A| + |B| - 2·LCS` is the right formula *for the insdel metric*, and it is a common source of subtle bugs when the requirement is actually Levenshtein.

---

## 5. Damerau-Levenshtein (with transpositions)

### The recurrence

```
                        ⎧ D[i-2][j-2] + 1                     if A[i-1] == B[j-2] and A[i-2] == B[j-1]
                        ⎪
   D[i][j]  =  min(     ⎨ D[i-1][j] + 1
                        ⎪ D[i][j-1] + 1
                        ⎪
                        ⎩ D[i-1][j-1] + cost(i,j)
```

The new term is the **transpose**: two adjacent characters swapped costs 1 instead of 2 substitutions.

**`A = "ca"`, `B = "ac"`:** `D[2][2] = D[0][0] + 1 = 1` via the transpose term. Levenshtein gives 2. **That is the whole value of Damerau.**

### The subtlety: the transpose window is `(i-2, j-2)`

So Damerau needs the **two previous rows**, not one. A `Θ(min(n,m))` rolled implementation must keep two rows and be careful about the `i-2, j-2` read.

### Unrestricted Damerau vs Optimal String Alignment

There are **two** different Damerau variants and they are not the same:

| Variant | Allow | Recurrence |
|---------|-------|-----------|
| **OSA** (Optimal String Alignment) | each substring edited at most once | the 4-term recurrence above; easy, `Θ(nm)` space rolled to 2 rows |
| **True Damerau-Levenshtein** | unrestricted edits | requires tracking the last row/column where each character was seen; the space-rolled form needs `Θ(nm)` space again unless you use Lowrance–Wagner's `Θ(nm)` with `O(m)` space via the "last matched row/column" arrays |

**This is a genuine trap:** the popular LeetCode "Edit Distance II"/"Minimum Number of Steps to Make Two Strings Equal" (712) is **OSA**, and implementations that call it Damerau-Levenshtein are naming the wrong algorithm. OSA gives a metric but **not a triangle inequality on all strings** (it is not a true metric; the unrestricted version is).

### Why OSA is not a metric

Classic counter-example: `A = "CA"`, `B = "AC"`, `C = "ABC"`.
- `OSA("CA","AC") = 1`
- `OSA("AC","ABC") = 1`
- `OSA("CA","ABC") = 2` — equal to the sum, so triangle inequality *holds* here.
- The real failure: `A = "CA"`, `B = "AB"`, `C = "AC"`: `OSA(CA,AC)=1`, `OSA(AC,AB)=1`, `OSA(CA,AB)=3 > 2`. **Triangle inequality violated.** This is why "edit distance" algorithms need to state which variant they implement before being used with anything that assumes metric properties (BK-trees, dedup thresholds).

---

## 6. Space optimisation: rolled rows

### LCS, rolled to `Θ(min(n,m))`

```
L[i][j] = L[i-1][j-1] + 1                      if A[i-1] == B[j-1]
        = max(L[i-1][j], L[i][j-1])           otherwise
```

Reads: `L[i-1][j-1]` (diagonal), `L[i-1][j]` (the cell being overwritten), `L[i][j-1]` (already updated in this row). So **one row plus one saved diagonal** suffices:

```java
int[] dp = new int[m + 1];
for (int i = 0; i <= m; i++) dp[i] = i;          // row 0 boundary: L[0][j] = 0, so just zeros
for (int i = 1; i <= n; i++) {
    int diagonal = 0;                             // L[i-1][0]
    int prevLeft = dp[0];                         // L[i-1][0] -- for LCS, L[i][0] = 0 always
    dp[0] = 0;
    for (int j = 1; j <= m; j++) {
        int up = dp[j];                            // L[i-1][j]
        if (a[i-1] == b[j-1]) dp[j] = diagonal + 1;
        else dp[j] = Math.max(dp[j], dp[j-1]);     // L[i-1][j] vs L[i][j-1]
        diagonal = up;
    }
}
```

**Always put the shorter string on the column axis.** If `m > n`, the row array is `Θ(m)`; swapping so `m = min` gives `Θ(min(n,m))`. This is a two-line change worth a factor of `n/m` in memory.

### Edit distance, rolled

```
E[i][j] = min(E[i-1][j]+1, E[i][j-1]+1, E[i-1][j-1]+cost)
```

Same three reads, same diagonal save. **But the boundary is non-zero:** `E[i][0] = i`, so `dp[0]` must be set to `i` at the start of each row (unlike LCS where `dp[0] = 0` forever). Forgetting this makes `E(n, m) = LCS`-flavoured and wrong in an obvious way (distance 0 between `"abc"` and `""`).

### Can you roll *and* reconstruct?

**No.** Backtracking needs the whole table. This is the motivation for Hirschberg.

---

## 7. Hirschberg's linear-space algorithm

### The divide

Split `A` at `mid = n/2`:

```
A = A1 · A2      with |A1| = ⌊n/2⌋
```

Any common subsequence splits into a common subsequence of `A1` with some prefix of `B`, and a common subsequence of `A2` with the remaining suffix of `B`.

Let `j` range over `0..m`:
- `fwd[j]` = `LCS(A1, B[0..j-1])` — a **forward** rolled LCS pass.
- `bwd[j]` = `LCS(A2, B[j..m-1])` — the same run on reversed strings.

Then

```
LCS(A, B)  =  max over j of  fwd[j] + bwd[j]
```

and `j*` attaining the max is the split point for `B`.

### Correctness

**Claim.** There is an optimal LCS that splits at `j*`.

Let `S` be an LCS of `A` and `B`, of length `L`. Since `S` uses `A1` before `A2` and `B` in order, there is a `j` such that `S = S1 · S2` with `S1` a common subsequence of `A1` and `B[0..j-1]`, and `S2` of `A2` and `B[j..m-1]`. Hence `L ≤ fwd[j] + bwd[j] ≤ max_j (fwd[j] + bwd[j])`.

Conversely, for any `j`, `fwd[j] + bwd[j]` is achievable by concatenating an optimal `S1` and `S2`. So `LCS(A,B) = max_j (fwd[j] + bwd[j])`. ∎

Note the recurrence only uses `fwd[⌊n/2⌋]` and `bwd[⌈n/2⌉]`, so **recursing on `(A1, B[0..j*-1])` and `(A2, B[j*..m-1])` is valid.**

### Complexity, carefully

```
T(n, m)  =  T(⌊n/2⌋, j*)  +  T(⌈n/2⌉, m - j*)  +  Θ(n·m)
```

**Total time.** Let `D` be the recursion depth. The subproblems at each level have **disjoint `A`-halves summing to `n`** and **disjoint `B`-ranges summing to `m`**. The work at a level is `Σ over subproblems of |A_sub| · |B_sub| ≤ (Σ|A_sub|) · (max |B_sub|) ≤ n · m`. With `D = Θ(log n)` levels:

```
Total  =  Θ(n m log n)
```

**But:** the `Θ(n·m)` per-level figure is loose — at level `i` the number of subproblems is `2^i` and the average subproblem is `(n/2^i) × (m/2^i)`, so the level's work is `2^i · (n m / 4^i) = n m / 2^i`. Summing over levels: `Σ n m / 2^i = 2 n m`. **Total `Θ(nm)`.**

The distinction is that the recursion depth is `Θ(log n)` but the *work per level decays geometrically*, giving `Θ(nm)`. **`MATH_FOUNDATION.md` derives this properly — this is the one place students routinely get the bound wrong.**

### Space

`Θ(min(n,m))` for the two `fwd`/`bwd` arrays, plus `Θ(log n)` frames, plus `Θ(n)` for the output. Compare with `Θ(nm)` for the full table.

**When Hirschberg is worth it:** `n·m > available memory`. For `n = m = 10⁵`, the full table is `10¹⁰` ints = **40 GB** (hopeless); Hirschberg needs `10⁵` ints = 400 KB plus `Θ(n)` output. **This is the only way to solve that instance exactly in Java.**

---

## 8. Bit-parallel LCS

### The idea

Represent an entire **row** of the DP table as a bit vector `V` of `m` bits, where bit `j` of `V` is set iff `L[i][j+1] > L[i][j]` — i.e. iff the LCS length increases between column `j` and `j+1`.

Because `L[i][j+1] - L[i][j] ∈ {0, 1}`, the row is *completely* determined by `m+1` bits instead of `(m+1)` ints. **A 64× compression.**

### The transition

Precompute, for each distinct character `c` of `B`, a mask `M[c]` whose `j`-th bit is set iff `B[j] == c`.

Then processing `A[i]`:

```
u = V | M[A[i]]                 // positions that would extend
V = (V << 1) | 1                // shift in the "boundary" bit
V = u & ~(u - V)                // the magic: subtraction propagates borrows
```

`Θ(1)` word operations per character, so the whole LCS is `Θ(n · m/w)`.

### Why `u & ~(u - V)` works

The `V << 1 | 1` encodes "the previous row's breakpoints shifted right, plus a new breakpoint at position 0". The subtraction `u - V` propagates a borrow chain through the positions between breakpoints, and `u & ~(...)` selects exactly the first `u`-bit at or after each shifted breakpoint. **That is: the new breakpoints of the row are, for each old breakpoint, the first `match` position at or after it** — which is precisely the LCS recurrence in disguise.

This is the **Crochemore/Hyyrö** formulation (used in GNU `libstring`, Rust's `packed-simd`, and `bio` crates). It is 10–50× faster than the scalar DP for long strings.

### The `m ≤ w` constraint and the multi-word variant

One word holds `m` bits, so this is directly applicable when `m ≤ 64`. For longer `B`:

- **Chunked**: process `B` in 64-character blocks, but the `borrow` out of one block must be fed into the next (and the initial `V << 1 | 1` boundary only for the first block). Implementable and correct, `Θ(n·m/64)` plus `Θ(n)` per-word overhead.
- **Full multi-word**: maintain `m/64` words and do the borrow propagation explicitly. Same complexity, more code.

**Practical state of the art:** bit-parallel LCS is a real production technique (Blast, agrep, `diff` for long lines, bio-alignment libraries) but it is niche in Java because `Long.reverseBytes`-style bit tricks still cost real cycles and the JIT will not vectorise them.

### Bit-parallel Levenshtein and Myers's diff

Levenshtein can also be bit-parallel, but the borrow chain is more delicate (P **e** **x** **t** and PDEP-style operations; no clean `u & ~(u-V)`). The standard alternative is:

- **Myers's `O(ND)` diff algorithm**: computes the edit script in `O((n+m)·D)` where `D` is the edit distance. **When `D` is small (the case you care about for diffs), this beats `Θ(nm)` by orders of magnitude.** `Θ((n+m)·D)` for `D = 5` vs `Θ(nm)` for `n = m = 10⁶` is `10⁷` vs `10¹²`.
- Myers's **bit-vector variant** computes it in `Θ(m/w)` per `D` step.

**This is the algorithm real diff tools use** — GNU `diff` uses a related idea, `git diff` uses Myers with heuristics, and the "diff is quadratic in the worst case" complaint is about the *fallback*, not the common case.

---

## 9. Variants worth knowing

| Variant | What changes | Use |
|---------|--------------|-----|
| **Semi-global / overlap** | `E[i][0] = 0` and `E[n][j] = 0` — free gaps at the ends | aligning a short read inside a long reference (bioinformatics) |
| **Needleman–Wunsch** | global alignment, substitution matrix (scores, not distances) | sequence alignment with biological scoring |
| **Smith–Waterman** | local alignment, `max(0, …)` reset | local alignment, `Θ(nm)`, Smith-Waterman with affine gaps in bioinformatics |
| **Affine gaps** | extra states `E`, `F` for gap-open vs gap-extend | realistic alignment scoring; `Θ(3nm)` |
| **Banded** | only compute cells with `|i-j| ≤ k` | `Θ(nk)` when the answer is known to be `< k` — used in approximate string matching (k-mismatch) |
| **Bit-parallel approximate matching** | `Θ(nm/w)` for all patterns of a fixed length | `glgrep`, `grep -F` with many patterns |
| **Myers's `O(ND)`** | `D` = edit distance | diffs of similar files |
| **LCS on a suffix automaton** | `Θ(n + m)` | when you need many LCS queries against one string |

**The most practically important insight:** the "one `Θ(nm)` DP" framing hides that `Θ(nm)` is only correct when you need the *whole* answer. Semi-global, banded, and Myers's variants are all much faster in their intended regimes, and **knowing which regime you are in is worth more than optimising the `Θ(nm)`**.

---

## 10. Choosing

| Situation | Use |
|-----------|-----|
| One LCS, `n·m` fits in memory | rolled `Θ(min(n,m))`-space DP |
| One LCS, `n·m` does not fit | **Hirschberg** |
| `m ≤ 64`, one LCS, performance-critical | **bit-parallel** |
| Edit distance, want the operations | Levenshtein with a `choice[]` array, or backtrack the table |
| Diff of two similar files | **Myers's `O(ND)`** |
| Transpositions count as 1 | **OSA / Damerau** — and say which |
| Short pattern inside a long text | **semi-global** or **banded** |
| Alignment with biological scores | Needleman–Wunsch / Smith–Waterman |
| Many LCS queries against one string | build a **suffix automaton** (`Θ(n)`) and answer each in `Θ(m)` |
| Real Java, one-off | `String` methods do not exist for these — implement them, or use Apache Commons Text's `LevenshteinDistance` |

**The honest production answer:** Apache Commons Text / `java-string-similarity` for one-offs, your own Myers or banded implementation for large similar inputs, bit-parallel for long-line diffs, and `Θ(nm)` rolled DP for everything else. The `Θ(nm)` DP is the reference implementation every other algorithm in this lab is validated against — write it first, always.