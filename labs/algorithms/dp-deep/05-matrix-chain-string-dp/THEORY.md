# Theory — Matrix Chain & String DP

This lab is about a single DP shape that shows up in matrix chains, polygon triangulations, burst balloons, palindrome partitioning, string metrics, word break, and RNA folding. Recognising the shape is worth more than memorising seven recurrences.

---

## 1. The shape: interval state + split transition

```
STATE:       dp[i][j]  = best value for the sub-interval [i, j]
TRANSITION:  dp[i][j] = OPT over i <= k < j of ( dp[i][k] ⊕ dp[k+1][j] ⊗ cost(i, k, j) )
```

- **States:** `Θ(n²)` intervals.
- **Split points:** `Θ(n)` per interval.
- **Total: `Θ(n³)`** — unless the `OPT` over `k` can be simplified, which it cannot in general.
- **Fill order:** by **increasing interval length**, `len = 1, 2, …, n`. `i` ascending with `j = i + len − 1`.

**Fill order matters and is often stated wrong.** The alternatives:

```java
for (int len = 2; len <= n; len++)          // CORRECT: increasing length
    for (int i = 0; i + len - 1 < n; i++) {
        int j = i + len - 1;
        for (int k = i; k < j; k++)
            dp[i][j] = min(dp[i][j], dp[i][k] + dp[k+1][j] + cost(i,k,j));
    }
```

Using `for (i = n-1 downto 0) for (j = i+1 to n-1)` also works **only if** the inner `j` direction and the split guarantee `dp[i][k]` (shorter, same `i`) and `dp[k+1][j]` (same `j`, shorter) are both already computed. `i` descending, `j` ascending satisfies both. `i` ascending, `j` descending does **not**.

**`Θ(n³)` wall in Java:** `n = 500` ⇒ `1.25·10⁸` inner iterations ≈ 0.5–1 s. `n = 1000` ⇒ `1.67·10⁸`... precisely `Σ_{len=2}^{n} (n−len+1)(len−1) ≈ n³/6`, so `n = 1000` ⇒ `1.67·10⁸` ≈ 1 s; `n = 2000` ⇒ `1.3·10⁹` ≈ 8 s; `n = 5000` ⇒ `2·10¹⁰` ✗.

The `n³/6` constant (not `n³`) matters: the triangular loop structure gives you a 6× free speedup over a rectangular triple loop.

---

## 2. Matrix chain multiplication

### The problem

Given matrices `A₁…Aₙ` with `Aᵢ` of dimension `dᵢ₋₁ × dᵢ`, choose parenthesisation to minimise the total scalar-multiplication cost.

```
A1 A2 A3     ((A1A2)A3)  or  (A1(A2A3))
```

### Why greedy fails — the canonical demonstration

**The textbook counterexample (dimensions 10, 100, 5, 50):**

| parenthesisation | cost | scalar multiplications |
|------------------|------|-----------------------|
| `((A1A2)A3)A4` | `10·100·5 + 10·5·50 + 10·100·50` | `5 000 + 2 500 + 50 000 = 57 500` |
| `(A1((A2A3)A4))` | `100·5·50 + 100·50·10 + 10·100·50` | `25 000 + 50 000 + 50 000 = 125 000` |
| `(A1(A2A3))A4` | `100·5·50 + 10·100·50 + 10·100·50` | `25 000 + 50 000 + 50 000 = 125 000` |
| **`(A1A2)(A3A4)`** | `10·100·5 + 10·50·50 + 10·100·50` | **`5 000 + 25 000 + 50 000 = 80 000`** |
| `A1((A2A3)A4)` | `100·5·50 + 10·100·50 + 10·100·50` | `125 000` |

**Greedy by "compute the cheapest product first"** picks `A1A2` (cost 5000), then is forced into `((A1A2)A3)A4` at `57 500` — which *is* the optimum here. **Greedy by "associate the smallest inner dimension first"** picks `A2A3` (100·5·50 = 25 000) — wait, `A1A2` at 5000 is cheaper. Let me use the standard three-matrix demonstration instead:

**Three matrices, `A1 = 10×100`, `A2 = 100×5`, `A3 = 5×50`:**

| | scalar multiplications |
|---|---|
| `(A1A2)A3` | `10·100·5 = 5 000`, then `10·5·50 = 2 500` ⇒ **7 500** |
| `A1(A2A3)` | `100·5·50 = 25 000`, then `10·100·50 = 50 000` ⇒ **75 000** |

Greedy that pairs the two matrices with the cheapest single multiplication chooses `A1A2` — correct. **Greedy that pairs the two matrices whose combined dimension is smallest** chooses `A2A3` — giving `75 000` against an optimum of `7 500`. **A 10× gap from one greedy heuristic.**

