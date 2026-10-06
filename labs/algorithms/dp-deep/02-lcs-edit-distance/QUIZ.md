# Quiz — LCS & Edit Distance

15 questions. Each key gives the reason.

---

## Q1
Prove that `L[i][j] = L[i-1][j-1] + 1` when `A[i-1] == B[j-1]` is optimal, not merely feasible.

<details><summary>Answer</summary>

(≥) Feasible: append `A[i-1]` to an LCS of `A[0..i-2]`, `B[0..j-2]`.

(≤) Let `S` be any LCS of the longer prefixes, `|S| = L[i][j]`.
- If `S` ends with the shared character, `|S| = |S'| + 1 ≤ L[i-1][j-1] + 1`.
- If `S` does not use `A[i-1]`, then `|S| ≤ L[i-1][j] ≤ L[i-1][j-1] + 1` (one more character of `A` raises the LCS by at most 1). Symmetric for `B[j-1]`.

Hence `L[i][j] = L[i-1][j-1] + 1`. **The consequence: you never take `max` on a match, and the greedy diagonal is provably optimal.**
</details>

## Q2
The three boundary conditions. Get any one wrong and say what happens.

<details><summary>Answer</summary>

| | LCS | Levenshtein |
|---|---|---|
| row 0 | `L[0][j] = 0` | `E[0][j] = j` |
| col 0 | `L[i][0] = 0` | `E[i][0] = i` |

- LCS with a non-zero boundary counts "characters matched against nothing" — absurd.
- Levenshtein with a zero boundary makes `editDistance("abc","") == 0`, i.e. the empty string is free to transform from anything. This is the bug that turns Levenshtein into the insert/delete-only metric.
</details>

## Q3
State the rolled-DP invariant and why the `diagonal` save is required.

<details><summary>Answer</summary>

Before updating `dp[j]` in row `i`: `dp[j] = L[i-1][j]`, `dp[j-1] = L[i][j-1]`, `diagonal = L[i-1][j-1]`.

After `dp[j] = …`, the old `dp[j]` is overwritten, so `L[i-1][j-1]` is destroyed. **The `diagonal` local saves it before the write**, and becomes the next iteration's diagonal.

Symptom of omission: **the first row is always correct** (there `dp[0]` is the boundary, so nothing is lost), everything after is wrong. A test suite checking only small `n` can miss it.
</details>

## Q4
When is `|A| + |B| - 2·LCS(A,B)` equal to the Levenshtein distance? Give a counter-example.

<details><summary>Answer</summary>

Equal **iff** some optimal script uses no substitution — i.e. iff the optimal alignment contains no diagonal move with cost 1.

**Counter-example:** `A = "aaaa"`, `B = "bbbb"`. `LCS = 0`, so the formula gives `4 + 4 - 0 = 8`. Levenshtein is `4` (four substitutions). **The formula over-estimates by 2×** in the fully-disjoint case.

This matters: if your metric treats substitution as cheap, computing `LCS` and deriving the distance is wrong by a factor of up to 2.
</details>

## Q5
Damerau vs OSA. Which one is a metric, and give a triple that breaks the other.

<details><summary>Answer</summary>

- **Unrestricted Damerau-Levenshtein** is a metric (satisfies the triangle inequality).
- **OSA (Optimal String Alignment)** is **not**.

Witness: `osa("CA","AC") = 1`, `osa("AC","AB") = 1`, but `osa("CA","AB") = 3 > 2`. Triangle inequality violated.

**Consequence:** BK-trees, approximate dedup thresholds, and nearest-neighbour search over OSA distances return **wrong answers**. Use true Levenshtein or unrestricted Damerau.
</details>

## Q6
The transpose term reads `(i-2, j-2)`. What does that imply for space optimisation?

<details><summary>Answer</summary>

The Damerau/OSA recurrence cannot roll to **one** row — it needs the row from two steps back.

Two rows suffice (`prevPrev`, `prev`, `cur` rotated). The single-row version silently reads stale values and produces wrong answers only when a transposition is available, which is exactly when you did not test.
</details>

## Q7
Hirschberg: state the split rule, prove it, and give the space bound.

<details><summary>Answer</summary>

Split `A` at `mid = n/2`. Compute `fwd[j] = LCS(A1, B[0..j))` (forward roll) and `bwd[j] = LCS(A2, B[j..m))` (backward roll). Then

```
LCS(A,B) = max_j ( fwd[j] + bwd[j] )
```

**Proof:** any common subsequence splits at some `j` into `S1` over `(A1, B[0..j))` and `S2` over `(A2, B[j..m))`, so its length `≤ fwd[j] + bwd[j]`; and any `fwd[j] + bwd[j]` is achievable by concatenation. ∎

**Space:** `Θ(min(n,m))` for `fwd`/`bwd` plus `Θ(log n)` frames.
</details>

## Q8
Hirschberg's time bound. Why is `Θ(nm log n)` quoted as `Θ(nm)` — and when is each true?

<details><summary>Answer</summary>

Splitting only `A`: level `i` does `Σ_j |A_ij| · |B_ij| ≤ n · m`, and there are `Θ(log n)` levels ⇒ **`Θ(nm log n)`**.

Splitting the **longer** string alternately: level `i` has `2^i` subproblems of size `(n/2^i) × (m/2^i)`, so the level's work is `nm/2^i` and the total is `Σ nm/2^i = **Θ(nm)**`. ∎

**In practice:** the `log n` factor is 2–5× on real inputs and the memory win (40 GB → 400 KB) is what matters. Implement the fast version anyway — it is two lines of `if (a.length >= b.length)`.
</details>

## Q9
Bit-parallel LCS: state the recurrence and explain what `u & ~(u - V)` exploits.

