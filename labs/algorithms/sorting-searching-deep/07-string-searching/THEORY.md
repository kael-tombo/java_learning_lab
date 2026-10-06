# Theory — String Searching

String searching is not one problem but three, and they have different optimal algorithms:

| Problem | Complexity | Algorithm |
|---------|-----------|-----------|
| One pattern in one text | `Θ(n + m)` deterministic | KMP, Z-algorithm |
| One pattern, average case, large alphabet | sublinear in `n` | Boyer–Moore |
| Many patterns, one text | `Θ(Σ|Pᵢ| + n)` | Aho–Corasick |

Understanding *which* problem you have is worth more than any single implementation.

---

## 1. The setup

Text `T` of length `n`, pattern `P` of length `m` (`m ≤ n`). We report every index `i` with `T[i..i+m-1] = P`.

**The comparison-counting subtlety.** For naive search, "comparisons" is usually defined as *character comparisons*. Under this metric:
- Naive: up to `(n − m + 1)·m` character comparisons = `Θ(nm)`.
- KMP: at most `2n` character comparisons (proved below).
- Boyer–Moore: **as few as `n/m` character comparisons** in the best case.

This is why BM can be called sublinear: with `m = 1000` and a 256-symbol alphabet, the average skip is ~`256` positions, so you can find a match in a 10⁷-character text with ~4 000 comparisons.

---

## 2. Naive search and why it is `Θ(nm)`

```java
for (int i = 0; i + m <= n; i++)
    if (T.startsWith(P, i)) report(i);       // O(m) but startsWith is intrinsified
```

Worst case: `P = "aaaa...a"` (m a's), `T = "aaaa...a"` (n a's). Every window matches on all `m` characters but the *last* one differs... to get `Θ(nm)` you need `P = "aaab"` and `T = "aaaa...a"`: every one of the `n−3` windows compares 3 a's successfully and then fails on `b`, costing `Θ(nm)` total.

**Never ship this.** Its only virtue is being the correctness oracle for the other six algorithms.

---

## 3. KMP — the prefix function

### The failure function

For each `i`, `lps[i]` = length of the longest prefix of `P` that is also a suffix of `P[0..i]`, **excluding the whole prefix itself** (hence "proper").

```java
static int[] lps(String p) {
    int[] lps = new int[p.length()];
    for (int i = 1, len = 0; i < p.length(); ) {
        if (p.charAt(i) == p.charAt(len)) lps[i++] = ++len;
        else if (len > 0)               len = lps[len - 1];   // fall back
        else                           lps[i++] = 0;
    }
    return lps;
}
```

**Build cost:** `Θ(m)`. The inner `len` only increases by 1 per outer iteration and only decreases via `lps[len-1] < len`, so the total decrease is bounded by the total increase → `O(m)` amortised.

**Example.** `P = "ABABCABAB"`:

```
i    : 0 1 2 3 4 5 6 7 8
P[i] : A B A B C A B A B
lps  : 0 0 1 2 0 1 2 3 4
```

`lps[8] = 4` means `"ABAB"` is both a prefix and a suffix of `"ABABCABAB"`.

### Search

```java
static void kmp(String t, String p, IntConsumer out) {
    int[] lps = lps(p);
    int j = 0;
    for (int i = 0; i < t.length(); i++) {
        while (j > 0 && t.charAt(i) != p.charAt(j)) j = lps[j - 1];   // fall back
        if (t.charAt(i) == p.charAt(j)) j++;
        if (j == p.length()) { out.accept(i - p.length() + 1); j = lps[j-1]; }
    }
}
```

### Correctness: the no-backtracking invariant

> **After processing `t[i]`, `j` is the length of the longest prefix of `P` that is a suffix of `t[0..i]`.**

- If `t[i] == p[j]`, extending gives `j+1` — and no longer prefix can match, because any longer match would have had to be a match at `t[i-1]` too, contradicting maximality.
- If `t[i] != p[j]`, every candidate prefix length `k < j` must be such that `p[0..k-1]` is a suffix of `t[0..i-1]`, i.e. a *border* of `p[0..j-1]`. The chain `j, lps[j-1], lps[lps[j-1]-1], ...` enumerates **all** borders in decreasing order, so the first `k` that matches is the right one.

**That chain is the entire algorithm.** It is why `lps` must be the *longest* proper border and why the fallback chain (not a single fallback) is required.

### Complexity proof

Two counters:

- `i` advances exactly `n` times, **never backwards**.
- `j` advances by 1 per character match. Each `while` iteration decreases `j` by at least 1 (`lps[j-1] < j`).

Since `j` starts at 0, is bounded above by `m`, and is never negative:

```
Σ (increases of j) = Σ (decreases of j) + final_j  ≤  Σ (decreases) + m
```

Total `while`-iterations `≤` total `j`-decreases `≤` total `j`-increases `+ m = n + m`.