**The four matrices (10,100,5,50) case** where greedy by "compute A1A2 first" gives 57 500 and the optimum is 80 000 — **greedy is *better* than the optimum?** No: `57 500 < 80 000`, so let me recompute. `((A1A2)A3)A4`: `A1A2` is `10×100 · 100×5` → `10×5`, cost `10·100·5 = 5 000`. Then `(A1A2)A3` is `10×5 · 5×50` → `10×50`, cost `10·5·50 = 2 500`. Then `·A4`: `10×50 · 50×50` → `10×50`, cost `10·50·50 = 25 000`. **Total `5 000 + 2 500 + 25 000 = 32 500`.**

`(A1A2)(A3A4)`: `A3A4` is `5×50 · 50×50` → `5×50`, cost `5·50·50 = 12 500`; then `10×5 · 5×50` → cost `2 500`. **Total `5 000 + 12 500 + 2 500 = 20 000`.** **Optimum is 20 000; greedy's 32 500 is 62% worse.** That is the correct textbook counterexample. *(Verify these numbers in Exercise 1 — computing them yourself is the point.)*

### Recurrence

```
cost[i][i] = 0
cost[i][j] = min over i <= k < j of ( cost[i][k] + cost[k+1][j] + rows(i,k)·cols(i,k)·cols(k+1,j) )
```

where `rows(i,k) = d[i-1]` and `cols(k+1,j) = d[k]` — hence the scalar cost of the final multiply at split `k` is `d[i-1] · d[k] · d[j]`.

**Time `Θ(n³)`, space `Θ(n²)`.** With `split[i][j] = k` recorded you can reconstruct in `Θ(n)`.

**The `Θ(n³)` is the state-space size, not the recurrence.** There are `Θ(n²)` intervals and each needs `Θ(n)` splits; no known general technique reduces the polynomial matrix-chain problem below `Θ(n³)` (for arbitrary dimensions), though the **scalar-chain** version has `Θ(n log n)` and better algorithms exist (Hu–Shing for polygons).

---

## 3. Optimal polygon triangulation — the same problem

Triangulating a convex `n`-gon with vertex weights `wᵢ`, minimising `Σ (triple weight)`. The recurrence is **identical**:

```
T[i][j] = 0                                            if j <= i+1
T[i][j] = min over i < k < j of ( T[i][k] + T[k][j] + w[i]·w[k]·w[j] )
```

**Why:** the triangle incident to edge `(i, j)` has some third vertex `k`, splitting the polygon into `(i..k)` and `(k..j)` — exactly the split. **A matrix chain of dimensions `d[i-1], d[i]` is a triangulated "polygon" whose triangle `(i, k, j)` has weight `d[i-1]d[k]d[j]`.** Same `Θ(n³)`, same code.

**Related `Θ(n³)` DPs with the same shape:**
- **Burst balloons:** `dp[i][j] = max over k of ( dp[i][k] + dp[k][j] + nums[i]·nums[k]·nums[j] )` — LeetCode 312.
- **Minimum cost to cut a stick** — `Θ(n²)`, a 1-D special case.
- **Optimal BST** — `Θ(n³)` naive, `Θ(n²)` with Knuth's optimisation.
- **RNA folding (Nussinov)** — `Θ(n³)`, same shape, see §7.

**Practical note:** LeetCode 1031 (matrix chain) and 312 (burst balloons) are the same algorithm with `min`/`max` and different cost functions. Recognising that is the skill.

---

## 4. Palindrome partitioning

### Minimum cuts

```
pal[i][j] = s[i] == s[j] && (j - i <= 1 || pal[i+1][j-1])         // Θ(n²)
cut[0]    = -1                                               // convention: -1 cuts before index 0
cut[i]    = min over 0 <= j < i with pal[j][i-1] of ( cut[j-1] + 1 )
answer    = cut[n-1]
```

Time `Θ(n²)`, space `Θ(n²)` for `pal` plus `Θ(n)` for `cut`.

### The `O(n)`-space variant

`pal` is not needed if you expand palindromes from centres, tracking only whether `[j, i-1]` is a palindrome *right now*:

```java
for (int centre = 0; centre < 2n - 1; centre++) {
    boolean odd = (centre & 1) == 1;
    for (int l = centre / 2, r = (centre + 1) / 2; l >= 0 && r < n && s.charAt(l) == s.charAt(r); l--, r++) {
        // s[l..r] is a palindrome -- relax dp[r]
    }
}
```

