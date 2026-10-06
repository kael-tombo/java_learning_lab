# 07 — String Searching

<div align="center">

**Naive · KMP · Boyer–Moore · Rabin–Karp · Z-Algorithm · Aho–Corasick · Sunday Quick Search**

</div>

---

## Learning Objectives

- Distinguish the three different "string searching" problems: one pattern, many patterns, and substring/prefix queries
- Derive KMP's failure function and prove its `Θ(n + m)` guarantee
- Explain why Boyer–Moore can be sublinear (fewer than `n` comparisons) and when it is not
- Explain Rabin–Karp's true expected complexity (Monte Carlo, not deterministic `O(1)`)
- Implement the Z-algorithm and use it for pattern matching, convolution-free matching, and palindrome detection
- Implement Aho–Corasick for multi-pattern matching with `Θ(total_pattern_length + text_length)`
- Know which algorithm each real system uses (and why Java's `String.indexOf` is Boyer–Moore-Horspool)

## Prerequisites

- Hashing for Rabin–Karp
- Automata/greeks for Aho–Corasick
- `16-string-matching` and `40-string-algorithms-advanced` for the structural cousins (suffix arrays, suffix automata)

## Estimated Time

- **Theory**: 110 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## The Three Problems

| Problem | Input | Output | Canonical algorithm |
|---------|-------|--------|---------------------|
| **Single-pattern search** | text `T` (`n`), pattern `P` (`m`) | all match positions | KMP / Boyer–Moore |
| **Multi-pattern search** | `k` patterns | all `(pattern, position)` matches | **Aho–Corasick** |
| **Substring / prefix query** | `T`, suffixes/prefixes | answers | suffix array / automaton |

Choosing the wrong family is the most common design mistake: `Aho–Corasick` is `Θ(Σ|P| + n)` for *any* `k`, while running KMP `k` times is `Θ(k·n)`.

## Complexity Snapshot

| Algorithm | Best | Average | Worst | Extra space | Deterministic? |
|-----------|------|---------|-------|-------------|----------------|
| Naive | `Θ(1)` | `Θ(nm)` | `Θ(nm)` | O(1) | yes |
| KMP | `Θ(n)` | **`Θ(n)`** | `Θ(n)` | `Θ(m)` | yes |
| Boyer–Moore (full) | `O(n/m)` | `Θ(n)` | `Θ(nm)` | `Θ(m)` | yes |
| Boyer–Moore-Horspool | `O(n/m)` | `Θ(n)` | `Θ(nm)` | `Θ(σ)` | yes |
| Boyer–Moore–Hood | `O(n/m)` | `Θ(n)` | `Θ(n)` | `Θ(σ)` | yes |
| Rabin–Karp | — | **`Θ(n + m)` expected** | `Θ(nm)` | O(1) | **no** (Monte Carlo) |
| Z-algorithm | `Θ(n)` | `Θ(n)` | `Θ(n)` | `Θ(n)` | yes |
| Aho–Corasick | `Θ(Σ|P| + n)` | `Θ(Σ|P| + n)` | `Θ(Σ|P| + n)` | `Θ(Σ|P|·σ)` | yes |

## Algorithms Covered

### Naive
```
for i in 0..n-m:  if T[i..i+m-1] == P: report i
```
`Θ(nm)`. Never acceptable — except for `m ≤ 2`, or as a baseline for benchmarking.

### KMP
- **Failure function** `lps[i]` = length of the longest *proper* prefix of `P[0..i]` that is also a suffix. Build in `Θ(m)`.
- **Search:** on mismatch at `P[j]`, set `j = lps[j-1]` — **the pattern is not re-scanned from scratch, and the text pointer never moves backwards.**
- **Why linear:** the text pointer `i` advances exactly `n` times; the pattern pointer `j` advances at most `n + m` times total (each advance is either a match advance or a lps-reset, and resets only move `j` down while `i` moves up). Total `Θ(n + m)`.
- **Key insight:** prefix-overlap information. `lps` encodes exactly how much of the pattern is still valid after a mismatch.

### Boyer–Moore (and Horspool / Hood variants)
- Compare **right to left**, allowing a mismatch near the end to skip up to `m` text positions.
- **Good-suffix rule:** if `P[j..m-1] == T[i+j..i+m-1]` matched and `P[j] ≠ T[i+j]`, skip to the next occurrence of that suffix's longest border.
- **Bad-character rule:** precompute `last[c]` = the last index of character `c` in `P`. On mismatch, skip `j − last[c]` positions ( Horspool: `last[c]` over the *whole* pattern, giving a simpler, slightly weaker rule).
- **Why sublinear:** with a large alphabet and `m` large, the average skip is `Θ(σ/m)`, so `Θ(n·m/σ)` comparisons — potentially **fewer comparisons than the text length**.
- **Where it loses:** `m = 1` or `m = 2` (no skip possible), tiny alphabets (DNA, base-64), and long patterns with periodic structure.
- **This is what `String.indexOf` uses.** HotSpot's `StringLatin1.indexOf` is a hand-optimised Horspool-like algorithm with an `intrinsic` candidate — it is ~5–10× faster than a naive loop and is the single most optimised string routine in the JDK.

### Rabin–Karp
- Rolling hash: `H(P)` compared to `H(T[i..i+m-1])` for each `i`, in `O(1)` per window.
- **True cost:** `O(n + m)` *hash operations*, but each is `Θ(w)` machine words, and **collisions** cost `Θ(m)` verification.
- Expected collisions with a random prime base and a `w`-bit modulus: `≈ n/m · (m/p)` ... precisely, the false-positive probability per window is `≈ 1/p` for a random prime `p`, so expected extra work is `Θ(n·m/p)` — negligible for `p ≫ nm`.
- **This is a Monte Carlo algorithm:** it can report a false match, never a false miss. Use double hashing or a `long` modulus to make the error probability ~`2⁻⁶⁴`.
- **Use when:** alphabet/pattern preprocessing must be tiny (streaming), or you need many searches against one pattern with hardware word hashing. Otherwise KMP is faster and exact.

### Z-algorithm
- `Z[i]` = length of the longest common prefix of `T` and `T[i..]`. Computed in `Θ(n)` using a rightmost-reaching "box" `[L, R]`.
- `Z[i] ≥ m` ⟺ pattern `P` occurs at `i` — so **KMP is a special case of the Z-algorithm**.
- Also gives: all occurrences of every suffix, longest common prefix of any two suffixes, palindrome detection in `Θ(n)` (Manacher's algorithm is the even/odd variant), and period detection.

### Aho–Corasick
- Build a **trie** of all patterns; compute failure links via BFS so every node's failure link points to its longest proper suffix that is also a trie prefix.
- Scan the text once, following goto/failure transitions; report every pattern ending at each position (via an "output link" chain).
- `Θ(Σ|Pᵢ| + n)` for `k` patterns.
- **Space:** `Θ(σ · Σ|Pᵢ|)` with a dense goto table (`σ` = alphabet size). With a sparse map it is `Θ(Σ|Pᵢ|)` but with worse constants.
- **Real uses:** grep-like search, content filtering, virus scanning, intrusiveness detection, tokenizer generation, keyword highlighting.

### Sunday / Quick Search
- Simplest practical member of the BM family: on mismatch at `P[j]` vs `T[i+m]`, shift so that `T[i+m]` aligns with its last occurrence in `P`.
- `Θ(n)` average, `Θ(nm)` worst, but the code is 20 lines and it beats KMP on realistic ASCII text.

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/string-search/` | All algorithms + failure functions |
| `src/test/java/com/alglab/string-search/` | Cross-validation fuzz tests |
| `SOLUTION/` | Worked solutions |
| `TESTS/` | Adversarial patterns (`aaaa...`, Fibonacci words) |
| `BENCHMARK/` | Benchmarks vs `String.indexOf` |
| `MINI_PROJECT/` | Pattern-match visualiser with failure-function overlay |
| `REAL_WORLD_PROJECT/` | Multi-keyword content filter |
| `CHALLENGE/` | Parallel Aho–Corasick, compressed automata |
| `DIAGRAMS/` | Failure-link diagrams, BM skip tables |