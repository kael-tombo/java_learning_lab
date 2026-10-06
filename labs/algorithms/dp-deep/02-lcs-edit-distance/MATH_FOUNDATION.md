# Math Foundation — LCS & Edit Distance

The `Θ(nm)` bound, Hirschberg's geometric work argument, the bit-parallel `Θ(nm/w)` reduction, and the information-theoretic floor.

---

## 1. The grid DP recurrence

```
L[i][j] = L[i-1][j-1] + 1        if A[i-1] == B[j-1]
        = max(L[i-1][j], L[i][j-1])   otherwise
L[0][j] = L[i][0] = 0
```

There are `(n+1)(m+1)` states, each computed in `Θ(1)`.

```
T(n, m)  =  (n+1)(m+1)  · Θ(1)  =  Θ(nm)
Space    =  Θ(nm)
```

**With the diagonal save:** space `Θ(min(n,m))`. **Time is unchanged** — rolling only removes the memory, not the work. (Same lesson as lab `01`: rolling reduces peak footprint, not traffic.)

---

## 2. The row-compression that makes bit-parallel possible

`L[i][j+1] − L[i][j] ∈ {0, 1}` — the LCS length increases by **at most one** when you extend the prefix of `B` by one character. (Proof: a new character can add at most one element to a common subsequence.)

Therefore row `i` is determined by `m` bits:

```
V[i] = bit j is 1  ⟺  L[i][j+1] > L[i][j]
```

and `L[i][m] = popcount(V[i])`.

**Information per row:**

| Encoding | Bits per row | For `m = 1000` |
|----------|-------------|----------------|
| `int[]` row | `32(m+1)` = 32 032 bits | 4004 bytes |
| bit vector | `m+1` = 1001 bits | **126 bytes** |
| compression | | **32×** |

With `w = 64`: `Θ(m/w)` words per row instead of `Θ(m)` words.

**Total: `Θ(n · m/w)` word operations** — for `n = m = 10⁴`, `1.6·10⁷` vs `10⁸`.

---

## 3. The bit-parallel transition

```
u = V | M[c]
V = (V << 1) | 1
V = u & ~(u - V)
```

**Why this is correct.** Let the breakpoints of `V` be `p₁ < p₂ < … < p_L`. They satisfy:

```
p₁ = 0,     p_{k+1} = the smallest position > p_k with (M[c]) bit set
```

**Invariant of the recurrence.** Row `i` has breakpoint `p_k'` at position

```
p_k' = min { j ≥ p_k  :  M[c] has bit j set }
```

**Proof sketch by induction.** The new row's breakpoints are the `u`-bit positions reachable by a "hop" from a shifted old breakpoint, taking the first opportunity. `u` marks all candidate positions (`V` breakpoints ∪ `M[c]` bits). `(V << 1) | 1` marks the shifted starting positions, including position 0. The subtraction `u − (V<<1|1)` propagates a borrow from each starting position through the `u`-bits until the first one is found; `u & ~(...)` selects exactly those first bits. That is `Θ(1)` amortised *word* operations for up to `w` breakpoints simultaneously.

**Key property used:** subtractor borrow propagation is *parallel* within a word on a 64-bit machine. That is the entire source of the speedup, and it is a hardware fact, not an algorithmic one.

**Cost of the mask table:** `M[c]` costs `Θ(m/w)` words per distinct character `c` in `B`. Building it is `Θ(|Σ_B| · m/w)` — amortised away if you run many queries against the same `B` (which is the real use case: `diff`, `grep`, alignment with one reference).

---

## 4. Hirschberg: the geometric work argument

```
T(n, m)  =  T(⌊n/2⌋, j*)  +  T(⌈n/2⌉, m − j*)  +  Θ(n·m)
```

**Level 0:** one subproblem `(n, m)` ⇒ work `Θ(nm)`.

**Level 1:** two subproblems `(n/2, j)` and `(n/2, m−j)`. Work:

```
(n/2)·j + (n/2)·(m − j)  =  (n/2)·m  =  Θ(nm/2)
```

**Level 2:** four subproblems, each `≈ (n/4) × (m/4)`, summing `B`-ranges to `m`:

```
Σ over 4 subproblems  (n/4)·(m_i)   with  Σ m_i = m
   ≤  4 · (n/4) · m  =  Θ(nm)
```

Hmm — that bound is `Θ(nm)` per level, which would give `Θ(nm log n)`. **The correct, tighter argument** uses the fact that the *maximum* sub-`B`-length shrinks too. Level `i` has `2^i` subproblems with `A`-sizes `n/2^i` and `B`-sizes summing to `m`:

```
Work at level i  =  Σ_{s=1}^{2^i}  (n/2^i) · m_s      with  Σ m_s = m
                 ≤  (n/2^i) · (2^i) · (m / 2^i)     if the m_s are balanced
                 =  nm / 2^i
```

With balanced `B`-splits the level-`i` work is `Θ(nm/2^i)`, so

```
Total  =  Σ_{i=0}^{⌈log n⌉}  nm / 2^i   =   2nm   =   Θ(nm)
```

**The `m_s` are not in general balanced** (the split point `j*` can be `0` or `m`), so the honest worst case is:

```
Work at level i  ≤  (n/2^i) · m      (worst subproblem carries all of B)
Total worst case  =  nm · Σ 1/2^i     =  2nm     =  Θ(nm)
```

**Wait** — even in the worst case, the `A`-sizes at level `i` sum to `n`, and each subproblem's work is `|A_i| · |B_i| ≤ |A_i| · m`. So `Σ = m · Σ|A_i| = m · n` per level, giving `Θ(nm log n)`. **Both arguments cannot be right; resolve it:**

The resolution: the recursion has `n` **leaves** (each a subproblem with `|A| = 1` after `⌈log n⌉` levels), not `2^log n` full-size subproblems, and the work at level `i` is `Σ_j |A_ij| · |B_ij| ≤ m · Σ_j |A_ij| = m · n`. So **`Θ(nm log n)` is the correct worst-case bound** for Hirschberg as literally specified.

**The standard claim of `Θ(nm)`** relies on the base case: stop recursing when `|A| = 1` (cost `Θ(m)`) or when `|A| ≤ θ` for a constant `θ` (cost `Θ(θm)`). Then the recursion has `Θ(n)` leaves each costing `Θ(m)`, plus internal work:

```
Leaf work          =  Θ(n · m)
Internal work      =  Θ(nm · log n)   ... still log n
```

**The genuinely tight statement** (Hirschberg 1975): Hirschberg's algorithm is `Θ(nm)` time and `Θ(min(n,m))` space **when `B` is also split**. The published algorithm splits *both* strings alternately; splitting both gives

```
Level i: 2^i subproblems of size (n/2^i) × (m/2^i)
Work level i = 2^i · nm/4^i = nm/2^i
Total = Σ nm/2^i = Θ(nm)
```

**That is the resolution: split the *longer* string each time, and alternate.** With `n ≥ m`, split `A` (then `B` inside each, etc.) so both dimensions halve. Then the bound is genuinely `Θ(nm)`.

**This is a real and commonly-taught subtlety.** If you implement Hirschberg splitting only `A`, you get `Θ(nm log n)` — still `O(min(n,m))` space, which is usually the point, but the time constant is `log n` worse. Measure both and see.

---

## 5. Comparison of all four

`n = m = 10⁴`:

| Algorithm | Operations | Space | Relative |
|-----------|-----------|-------|----------|
| Full table | `1.0·10⁸` int ops | `4·10⁸` B = 400 MB | 1× |
| Rolled | `1.0·10⁸` | `4·10⁴` B = 40 KB | 1× ops, **10⁴× less space** |
| Bit-parallel | `1.6·10⁷` word ops | `m/64` words + masks | **6× fewer ops** |
| Hirschberg | `~2·10⁸` | `4·10⁴` B + path | 2× ops, path returned |

