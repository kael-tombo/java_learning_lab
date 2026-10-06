# Math Foundation — String Searching

Amortised proof of the KMP linear-time bound, the Z-algorithm accounting, and the skip-distance arithmetic behind Boyer–Moore.

---

## 1. KMP: the amortised `Θ(n + m)` proof

Two counters: text pointer `i` (monotone, `0 → n`) and pattern pointer `j` (`0 → m`, never negative).

**Claim:** the number of `while`-loop iterations `≤` the total decrease in `j`.

**Proof.** Let `U` = total `j`-increments, `D` = total `j`-decrements. Since `j` starts at 0, ends at `j_f ≥ 0`, and never goes below 0:

```
U − D = j_f  ⟹  U = D + j_f ≤ D + m
```

Each `while` iteration strictly decreases `j` by at least 1 (`lps[j-1] ≤ j-1`). Each `j`-increment comes from one successful `t[i] == p[j]` comparison. So:

```
U ≤ n        (at most one increment per text character)
iterations  ≤  D  =  U − j_f  ≤  n
```

**Total: `Θ(n + m)` character comparisons** — at most `n` increments plus at most `n` decrements. ✓

### Why naive is `Θ(nm)` on the same input

`P = "aaab"`, `T = "aaaa…a"` (`n` a's):

| window `i` | comparisons before failing |
|------------|--------------------------|
| 0 | `a=a, a=a, a=a, a≠b` → 4 |
| 1 | same → 4 |
| … | |
| `n−3` | same → 4 |

Total `≈ 4n`. To get a true `Θ(nm)`, take `P = "a"^m + "b"`: every one of the `n−m` windows matches `m` a's then fails on `b`:

```
(n − m + 1) · (m + 1)  =  Θ(nm)
```

**KMP on that same input:** the `lps` chain of `"a"^m` is `0, 1, 2, ..., m-1`, so on each mismatch `j` falls back by exactly 1. Total decrements `≈ n` ⇒ **`Θ(n)`**. Ratio `m:1`. For `m = 10³`, KMP is a thousand times better on this input.

### Exact worst-case comparison count for KMP

Known result: **at most `2n + m − 2` character comparisons** for `n ≥ m`. (Proved via the `U ≤ n`, `D ≤ U` accounting above with a tighter `j_f ≤ m` bound.)

| Algorithm | `n = 10⁶`, `m = 10³`, worst-case input |
|-----------|-----------------------------------------|
| Naive | `~10⁹` |
| **KMP** | `~2·10⁶` |

**500× gap on the worst case.**

---

## 2. The Z-algorithm accounting

Let `[L, R]` be the rightmost-reaching box: `T[L..R] = T[0..R−L]`, with `R` maximum so far.

For each `i`:
- If `i < R`: `Z[i] ≥ min(R − i, Z[i−L])` — **copied in O(1)**, no character comparisons.
- Then the `while` loop may extend beyond `R`.

**Key claim:** every character examined inside the `while` loop that lands at a position `≤ R` was already counted as a `Z` value.

```
T = "aabxaabxaaab"
     ^--- Z[1]=1
```

Formally: while `i + Z[i] ≤ R`, the comparison succeeds or fails but the position is inside the known box, where `Z[i−L]` already told us the answer — so **at most one comparison per `i`** is spent inside the box. Comparisons *outside* the box (`i + Z[i] > R`) extend `R`.

Since `R` increases monotonically from 0 to `n` and is increased by at most 1 per outer iteration:

```
Total inner-loop body executions  ≤  (initial R) + Σ (R increase)  ≤  n
Total outer iterations            =  n − 1
Total                            =  Θ(n)
```

### `Z` vs KMP as pattern matchers

```
Z(P + '\0' + T):   n' = m + 1 + n,  Θ(n + m) time,  Θ(n + m) space
KMP:               Θ(n + m) time,  Θ(m) space
```

Same time; Z uses more memory. **But** Z also yields all the other prefix/suffix data. Trade-off summary:

| | Time | Space | Gives you |
|---|------|-------|-----------|
| KMP | `Θ(n+m)` | `Θ(m)` | match positions only |
| Z | `Θ(n+m)` | `Θ(n+m)` | match positions + every `LCP(T, T[i..])` |
| Suffix array | `Θ(n log n)` or `Θ(n)` | `Θ(n)` | match positions + `LCP` of any two suffixes |
| Suffix automaton | `Θ(n)` | `Θ(n·σ)` | match positions + longest matching suffix at every prefix |

---

## 3. Boyer–Moore skip arithmetic

### The expected skip

Let `P` be a random pattern of length `m` over an alphabet of size `σ`, and `c` a uniformly random text character. The last position of `c` in `P` is `m-1` with probability `1/σ`, `m-2` with probability `(1-1/σ)/σ`, etc.

```
E[m − 1 − last[c]]  =  Σ_{k=0}^{m-1} k · P(last[c] = m-1-k)
                    =  Σ_{k=0}^{m-1} k · σ^{-(k+1)}
                    ≈  m/σ          (for m << σ)
```

Capped at `m` (you cannot skip past a full pattern length on a Horspool step):

```
E[skip]  =  min(m, m/σ + 1)
```

**Expected character comparisons:**

```
                n
E[comparisons] = --- · E[comparisons per window]
                E[skip]
```

With `E[comparisons per window] ≈ 1` (the rightmost characters usually mismatch immediately):

| σ | `m` | `E[skip]` | `E[comparisons]` for `n = 10⁶` |
|---|-----|-----------|----------------------------------|
| 2 (DNA) | 10³ | 2 | **500 000** — no better than KMP |
| 2 | 10³ | … | KMP wins |
| 26 (letters) | 10³ | 38 | 26 000 |
| 95 (printable) | 10³ | 12 | 83 000 |
| 256 (bytes) | 10³ | 5 | 200 000 |
| 256 | 100 | 2.4 | 420 000 |
| 256 | 10 | 1 | 10⁶ — **worse than KMP** |
| 65 536 (unicode, frequent) | 10³ | 1000 | 1000 |

### The crossover

BM beats KMP when `E[comparisons] < 2n`:

```
n·m/σ  <  2n    ⟺    m/σ < 2    ⟺    m < 2σ
```

| Alphabet | BM wins for |
|----------|-------------|
| 2 (DNA) | never |
| 26 | `m < 52` |
| 95 (printable ASCII) | `m < 190` |
| 256 (bytes) | `m < 512` |

**Practical implication:** for typical English text with words of length 3–15 and σ = 95, BM-Horspool's skip advantage is small — yet BM still wins because its *average comparisons per window is below 1* while KMP's is ~2. The win is in the constant factor and in the branch predictability of the loop, not in a dramatic asymptotic gap.

### Good-suffix rule analysis

Define `γ(i)` = the largest `k` such that the suffix `P[i..m-1]` occurs in `P` again at a position shifted by `k`. The good-suffix rule shifts by `m − γ(j+1)`.

Worst case for the good-suffix rule alone (M needle / haystack pattern): `P = "b" + "a"^(m-1)`, `T = "a"^(n-1)`. All `(m−1)` a's match on every window, then `b` mismatches, and `γ` is small ⇒ `Θ(nm)`.

This is why **full BM has `Θ(nm)` worst case** despite the good-suffix rule. Only BMH (Knuth–Morris–Pratt–Horspool, 1980) restores a practical `Θ(n)` on such inputs by adding a third rule: if the mismatch position is `m−1`, shift by `m` outright.

---

## 4. Aho–Corasick accounting

Let `S = Σ|Pᵢ|`, `σ` = alphabet size, `n` = text length, `M` = total number of (pattern, position) matches.

### Build

```
Trie construction:     Θ(S)          (each character creates or extends one node)
Failure links (BFS):   Θ(S·σ) dense,  Θ(S) sparse
DFA completion:        Θ(S·σ) dense
```

**Dense total: `Θ(S·σ)`.** For `S = 10⁶` and σ = 256: `2.56·10⁸` ints = **1 GB**. This is why large pattern sets use sparse maps or the compressed variant.

### Scan

```
Text traversal:   Θ(n)      (each character advances the state by at least one fail link, amortised)
Output reporting: Θ(M)
```

**Amortised state advance:** along a single text position, you may traverse `d` fail links. The number of fail-link traversals over the whole scan is bounded by the total decrease in "depth of the current suffix", which telescopes against the `n` character advances ⇒ `Θ(n)`.

### Total

```
Θ(S·σ + n + M)     dense
Θ(S + n + M)       sparse
```

### The output-explosion problem

Pattern set `{"a", "aa", "aaa", …, "a"}` of length `k` over text `"a"ⁿ`: the number of matches is `M = Θ(nk)`. Reporting them all is **`Ω(nk)` output** — no algorithm can beat it. But *counting* them is only `Θ(n)` if you chain output links:

```
For "aaa..." with patterns {a, aa, aaa}:   matches at position i = i, total M = Θ(nk).
With output links: report each once → Θ(M) = Θ(nk) reports (unavoidable if you must list them).
Without output links: walk the failure chain from the state → also Θ(k) per position.
```

The distinction: output links give **`Θ(1)` amortised navigation** between consecutive reports, so the total is `Θ(n + M)` rather than `Θ(n + k²)`. **That is the difference between linear and quadratic on adversarial pattern sets**, and it is why the `output` chain is not an optimisation but a correctness-of-complexity feature.

### The Bloom-filter prefilter

If you must report only *whether* any pattern matches (or which of `k` patterns are candidates), a Bloom filter over the patterns' character sets reduces `k` to `k'` candidates:

```
Build cost:  Θ(Σ|Pᵢ|)
Scan cost:   Θ(n) hash lookups, O(1) false positives
Expected reduction on real content:  k' ≈ 0.05 k
```

Net: `Θ(n + Σ|Pᵢ|)` with a much smaller `S`. This is exactly how production content filters avoid the `Θ(S·σ)` blow-up.

---

## 5. Space-time table (the practical decision data)

| Algorithm | Time | Space (bits) | For `n = 10⁶`, `m = 10³` |
|-----------|------|--------------|---------------------------|
| Naive | `Θ(nm) = 10⁹` | `O(1)` | ~3 s |
| KMP | `Θ(n+m)` | `Θ(m·w)` ≈ 8 KB | ~2 ms |
| Z | `Θ(n+m)` | `Θ(n·w)` ≈ 4 MB | ~3 ms |
| BM-Horspool | `Θ(n)` avg | `Θ(σ·w)` ≈ 1 KB | ~1 ms |
| BM full | `Θ(n)` avg, `Θ(nm)` worst | `Θ(m·σ)` ≈ 256 KB | ~1 ms |
| Rabin–Karp | `Θ(n+m)` expected | `O(1)` + `Θ(m)` | ~4 ms |
| Aho–Corasick (`k` patterns, total `S = 10⁵`) | `Θ(Sσ + n)` | `Θ(Sσ·w)` ≈ 10 GB dense | use sparse: ~1 MB |

`w` = bits per character (`8` for bytes, `16` for Java `char`). **Java's `char` being 16 bits is why dense Aho–Corasick tables are so memory-hungry: restrict to `byte[]`/`latin1` strings and use σ = 256.**

---

## 6. Information-theoretic floor

Any search must at minimum read the text: `Ω(n)` character accesses, or `Ω(n/w)` word accesses. Both KMP and Aho–Corasick achieve `Θ(n)`, so they are **asymptotically optimal for deterministic single-pattern search**.

Boyer–Moore can beat `Θ(n)` *in comparisons* by exploiting the fact that the answer's location has `log₂ n` bits of entropy — you need only `log₂ n` bits of information, so `Θ(log n)` comparisons suffice in principle. BM gets within a factor of `m/σ` of that, which is why "sublinear in comparisons" is legitimate rather than a paradox.

---

## 7. Quick reference

| Quantity | Value |
|----------|-------|
| KMP comparison bound (worst) | `≤ 2n + m − 2` |
| KMP build cost | `Θ(m)` (amortised `j` accounting) |
| Z-algorithm total | `Θ(n)`, driven by monotone `R` |
| Naive worst case | `Θ(nm)` (`P = "a"^m + "b"`) |
| BM expected skip | `min(m, m/σ + 1)` |
| BM expected comparisons | `n·m/σ` |
| BM beats KMP when | `m < 2σ` |
| BM worst case | `Θ(nm)` (`P = "b" + "a"^(m-1)`) |
| BMH fixes that by | shifting `m` when the mismatch is at `m−1` |
| Rabin–Karp window cost | `O(1)` hash, `Θ(w)` words |
| RK false-positive probability | `≈ 1/p` per window; need `p ≫ nm` |
| Aho–Corasick build (dense) | `Θ(S·σ)` |
| Aho–Corasick scan | `Θ(n + M)` |
| Aho–Corasick total (sparse) | `Θ(S + n + M)` |
| Output-link necessity | makes reporting `Θ(n+M)` instead of `Θ(n + k²)` |
| Java's `String.indexOf` | intrinsified BMH — use it in production |