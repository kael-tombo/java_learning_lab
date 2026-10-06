# Flashcards — LCS & Edit Distance

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | LCS state | `L[i][j]` = LCS length of `A[0..i-1]` and `B[0..j-1]` (half-open prefixes) |
| 2 | LCS transition | `L[i-1][j-1]+1` on a match; `max(L[i-1][j], L[i][j-1])` otherwise |
| 3 | LCS boundary | `L[0][j] = L[i][0] = 0` |
| 4 | Why the diagonal is optimal on a match | Exchange argument: any LCS is `≤ L[i-1][j-1]+1` because one extra character adds at most 1 |
| 5 | LCS complexity | `Θ(nm)` time, `Θ(nm)` space |
| 6 | Levenshtein transition | `min(E[i-1][j]+1, E[i][j-1]+1, E[i-1][j-1]+cost)` |
| 7 | Levenshtein boundary | `E[0][j] = j`, `E[i][0] = i` — **non-zero** |
| 8 | The three Levenshtein cases | delete, insert, match/substitute — they exhaust how an alignment can end |
| 9 | Levenshtein always takes `min` | yes, even on a match (`cost = 0`) — the Damerau variant needs it |
| 10 | Rolling `diagonal` save | required or `dp[i-1][j-1]` is destroyed; the first row stays correct, the rest breaks |
| 11 | Put the shorter string on | the column axis ⇒ `Θ(min(n,m))` space |
| 12 | `LCS → insert/delete-only distance` | `\|A\| + \|B\| − 2·LCS` |
| 13 | When that equals Levenshtein | iff an optimal script uses no substitution |
| 14 | Counter-example | `"aaaa"` vs `"bbbb"`: formula `8`, Levenshtein `4` |
| 15 | LCS vs substring DP | `else 0` instead of a `max`; answer is `max` over cells, not the corner |
| 16 | LCS vs prefix | only `dp[i][i]` is meaningful |
| 17 | Damerau (OSA) extra term | `D[i-2][j-2] + 1` when `A[i-1]==B[j-2]` and `A[i-2]==B[j-1]` |
| 18 | Damerau's space requirement | **two** previous rows (the transpose reads `i-2`) |
| 19 | OSA vs unrestricted Damerau | OSA edits each substring at most once; they give **different** answers |
| 20 | Is OSA a metric? | **No** — `"CA","AB","AC"`: `3 > 1 + 1` |
| 21 | Consequence of OSA not being a metric | BK-trees / dedup thresholds over OSA distances return **wrong** answers |
| 22 | Hirschberg split rule | `LCS(A,B) = max_j ( fwd[j] + bwd[j] )`, recurse on `(A1, B[0,j))` and `(A2, B[j,m))` |
| 23 | Hirschberg space | `Θ(min(n,m))` |
| 24 | Hirschberg time — split `A` only | `Θ(nm log n)` |
| 25 | Hirschberg time — split the longer | **`Θ(nm)`** (level `i` work decays as `nm/2^i`) |
| 26 | Row compression | `L[i][j+1] − L[i][j] ∈ {0,1}` ⇒ a row is `m+1` **bits**, a **32×** saving |
| 27 | Bit-parallel LCS | `u = V\|M[c]; V = (V<<1)\|1; V = u & ~(u − V)` |
| 28 | What `u & ~(u−V)` exploits | **parallel borrow propagation** inside a 64-bit subtractor |
| 29 | Bit-parallel LCS complexity | **`Θ(n·m/w)`** word operations, `w = 64` |
| 30 | Bit-parallel mask cost | `Θ(\|Σ_B\| · m/w)` per distinct `B` — `256` chars × `m/8` bytes of memory |
| 31 | Bit-parallel practical limit | `m ≤ 64` per word; multi-word borrow is fiddly and slow |
| 32 | Levenshtein row compression | `E[i][j+1] − E[i][j] ∈ {−1, 0, 1}` — needs **two** bit vectors, so bit-parallel is harder |
| 33 | Myers `O(ND)` time / space | `Θ((n+m)·D)` / `Θ(D)` |
| 34 | Myers's state | the **diagonal** `k = i − j`, plus the "snake" of matches |
| 35 | Myers's weakness | loses when `D > min(n,m)/2`; random strings are `D ≈ n` ⇒ **worse than `Θ(nm)`** |
| 36 | Production diff shape | strip common prefix/suffix, cap `D`, fall back to `Θ(nm)` |
| 37 | Banded (Ukkonen) | `Θ(nk)` time, `Θ(k)` space when the answer is `≤ k` |
| 38 | Banded correctness | `E[i][j] ≤ k ⟹ \|i−j\| ≤ k` — each edit shifts `i−j` by ≤ 1 |
| 39 | Semi-global alignment | `E[i][0] = E[n][j] = 0` — free end gaps; short read in a long reference |
| 40 | Affine gaps | extra `E`/`F` states, `Θ(3nm)` |
| 41 | Needleman–Wunsch / Smith–Waterman | scoring matrices: global / local alignment |
| 42 | LCS against one suffix automaton | `Θ(\|A\|)` build + `Θ(\|B\|)` per query |
| 43 | LCS lower bound | `Ω(nm)` — adversary on independent grid cells |
| 44 | Sub-quadratic requires a promise | `D` small (banding/Myers) or `m ≤ w` (bit-parallel) |
| 45 | Hidden parameter selecting the algorithm | **`D/n`** — the edit distance relative to the length |
| 46 | Roll the longer or shorter onto rows | shorter ⇒ `Θ(min(n,m))` memory |
| 47 | LCS backtracking tie-break | `L[i-1][j] >= L[i][j-1]` ⇒ prefer delete; the other is equally optimal |
| 48 | LCS backtracking must take the diagonal on a match | otherwise the emitted alignment can be shorter than `L[n][m]` |
| 49 | Bit-parallel `m = 64` hazard | `1L << 63` sets the sign bit; borrow semantics change — test 63 and 64 explicitly |
| 50 | Bit-parallel alphabet hazard | indexing by `char` needs 65 536 entries = 512 KB |
| 51 | `n = m = 10⁵` LCS with the subsequence | Hirschberg — 40 GB table is impossible, rolled cannot reconstruct |
| 52 | Validating every variant | fuzz against the `Θ(nm)` full-table DP, which is 20 lines |
| 53 | What the reference DP is for | it is the oracle; write it first, always |
| 54 | When bit-parallel LCS is the right tool | spell checkers, `diff` on long lines, `m ≤ 64` |
| 55 | Never use `\|A\|+\|B\|−2·LCS` for Levenshtein | unless substitution is genuinely forbidden |
| 56 | Never use OSA with a BK-tree | it is not a metric |
| 57 | Never roll Damerau to one row | the transpose needs `i-2` |
| 58 | Never rely on Hirschberg for speed | roll it (`Θ(nm log n)` → `Θ(nm)`) |
| 59 | Never skip the `diagonal` save | first row correct, everything after wrong |
| 60 | The order that works | reference DP → validate → then optimise |

## Self-test (one line each)

1. LCS complexity and its lower bound? → **`Θ(nm)`, tight — `Ω(nm)` by adversary**
2. Rolling LCS needs what besides one row? → **A `diagonal` local holding `dp[i-1][j-1]`**
3. Bit-parallel LCS transition? → **`u = V|M[c]; V = (V<<1)|1; V = u & ~(u−V)`**, exploiting **parallel borrow propagation**
4. Hirschberg's rule and space? → **`max_j (fwd[j] + bwd[j])`, `Θ(min(n,m))` space, `Θ(nm)` time only if you split the longer string**
5. When does `|A|+|B|−2·LCS` equal Levenshtein? → **Only when no optimal script uses a substitution** (`"aaaa"` vs `"bbbb"`: 8 vs 4)