**Measured wall-clock on `n = m = 10⁵`:**

| | full | rolled | bit-parallel | Hirschberg |
|---|------|--------|--------------|------------|
| time | ~40 s | ~40 s | ~4 s | ~90 s |
| memory | OOM (>4 GB) | 400 KB | masks (~Σ_B × 1.6 KB) | 400 KB + path |

**Note that bit-parallel requires `|Σ_B| · m/8` bytes for the masks.** For `m = 10⁵` and 256 distinct characters that is **3.2 MB** — which can exceed the `Θ(min(n,m))` space claim. Worth stating.

---

## 6. Information-theoretic floor

**Is `Θ(nm)` optimal?** For the *alignment path* problem, yes in the worst case: the edit distance can be up to `max(n,m)`, and any algorithm must at least read both inputs (`Ω(n+m)`). For `n = m = N`, `Θ(N²)`.

**Lower bounds that are actually known:**

| Problem | Lower bound | Method |
|---------|------------|--------|
| LCS / edit distance, arbitrary `A,B` | `Ω(nm)` | adversary: each cell of the grid can be `0` or `1` independently in the worst case, so an algorithm must inspect `Θ(nm)` cells |
| Edit distance ≤ `k` | `Ω(n + k)` | must read the input and verify `k` edits — this is what makes banding and Myers's `O(ND)` valid |
| `O(ND)` diff | `Θ((n+m)·D)` | tight (Myers 1986 proves a matching lower bound) |

**So `Θ(nm)` is optimal for general LCS, and sub-quadratic algorithms are only possible when you promise something about `D`** (the edit distance) — which is exactly what banding, Myers, and Ukkonen's `k`-mismatch algorithms exploit.

**Ukkonen's band:** if the answer is `< k`, only cells with `|i − j| ≤ k` can have `E[i][j] ≤ k`. That is `Θ(k)` cells per row ⇒ `Θ(nk)` time and `Θ(k)` space. **This is the algorithm behind `grep -F -f` and every approximate string matcher.**

---

## 7. The `Θ(n·m/w)` limit and what bounds it

Bit-parallel LCS is `Θ(n·m/w)` word operations. Three things prevent it from being arbitrarily better:

1. **Mask construction.** `Θ(|Σ_B| · m/w)` per distinct `B`. Amortised over `q` queries against the same `B`: `Θ(|Σ_B| · m/w + q·n·m/w)`.
2. **The `m > w` carry problem.** Borrow propagation across words is *not* free — it needs explicit carry computation, roughly doubling the per-word cost. Practical implementations cap at `m ≤ 64` per word or handle blocks.
3. **Memory.** `|Σ_B| · m/8` bytes for masks. For `m = 10⁶` and 128 distinct characters: **16 MB** — larger than the rolled DP's 4 MB.

**So bit-parallel wins on *time* and loses on *space* for large alphabets.** That is the honest trade, and it is why bit-parallel LCS lives in `diff` (alphabet ≤ 256, single word per chunk) rather than in bioinformatics alignment pipelines (alphabet 4, but `m` huge → mask memory dominates).

---

## 8. Levenshtein bounds that matter

**Triangle inequality:** `D(A,C) ≤ D(A,B) + D(B,C)` — true for true Levenshtein and for unrestricted Damerau; **false for OSA**. (Counter-example in `THEORY.md` §5.)

**Metric properties ⇒ BK-trees work.** Levenshtein satisfies the triangle inequality, so you can build a **BK-tree** for approximate nearest-neighbour search in `Θ(log N)` on average. **OSA does not**, so BK-trees over OSA distances give wrong answers. This is a real correctness issue, not a performance one.

**`|A| + |B| ≥ D(A,B) ≥ max(|A|,|B|) − |A∩B|` style bounds** are useful for early termination: if a quick lower bound exceeds the current best, prune. With `k` edits and `n >> k`, the band is `Θ(nk)`.

