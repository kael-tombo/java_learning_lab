# Exercises — Matrix Chain & String DP

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.intervaldp`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Compute the matrix-chain example yourself

**Do the arithmetic by hand before coding.** Dimensions `(10, 100, 5, 50)`. Fill the table for all 5 parenthesisations of 4 matrices:

| parenthesisation | step costs | total |
|------------------|-----------|-------|
| `(((A1A2)A3)A4)` | | |
| `((A1(A2A3))A4)` | | |
| `((A1A2)(A3A4))` | | |
| `(A1((A2A3)A4))` | | |
| `(A1(A2(A3A4)))` | | |

**Then:**
1. Verify your DP returns the minimum.
2. Verify a greedy rule and measure its ratio. Try at least three: "cheapest single product first", "smallest output dimension first", "largest shared dimension first".
3. Construct the 3-matrix counterexample `(30×10, 10×60, 60×30)` and confirm both tie-breaks give the worse answer.

**Fill the `cost` table by hand** for `(10, 100, 5, 50)`:

| | A1 | A2 | A3 | A4 |
|---|---|---|---|---|
| A1 | 0 | | | |
| A2 | | 0 | | |
| A3 | | | 0 | |
| A4 | | | | 0 |

Then answer: **why does greedy have no chance here?** (One paragraph: the cost of a split `k` is `d[i-1]·d[k]·d[j]`, which depends on `i`, `k`, **and** `j` simultaneously; the decision at one level constrains all others, so no local rule is correct.)

---

## Exercise 2 — Fill order matters

Implement matrix chain four ways and find the smallest failing input for each:

| variant | order |
|---------|-------|
| A (correct) | increasing interval length |
| B | `i` ascending, `j` ascending |
| C | `i` descending, `j` ascending |
| D | `i` ascending, `j` descending |

For each, report: does it produce the right answer, `INF`, or a plausible wrong number? **Variant C is the interesting one** — it may be correct, in which case explain why by checking whether both sub-intervals are ready.

Then: **prove** C correct or find its counterexample. (C works iff both `dp[i][k]` and `dp[k+1][j]` are ready: `dp[i][k]` needs same `i`, smaller `j` — j ascending gives that; `dp[k+1][j]` needs larger `i` — i descending gives that. **So C is correct.** The lesson: two orders work, one does not, and the reason is about which axes each sub-interval differs in.)

---

## Exercise 3 — Palindrome partitioning

Trace `minCuts("aab")` by hand:

| `i` | `pal[?][i-1]` candidates | `dp[i]` |
|-----|------------------------|---------|
| 0 | — | `0` |
| 1 | `pal[0][0]="a"` ✔ ⇒ `dp[0]+1 = 1` | `1` |
| 2 | `pal[0][1]="aa"` ✔ ⇒ `1`; `pal[1][1]="a"` ✔ ⇒ `dp[1]+1 = 2` | `1` |
| 3 | `pal[0][2]="aab"` ✘; `pal[1][2]="ab"` ✘; `pal[2][2]="b"` ✔ ⇒ `dp[2]+1 = 2` | `2` |

**Answer: 1 cut** (`"aa|b"`). Verify with code.

Then implement and validate:
- `minCuts` (`Θ(n²)` space)
- `minCutsO1Space` (centre expansion, `Θ(n)` space)
- `countPartitions` (number of minimal-partition ways) — `Θ(n²)`
- `countPalindromicSubstrings` — `Θ(n²)`, but there is an `Θ(n)` Manacher solution. **Implement Manacher and report the speedup at `n = 10⁶` on `"aaaa…a"`** (the worst case: `n(n+1)/2 = 5·10¹¹` palindromes for the `Θ(n²)` version).

**Answer in writing:** why is `Θ(n²)` the natural bound for palindrome partitioning, and what does the `pal` precomputation buy?

---

## Exercise 4 — Word break: three implementations, three complexities

Implement and time:
1. `HashSet` + `substring` — expect `Θ(n³)`
2. Trie walk — expect `Θ(n·L)`
3. **Aho–Corasick** — expect `Θ(S + n + matches)`

Benchmark for `n = 10⁴` with dictionaries of size `{10, 10³, 10⁴}` and mean word length 8.

**Then:**
1. Verify all three agree on 10 000 random cases.
2. Find the input where the naive version is worst: `n = 2000` all `a`, dictionary `{a, aa, ..., a^10}`.
3. Implement "all segmentations" and verify `countSeg("a"×40, {a,aa,aaa,aaaa}) == 2^39`. **Then add a cap and explain why a production implementation MUST cap it** (DoS via a short adversarial input).

**Answer:** why is Aho–Corasick the "right" algorithm here, and what property of word break makes it applicable?

---

## Exercise 5 — RNA folding, traced

Trace `maxPairs` for `"GGGACCC"` by hand. Fill the interval table:

```
        G  G  G  A  C  C  C
    G   0  1  1  0  0  0  0
    G      0  1  1  0  0  0
    G         0  1  1  0  0
    A            0  0  0  0
    C               0  0  0
    C                  0  0
    C                     0