So: **`Θ(n + m)` character comparisons, `Θ(n)` `while`-iterations, `Θ(m)` space.** Text pointer never moves backwards — that is the whole point and the reason KMP beats naive on *any* input, including ones where naive happens to be fast.

### When KMP is preferred

- **Guaranteed linear**, no hash collisions.
- **Overlapping matches** are handled trivially (`j = lps[j-1]` after a match) — critical for `"aaaa"` in `"aaaaaa"` (4 matches, not 1).
- **`m` very large, alphabet small**: no skip-table memory needed.

### When KMP is *not* preferred

- Large alphabet, large `m`: Boyer–Moore does fewer comparisons.
- `m` very small: KMP's setup (`Θ(m)` lps) is a fixed overhead and the search is only `Θ(n)` anyway.
- **`m = 1` or `m = 2`:** degenerate for BM; use `indexOf`.

---

## 4. Boyer–Moore

### The idea: compare from the right, skip on mismatch

Compare `P[m-1]` against `T[i+m-1]`. If they differ, we can skip up to `m` text characters because the whole window is dead.

### Horspool (the version Java's ancestors used)

Precompute, over the **whole** pattern, `last[c]` = the last index where `c` occurs in `P` (or `-1`).

```
while i <= n - m:
    j = m - 1
    while j >= 0 and P[j] == T[i+j]: j--
    if j < 0: report i; i += m            // full match: skip whole pattern
    else:     i += m - last[T[i + m - 1]]  // PITFALL: uses T[i+m-1], NOT T[i+j]
```

**The shift uses `T[i + m - 1]`, not the mismatching character `T[i+j]`.** Using `T[i+j]` is the most common BM implementation bug and it makes the algorithm incorrect (you can skip past a match).

**Correctness of the skip:** if `c = T[i+m-1]` does not appear in `P` at all (`last[c] = -1`), then shifting by `m` is safe — no window that starts at `i+1 … i+m` can match, because any such window has `c` at a position corresponding to `P`'s last `m − (start − i) ` characters... precisely: aligning the *right end* of the pattern with `c` is impossible, so no alignment in `[i+1, i+m]` works.

### Complexity

- Average skip `= m − last[c]`. For a random pattern and a text from an alphabet of size `σ`, the expected skip is `Θ(σ/m)` (capped at `m`).
- Expected comparisons `≈ n·m/σ`.
- **Best case `Θ(n/m)`**: e.g. searching `"abc"` in a text of random letters — you skip `m` positions per mismatch.
- **Worst case `Θ(nm)`**: `P = "aaaab"`, `T = "aaaa...a"` — the first 4 characters always match, then `b` mismatches, and the shift is small.

### The good-suffix rule (full Boyer–Moore)

Two rules, take the larger shift:

1. **Bad-character:** shift `j − last[T[i+j]]`.
2. **Good-suffix:** if `P[j+1..m-1] == T[i+j+1..i+m-1]` (the suffix matched), find the longest `k < m` such that `P[j+1..m-1]` has `P[j+1..m-1-k]` as both a prefix and a suffix; shift by `m − k`.

Precomputation is `Θ(m·σ)` naive, `Θ(m)` with the two-pointer variant.

**Skew table / Knuth–Morris–Pratt + Horspool (BMH)** — the practically important refinement:
```
i += m - 1 - last[T[i + m - 1]]
```
i.e. after computing the mismatch at `j = m − 1 − (m − 1 − last[...])`, skip the *entire pattern length minus the bad character's last position*. This turns the worst case for Horspool into something much better and is what makes BMH excellent on real text.

### Why this matters in production

`String.indexOf` in HotSpot is a hand-tuned, intrinsified Horspool/BMH variant:

```java
// Roughly what StringLatin1.indexOf does
int indexOf(byte[] value, byte[] str) {
    int n = value.length, m = str.length;
    if (m == 0) return 0;
    if (m > n) return -1;
    // last[c] table built on the fly into a small skip array
    ...
    while (i + m <= n) {
        // compare from the right, skip on mismatch
    }
}
```

Measured: `"the quick brown fox".indexOf(...)` on a 1 MB haystack is **~10–50× faster** than a hand-written KMP, because (a) fewer comparisons and (b) the whole loop is JIT-intrinsified into a tight scan. **Lesson: for single-pattern search, just use `String.indexOf` / `String.contains` unless you have measured otherwise.**

---

## 5. Rabin–Karp — and its honest complexity

### Rolling hash

```
H(s) = ( Σ s[i] · B^(m-1-i) ) mod P
H(T[i+1..i+m]) = ( H(T[i..i+m-1]) · B + c − s[i]·B^m ) mod P     in O(1)
```

Compare `H` of the window to `H(P)`. On equality, verify with a real comparison to eliminate false positives.