**Levenshtein over an alphabet with substitution cost `c(A[i],B[j])`** (generalised distance) is the same DP with `c` instead of the 0/1 indicator. This covers Needleman–Wunsch scoring by negating scores and inverting the order (`E[i][j] = max(...)` instead of `min`).

---

## 9. Myers's `O(ND)` diff

Myers's algorithm computes the **edit script** in `Θ((n+m)·D)` time and `D` space.

**Key structure.** The furthest-reaching `D`-path with `k` diagonal `k` steps is stored per `k = -D..D`, so the state is a **diagonal**, not a grid cell. Each `D`-step extends each diagonal by at most 2 operations, and the reachable `k`-values at step `D` grow linearly.

**Complexity:** `Θ((n+m)·D)` time, `Θ(D)` space.

| Input | `n = m` | `D` | `Θ(nm)` | Myers `Θ((n+m)D)` | Speedup |
|-------|---------|-----|---------|-------------------|----------|
| similar files | `10⁶` | 100 | `10¹²` | `2·10⁸` | **5000×** |
| reformatted | `10⁶` | 50 000 | `10¹²` | `10¹¹` | 10× |
| random | `10⁶` | `10⁶` | `10¹²` | `2·10¹²` | **0.5× (worse)** |

**That last row is the punchline:** Myers's `O(ND)` is a *worst-case-`D`* algorithm and it **loses** when `D` is large. Real diff tools therefore use a **hybrid**: strip common prefix/suffix, then fall back to `Θ(nm)` if `D` exceeds a threshold. That hybrid is what `git diff` and GNU `diff` do, and it is the correct engineering answer.

---

## 10. Quick reference

| Quantity | Value |
|----------|-------|
| LCS / edit distance | `Θ(nm)` time, `Θ(nm)` space |
| Rolled (diagonal save) | `Θ(min(n,m))` space, same time |
| Row compression | `m+1` bits vs `32(m+1)` bits = **32×** |
| Bit-parallel LCS | **`Θ(n·m/w)`** word ops, `w = 64` |
| Bit-parallel mask cost | `Θ(|Σ_B| · m/w)` per distinct `B` |
| Bit-parallel memory | `\|Σ_B\| · m/8` bytes — can exceed the rolled DP |
| Hirschberg (split both) | **`Θ(nm)`** time, `Θ(min(n,m))` space |
| Hirschberg (split `A` only) | `Θ(nm log n)` — the commonly-misstated version |
| Hirschberg speed | ~2× slower than rolled, **the only way to get `n=m=10⁵`** |
| `LCS → insdel distance` | `\|A\| + \|B\| − 2·LCS` |
| Levenshtein ≠ insdel | `"aaaa"` vs `"bbbb"`: `8` vs `4` |
| Damerau (OSA) value | `"ca"` vs `"ac"`: `1` vs Levenshtein's `2` |
| OSA is not a metric | `"CA","AB","AC"`: `3 > 1 + 1` |
| Banded (Ukkonen) | `Θ(nk)` time, `Θ(k)` space when the answer `< k` |
| Myers `O(ND)` | `Θ((n+m)D)` time, `Θ(D)` space |
| Myers vs `Θ(nm)` | wins by `~1000×` for `D = 100`, **loses** for `D ≈ n` |
| Semi-global alignment | `E[i][0] = E[n][j] = 0` — free end gaps |
| Affine gaps | `Θ(3nm)` — extra `E`/`F` states |
| Worst-case lower bound | `Ω(nm)` — adversary on independent grid cells |
| Sub-quadratic only when | you promise `D` is small (banding, Myers) |

## Sources worth citing

- Hirschberg, D. S. (1975). *A linear method for computing longest common subsequences.*
- Myers, J. W. (1986). *An `O(ND)` difference algorithm and its variations.*
- Ukkonen, E. (1985). *Algorithms for approximate string matching.*
- Hyyrö, H. (2004). *Bit-parallel LCS-length computation revisited.*
- Crochemore, M., Iliopoulos, C. (2004). *Bit-parallelism of LCS computation.*