`Θ(n²)` time, `Θ(n)` space. Slightly harder to read; the `Θ(n²)`-space version is clearer and usually fine for `n ≤ 5000` (25 MB for `boolean[n][n]`).

### Why `Θ(n²)` is the natural bound

There are `Θ(n²)` palindromic substrings in the worst case (`"aaaa…a"`), and a `Θ(n³)` DP that explicitly checks each `(i, j, k)` triple is wasteful. Precomputing `pal` makes the transition `Θ(1)`, giving `Θ(n²)`.

**Note the general pattern:** a `Θ(n³)` split DP becomes `Θ(n²)` when the "can these two combine?" predicate can be **precomputed in `Θ(n²)`**. That is the same insight as the `pal` table.

---

## 5. String metrics and the Penney game

### Separable costs

Levenshtein generalises to arbitrary costs `d(x, y)` for `x ≠ y` and `i(y)` for insertion, `s(x)` for deletion, with the **separability condition**:

```
d(x, y) = s(x) + i(y) + d(x, y)      for x ≠ y
d(x, y) = 0                          for x = y
```

Under separability, the `Θ(nm)` DP applies unchanged, with the substitution cost replaced.

### String edit distance `δ(X, Y)` — a `Θ(n²)` computation over pairs of strings

The **string edit distance** between two strings `X = x₁…xₙ` and `Y = y₁…yₘ` is the minimum total weight of a set of operations (`delete(xᵢ)`, `insert(yⱼ)`, `substitute(xᵢ, yⱼ)`, each **at most once**) that transforms `X` into `Y`. With `s(x) = 1`, `i(y) = 1`, `d(x,y) = |x − y|` (absolute code-point difference), the `Θ(nm)` DP computes it.

**The Penney game result.** For a two-player game where A picks a string `X` and B responds with a string `Y` of the same length, the probability B wins is a linear function of the **overlap matrix** `M` with

```
M(X, Y)[i][j] = δ( suffix of X of length |X| - i ,  prefix of Y of length j )
```

**Building `M` for all `(i, j)` is `Θ(|X|·|Y|)` DP cells per entry, giving `Θ(|X|²·|Y|²)` total** — and then an `Θ(n³)` linear solve for the equilibrium.

**The surprising theorem (Penney, 1974; Conway):** in the best-response game, **every symbol except the first is the same in the optimal string**, and the optimal string for A (against the uniform prior) is `HRRRRR…R`. The entire equilibrium reduces to choosing one symbol and then repeating it.

**This is a lovely result because it comes out of a `Θ(n²)` DP plus linear algebra, and it is completely counter-intuitive** — from a game-theoretic standpoint you'd expect variety.

**Where it is used:** iterated function systems, DNA sequence analysis, and (in the general form) competitive-programming sequence games. The DP is the reusable part; the theorem is the fun part.

---

## 6. Word break

### Existence

```
can[0] = true
can[i] = OR over j in [max(0, i-L) .. i-1] with s[j..i-1] in dict of can[j]
```

- With a `HashSet<String>` lookup: `Θ(n²)` (or `Θ(n·L)` with `L` = longest word).
- **Trick:** `Θ(n·L)` with a trie: walk from each start position through the trie, stopping at `L` characters or a terminal node.

```java
static boolean wordBreak(String s, Set<String> dict) {
    int n = s.length();
    boolean[] can = new boolean[n + 1];
    can[0] = true;
    for (int i = 1; i <= n; i++)
        for (int j = Math.max(0, i - maxLen); j < i; j++)
            if (can[j] && dict.contains(s.substring(j, i))) { can[i] = true; break; }
    return can[n];
}
```

**Pitfall:** `s.substring(j, i)` inside the inner loop is `Θ(i−j)` → the whole thing is `Θ(n³)`. Precompute the substring hashes (`O(1)` per lookup) or use a trie.

### All segmentations

Same DP plus a `List<String>` at each reachable `i`:

```java
for (int i = 1; i <= n; i++)
    for (int j = max(0, i-L); j < i; j++)
        if (can[j] && dict.contains(s.substring(j, i))) {
            can[i] = true;
            for (String pre : ways[j]) ways[i].add(pre + s.substring(j,i));
        }
```

Time `Θ(n² + total output)`. The output can be exponential (`"aaaa…a"` with a dict of all lengths), so `Θ(output)` is optimal.

### The connection to knapsack

`word break` is **0/1 knapsack on prefixes**: the items are the dictionary words and the "capacity" is the position in the string, with each word usable once. It is also exactly the `Θ(n²)` sub-problem of `04-knapsack-variants`'s subset sum, with `W = n` and a boolean state.