```

**Verify the answer is 2** (`G(0)-C(6)` and `G(1)-C(5)`, or `G(0)-C(5)` and `G(1)-C(6)`... compute which is legal).

**Then:**
- Implement a brute-force over all pairings for `n ≤ 12` and validate.
- Benchmark for `n ∈ {100, 500, 1000, 2000}` and find the practical limit.
- **Answer:** real RNA is `n = 10³–10⁵`. ViennaRNA reports `Θ(n³)` with SIMD at `n ≈ 10⁴` in minutes. What are the three techniques that make that possible, and which of them is available in Java?

---

## Exercise 6 — Burst balloons = matrix chain

Implement `burst(int[])` (LeetCode 312) and validate against brute force for `n ≤ 8`.

**Then write one paragraph** proving burst balloons and matrix chain are the same algorithm shape: same `Θ(n²)` interval states, same `Θ(n)` split transition, different combine function and boundary handling.

**Bonus:** LeetCode 1031 (matrix chain) and 312 (burst balloons) and 1130 (min cost from leaf values) — implement the third and show it is also the same shape.

---

## Exercise 7 — The Penney game (CHALLENGE)

Implement:
1. `stringDistance(X, Y)` with `delete = insert = 1`, `substitute = |x − y|` — `Θ(|X||Y|)`.
2. `overlapMatrix(X, Y)` — `Θ(n²m²)`.
3. Given the overlap matrix, the winning probability for B against A's string `X`, solved from a linear system (`Θ(n³)` Gaussian elimination).

Then compute the equilibrium for a binary alphabet (`{H, T}`) with string length 4, exhaustively over all 16 strings. Verify:
- **(H)** beats **(TTTH)** in ~7/8 of the time.
- **(THHH)** beats **(HHHT)** in ~7/8 of the time.

**Then:** verify Conway's theorem — for each length `L`, the optimal string has the form `HRRRRR…R`. Check `L = 2, 3, 4`.

**Finally answer:** what would it mean if the alphabet had more than two symbols? (The theorem still holds; the choice of `H` is the best-response symbol, and the game-theoretic content is the *timing*, not the *symbols*.)

---

## Exercise 8 — Debugging drills

1. Matrix chain with `d[i] * d[k] * d[j]` instead of `d[i] * d[k+1] * d[j+1]` — find a failing instance.
2. Matrix chain with `int` instead of `long` — construct the overflow.
3. Matrix chain with `cost[i][k] + cost[k+1][j]` where `k+1 == j` reads `cost[j][j]` = 0 ✔. Now break the indexing (`cost[k][j-1]`) — find the failing instance.
4. `pal` computed with `i` ascending — what does `minCuts` return for `"abababa"`?
5. `minCuts` returning `dp[n]` instead of `dp[n]-1` — off by one; which input exposes it? (`n = 1`.)
6. Word break with `can[0] = false` — what happens? (`Nothing can be built; returns `false` even for an empty string with an empty dict.)
7. Word break `substring` in the inner loop — confirm `Θ(n³)` by measuring at `n = 500, 1000, 2000`.
8. RNA `dp[i+1][k-1]` with `k == i` (loop `k < j` instead of `k <= j-2`) — what happens?
9. Burst balloons with `nums[k]` not guarded for `k == n` — `ArrayIndexOutOfBoundsException`; but with the sentinel `1` at both ends it works. **Explain why the sentinel version is cleaner.**
10. `overlapMatrix` with `int` distances and long strings — overflow at what length?

---

## Exercise 9 — Deliverable

`MINI_PROJECT/MatrixChainViz.java`:
- Print the `cost` table.
- Print the split tree recursively with the multiplication counts at each node.
- Compare against the Catalan enumeration for `n ≤ 8` and print both.

Then `BENCHMARK/IntervalRace.java` producing a markdown table: matrix chain / polygon triangulation / burst balloons / palindrome partitioning (`Θ(n²)` and `Θ(n)` space) / word break (three implementations) / RNA Nussinov — across `n ∈ {100, 500, 1000, 2000}`.

**Answer in writing:** for each algorithm, state whether the `Θ(n³)` wall was hit, at what `n`, and what the engineering response would be (specialise? parallelise? approximate? give up and declare NP-hard? — note that none of these are NP-hard, so "give up" is never right here; the answer is always "exploit the structure", which is lab `08`'s topic).