<details><summary>Answer</summary>

```
u = V | M[c]
V = (V << 1) | 1
V = u & ~(u - V)
```

`(V << 1) | 1` gives the shifted breakpoints of the previous row plus a new breakpoint at position 0. `u` marks all candidate positions (old breakpoints ∪ matches for `c`). **`u - V` propagates a borrow from each shifted breakpoint through the `u`-bits, stopping at the first `u`-bit** — and `u & ~(...)` selects exactly those. That is the recurrence "the new breakpoint of each old breakpoint is the first match at or after it", executed in `Θ(1)` word ops because **64-bit subtractors propagate borrows in parallel within a word**.

It is a hardware property, not an algorithmic one.
</details>

## Q10
Bit-parallel LCS is `Θ(nm/w)`. What are the three things that stop it from being arbitrarily better?

<details><summary>Answer</summary>

1. **Mask construction**: `Θ(|Σ_B| · m/w)` per distinct `B`. For `|Σ_B| = 256` and `m = 10⁶` that is **16 MB of masks** — more than the rolled DP's 4 MB.
2. **`m > w` borrow propagation across words is not free.** The bit-by-bit carry loop is `Θ(64)` per word, throwing away most of the speedup. Practical implementations cap at `m ≤ 64`.
3. **Alphabet size.** Indexing masks by `char` needs 65 536 entries = 512 KB. Compress the alphabet first.

So bit-parallel wins on **time** and loses on **space** for large alphabets — which is why it lives in `diff` (alphabet ≤ 256, short chunks) and not in bioinformatics alignment.
</details>

## Q11
Myers's `O(ND)`: state the bound, the space, and when it *loses*.

<details><summary>Answer</summary>

`Θ((n+m)·D)` time, `Θ(D)` space, where `D` is the edit distance. Tight (Myers 1986).

**It loses when `D` is large:** `Θ((n+m)D) > Θ(nm)` iff `D > nm/(n+m) ≈ min(n,m)/2`. For random strings of equal length, `D ≈ n`, so Myers is ~2× *worse* than the quadratic DP.

| `n = m = 10⁶` | `Θ(nm)` | Myers | speedup |
|---|---|---|---|
| `D = 100` | `10¹²` | `2·10⁸` | **5000×** |
| `D = 10⁵` | `10¹²` | `2·10¹¹` | 5× |
| `D = 10⁶` | `10¹²` | `2·10¹²` | **0.5×** |

**Production answer:** strip the common prefix/suffix, cap `D`, and fall back to `Θ(nm)` when the cap is hit. That hybrid is what `git diff` and GNU `diff` do.
</details>

## Q12
Banded (Ukkonen) alignment: the time/space and the correctness argument.

<details><summary>Answer</summary>

**Claim:** `E[i][j] ≤ k ⟹ |i − j| ≤ k`. Each edit changes `i − j` by at most 1, so a cell whose index difference exceeds `k` needs more than `k` edits to reach.

Therefore only the band `|i − j| ≤ k` can matter: **`Θ(nk)` time, `Θ(k)` space** (two diagonals' worth of cells).

This is the algorithm behind `grep -F -f patterns`, Ukkonen's `k`-mismatch problem, and every approximate string matcher. Combined with bit-parallelism it becomes `Θ(nm/w)` for all patterns of one length.
</details>

## Q13
LCS is `Θ(nm)`. Is that optimal? Under what promise can you beat it?

<details><summary>Answer</summary>

**Yes, `Ω(nm)` in the worst case** — an adversary can construct `A, B` such that every cell of the grid is independently determinable only by inspecting it, so any algorithm must inspect `Θ(nm)` cells.

**Sub-quadratic requires a promise:**
- Edit distance `≤ k` ⇒ band ⇒ `Θ(nk)`.
- Similar inputs (`D` small) ⇒ Myers ⇒ `Θ((n+m)D)`.
- `B` short (`≤ w`) ⇒ bit-parallel ⇒ `Θ(nm/w)`.

All three are the same idea: **add a parameter and pay in that parameter instead of in `n·m`.**
</details>

## Q14
Semi-global alignment. What changes and what is it for?

<details><summary>Answer</summary>

Free gaps at the ends: `E[i][0] = 0` for all `i`, and `E[n][j] = 0` for all `j`. The answer is `min_j E[n][j]`.

**For:** aligning a short read against a long reference — genome mapping, log-line pattern search, motif finding. You want the best place to put the short string inside the long one, not the cost of forcing both ends to align.

**Time is still `Θ(nm)`,** but only the band near the diagonal is ever interesting, so it is usually implemented with the banded machinery and runs in `Θ(nm)` with `Θ(m)` space and far better cache behaviour.
</details>

## Q15
You need the LCS of `n = m = 10⁵` strings, plus the actual subsequence. What do you build, and why not the alternatives?

<details><summary>Answer</summary>

**Hirschberg (the `Θ(nm)` version)**: `Θ(min(n,m)) = 400 KB` of scratch plus the `Θ(n)` output.

| alternative | verdict |
|---|---|
| Full table | `10¹⁰` ints = **40 GB** — impossible |
| Rolled DP | right answer, wrong question: **no reconstruction** |
| Bit-parallel | time is fine (`Θ(nm/64)`) but gives only the length; masks need `256 × 1563 × 8 = 3.2 MB` and there is **no backtracking path** |
| Myers | solves edit scripts, not LCS; and `Θ((n+m)D)` needs `D` known small |

**General rule: if you need the *plan*, you need `Θ(n)` of memory, and Hirschberg is the only algorithm here that gives it in `Θ(min(n,m))` working space.**
</details>