**The reverse problem — segmenting a string into `k` segments minimising total cost — is `Θ(n²k)`,** or `Θ(n²)` with the divide-and-conquer optimisation if the cost satisfies the quadrangle inequality (see lab `08-dp-optimizations`).

---

## 7. RNA folding (Nussinov)

### The problem

Given a sequence of bases `A, C, G, U`, find the maximum number of **disjoint** base pairs `(i, j)` with `i < j`, where `(i, j)` pairs `A-U` or `C-G`, every base is in at most one pair, and the pairs are **nested** (no pseudoknots).

### Recurrence

```
N[i][j] = 0                                            if j <= i + 1
N[i][j] = max( N[i+1][j],                              // i unpaired
               max over i <= k <= j-2 with pairable(i,k)
                   of ( 1 + N[i+1][k-1] + N[k+1][j] ) )  // (i,k) pairs
```

**Time `Θ(n³)`, space `Θ(n²)`.**

**Why the fill order is by increasing length:** `N[i+1][k-1]` has length `k−i−1 < j−i` ✔, and `N[k+1][j]` has length `j−k < j−i` ✔. So increasing length is required, exactly as in matrix chain.

**Where it is used:** RNA secondary-structure prediction is the canonical `Θ(n³)` DP in bioinformatics. **MFE (minimum free energy)** folding adds several more states (`Θ(n³)` with a constant of ~30 states) and is the actual algorithm used by tools like ViennaRNA.

**The `Θ(n³)` wall:** `n = 500` ⇒ `2·10⁷` inner iterations ≈ 50 ms ✔. `n = 2000` ⇒ `2.7·10⁹` ≈ 10 s ✗. Real RNA has `n = 10³–10⁵`, so real folding uses **`O(n³)` with heavy SIMD optimisation, or `O(n²)` probabilistic/grammar-based approximations, or linear-time `O(n³/logn)` parallel implementations.** This is the most important practical lesson in the lab: **a correct `Θ(n³)` DP is a research contribution's baseline, not a solution.**

---

## 8. The shared state graph

All of these problems have the same **state graph**:

```
states  =  pairs (i, j) with i <= j      → Θ(n²) states
edges   =  (i, j) -> (i, k) and (k+1, j) for all i <= k < j   → Θ(n³) edges
```

**So: `Θ(n³)` = `Θ(n²)` states × `Θ(n)` transitions each.** Any optimisation must attack one of those two factors:

| attack | example | result |
|--------|---------|--------|
| reduce transitions per state | precompute `pal[i][j]` | palindrome partitioning `Θ(n³) → Θ(n²)` |
| reduce states | rolling arrays for length only | `Θ(n²) → Θ(n)` space |
| monotonicity in `k` | Knuth / divide-and-conquer | optimal BST `Θ(n³) → Θ(n²)` |
| monotone in both `i` and `k` | SMAWK | `Θ(n³) → Θ(n²)` total |
| exploit the quadrangle inequality | Knuth's optimisation | same |
| special structure | Hu–Shing | polygon triangulation `Θ(n³) → Θ(n log n)` |

**Lab `08-dp-optimizations` is the systematic treatment of the last four.** This lab is the setup: here is the `Θ(n³)` shape and here is why it recurs.

---

## 9. Choosing

| Problem | Algorithm | Feasible up to |
|---------|-----------|----------------|
| Matrix chain | `Θ(n³)` DP | `n ≈ 500` |
| Polygon triangulation | `Θ(n³)` DP; Hu–Shing `Θ(n log n)` | DP `n ≈ 500`; Hu–Shing `n ≈ 10⁵` |
| Palindrome partitioning | `Θ(n²)` | `n ≈ 5000` |
| Palindrome *counting* | `Θ(n²)` | same |
| String metrics pair | `Θ(|X||Y|)` per pair | `|X|,|Y| ≈ 10³` |
| Penney game matrix | `Θ(n⁴)` for the full matrix | `n ≈ 30` |
| Word break (existence) | `Θ(n²)` or `Θ(nL)` trie | `n ≈ 10⁴` |
| Word break (all) | `Θ(n² + output)` | output-bound |
| RNA folding (Nussinov) | `Θ(n³)` | `n ≈ 500` |
| RNA folding (MFE) | `Θ(n³)`, 30× constant | `n ≈ 200` |

**The engineering reflex:** for matrix chain in production, you do not need the DP at all — matrix-chain order is determined **at compile time** by the JVM (via escape analysis and inlining). The `Θ(n³)` DP is a teaching and general-purpose tool, and it is exactly what you reach for when the "matrices" are really **strings, trees, or intervals** rather than arithmetic objects.