### The complexity nobody writes down correctly

Naively: `Θ(n + m)` hash operations plus verification. But:

- A **hash operation** on a `w`-bit modulus is `Θ(w)` machine words. With `w = 64`, it is a constant in practice but not free.
- **Collisions** trigger a `Θ(m)` verification. With a random prime modulus `p` and a random base, the per-window false-positive probability is `≈ 1/p`, so expected total verification cost is `Θ(n·m/p)`.

Setting `p ≫ n·m` makes the expected cost `Θ(n + m)`.

**But:**

- `p ≫ nm` means `p` needs `Θ(log(nm))` bits — for `n = 10⁶`, `m = 10³`, `p ≈ 2⁴⁰`. Fine, but you cannot use a single machine-word multiply-and-modulo; you need `long` (mod `2⁶⁴` is not a prime) or `BigInteger`.
- Double hashing or a random prime both cost extra per window.

**Verdict:** Rabin–Karp is *theoretically* optimal but in practice **slower than KMP and BM-Horspool**, and it is **Monte Carlo** (can report a false match). Its real niche:

- **Streaming search** where you cannot re-read the window (the hash is updated as bytes arrive) — this is genuinely useful in network/protocol scanning.
- **Searching a text that changes** (you keep the window's hash and slide).
- **Hardware-accelerated** word hashing (`crc32`, `Long.hashCode`) making the per-window cost ~2 cycles.

---

## 6. The Z-algorithm

### Definition and mechanism

`Z[i]` = length of the longest common prefix of `T` and `T[i..n-1]`.

```java
static int[] z(String s) {
    int n = s.length();
    int[] z = new int[n];
    int l = 0, r = 0;                                  // [l, r] is the rightmost-reaching box
    for (int i = 1; i < n; i++) {
        if (i < r) z[i] = Math.min(r - i, z[i - l]);   // copy from the box: O(1)
        while (i + z[i] < n && s.charAt(z[i]) == s.charAt(i + z[i])) z[i]++;
        if (i + z[i] - 1 > r) { l = i; r = i + z[i] - 1; }   // extend the box
    }
    return z;
}
```

**Why linear:** the inner `while` only does real work when `z[i]` extends **past** the current rightmost box `[l, r]`. Every character advanced inside the box is matched by a `Z` value already computed (the `z[i-l]` copy). Since the box's right edge `r` only ever increases, the total inner-loop work is `O(n)`.

**Invariant:** `[l, r]` is the box with maximum `r` among all boxes found so far, and `T[l..r] = T[0..r-l]`.

### Why Z subsumes KMP

Concatenate: `S = P + '\u0000' + T`. Then `P` occurs at text position `i` iff `Z[|P| + 1 + i] ≥ |P|`. So:

```
Z-algorithm on P + sep + T   ==   KMP
```

Z's constant factor is typically 2–3× worse (it allocates `Θ(n+m)` vs `Θ(m)`), but it also computes all the other useful things at no extra cost:

| Application | How |
|-------------|-----|
| Pattern matching | `Z(P + sep + T) ≥ m` |
| Longest common prefix of all suffixes | `Z` itself |
| Longest common prefix of `T[a..]` and `T[b..]` | `Z(b+a)` |
| Longest common **extension to the left** | mirror string + `Z` |
| Palindrome detection | Manacher's algorithm (`Θ(n)`) — the odd/even `Z` variant |
| Smallest period of a string | `Z[n-p] ≥ n-p` |
| Runs / repetitions | `Z` + LCP arrays |
| Suffix automaton construction | the standard linear method |

**Practical note:** for single-pattern search in Java, `String.indexOf` beats both. Z's value is as a *toolbox* for the suffix-array/suffix-automaton machinery (labs 27 / `03-string-algorithms-advanced`).

---

## 7. Aho–Corasick — multi-pattern search

### Setup

Given patterns `P₁ … P_k` with total length `S = Σ|Pᵢ|`, and text `T` of length `n`, report every occurrence of every pattern.

**Naive:** run KMP `k` times ⇒ `Θ(k·n + S)`.

### Construction

1. **Trie** of all patterns: `S` nodes, each with `σ` transitions. `Θ(S·σ)` dense, `Θ(S)` sparse.
2. **Failure links** by BFS: `fail(u)` = the longest proper suffix of `u`'s string that is also a trie prefix. Computed with the standard recurrence
   ```
   fail(u) = goto(fail(parent(u)), c)   for the edge parent(u) --c--> u
   ```
   `Θ(S·σ)` dense, `Θ(S · amortised)` sparse.
3. **Output links:** `output(u)` = the nearest proper suffix-node that is a pattern *end*. Chains let you report overlapping matches in `Θ(matches)` total rather than `Θ(σ)` per position.

### Scanning

```java
int state = 0;
for (int i = 0; i < t.length(); i++) {
    state = transition(state, t.charAt(i));       // follows goto, else fail, repeatedly
    for (int u = state; u != 0; u = output(u)) report(u, i - depth(u) + 1);
}
```

### Complexity

- Build: `Θ(S·σ)` dense, `Θ(S)` sparse.
- Scan: `Θ(n + matches)`.
- **Total: `Θ(S·σ + n + matches)`** — independent of `k` except through `S`.

**The output-link detail that matters:** in `"aaaa"` with patterns `{"a", "aa", "aaa", "aaaa"}`, every position matches all patterns ending there. Reporting via `output(u)` chains is `Θ(1)` per report; walking the whole `goto`/`fail` tree per position is `Θ(σ)`. **This is the difference between linear and quadratic on adversarial input.**

### Space trade-off

| Representation | Build | Space | Scan constant |
|----------------|-------|-------|---------------|
| Dense `[node][σ]` goto | `Θ(S·σ)` | `Θ(S·σ)` | best — one array index |
| Sparse `Map<Character,Node>` | `Θ(S)` | `Θ(S)` | worse — hash lookup per char |
| **Compressed (DFA on the fly)** | `Θ(S·σ)` time, `Θ(S)` space | `Θ(S)` | best — pure array index, no fail chain |

The compressed-DFA variant (`gotoDFA[v][c]` filled in from `fail` links after BFS) is the production choice for large alphabets: it keeps the `Θ(n)` scan constant factor minimal while using only `Θ(S)` space. For ASCII it needs 256 ints per node — 1 KB per node — so use it only when `S` is small; otherwise use a sparse map plus a fail chain.

---

## 8. Failure-function relationships (worth memorising)

```
            Z-array of P           longest border of P[0..i]
                |                             |
                v                             v
    all suffixes matching prefix   <---->  KMP failure function
        of the SAME string                   (one string, positions as prefixes)

            KMP failure function  <---->  Aho-Corasick failure links
                (one pattern)                (a whole trie)
```

- **KMP's `lps` is Aho–Corasick's failure link applied to a chain (trie) of length 1.** Generalising KMP to many patterns *is* Aho–Corasick.
- **Z on `P + sep + T` equals KMP** in power.
- **Suffix automaton** is the minimal DFA recognising "all suffixes of `T`"; its construction uses the Z/`lcp` machinery.

This is the conceptual spine of the string labs: prefix/suffix overlap information is the invariant, and every algorithm here is a different encoding of it.

---

## 9. Choosing an algorithm

| Situation | Choice | Why |
|-----------|--------|-----|
| Single pattern, production Java | **`String.indexOf` / `String.contains`** | intrinsified BMH; 10–50× a hand-rolled KMP |
| Single pattern, guaranteed linear, `m` large | KMP | no hash, exact, overlapping matches |
| Single pattern, huge alphabet, sublinear desired | Boyer–Moore (full) or BMH | fewer than `n` comparisons |
| Single pattern, streaming (window cannot be re-read) | Rabin–Karp | rolling hash updated as bytes arrive |
| Many patterns, static set | **Aho–Corasick** | `Θ(S + n)` regardless of `k` |
| Many patterns, non-matching (fingerprint) only | Rabin–Karp or a Bloom-filter prefilter | O(1) memory per pattern |
| Many patterns, `k` small (≤ 5) and `m` small | run `indexOf` per pattern | the constant factor beats automaton construction |
| All suffix/LCP queries | suffix array / suffix automaton | see labs 27 and `03-string-algorithms-advanced` |
| Palindromes in `Θ(n)` | Manacher's algorithm | the odd/even `Z` variant |

**The Bloom-filter prefilter deserves emphasis:** before running Aho–Corasick over a large pattern set, drop patterns whose Bloom filter does not hit for the text's distinct characters. For content filtering this routinely removes 95% of candidate patterns and turns a `Θ(S·σ)` build into something cheap.

---

## 10. Adversarial inputs for benchmarking

Any honest benchmark must include these, or the numbers are meaningless:

| Input | Kills |
|-------|-------|
| `P = "aaaa...a"`, `T = "aaaa...a"` | naive (matched prefixes) |
| `P = "aaaab"`, `T = "aaaa...a"` | naive, BM-Horspool (long partial matches) |
| `P = "baaaab"`, `T = "aaaa...a"` | BM good-suffix rule |
| Fibonacci words (`abaababaabaab...`) | **all** linear-time algorithms simultaneously; also destroys naive cache assumptions in suffix structures |
| `T` random over a 2-symbol alphabet | DNA / low-entropy collapse — BM's skip advantage vanishes |
| `P` a single character | BM degenerates to `Θ(n)` with no skipping |
| Many overlapping patterns (`{"a","aa","aaa",...}`) in `"aaaa..."` | Aho–Corasick output reporting |