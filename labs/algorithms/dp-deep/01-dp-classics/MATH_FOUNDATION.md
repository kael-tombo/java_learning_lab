# Math Foundation — DP Classics

The recurrence theory: characteristic equations, the overlapping-subproblem count, the amortised accounting for rolling arrays, and the `Θ(n·k)` shape.

---

## 1. Solving linear recurrences

### 1.1 Characteristic equation method

For `T(n) = a·T(n-1) + b·T(n-2) + Θ(1)`:

```
Assume T(n) = r^n.  Then  r^n = a r^(n-1) + b r^(n-2)
⟹ r² = a r + b  ⟹  r = (a ± √(a² + 4b)) / 2
T(n) = Θ(r^n)
```

**Fibonacci:** `a = b = 1` ⇒ `r = (1+√5)/2 = φ ≈ 1.618`.

| `n` | `φⁿ` | naive `fib(n)` calls |
|-----|------|----------------------|
| 10 | 123 | 177 |
| 20 | 15 127 | 21 845 |
| 30 | 1 860 498 | 2 692 601 |
| 40 | 228 826 127 | 331 160 981 |
| 50 | 28 143 753 123 | 40 730 022 147 |
| 60 | 3 461 972 553 985 | ~1.55·10¹² |
| 70 | 4.26·10¹⁴ | ~1.9·10¹⁴ (int overflows) |

**Ratio between consecutive naive values:** `φ ≈ 1.618`. Each increment of `n` multiplies the cost by 1.618 — that is *the* signature of exponential DP recursion.

### 1.2 Memoisation: counting distinct states

Let `D(n)` = number of **distinct** states reachable from the initial state.

```
Naive:      T(n) = 2T(n-1) + Θ(1)          = Θ(φⁿ)
Memoised:   M(n) = 1 + Σ M(i) for i < n     = Θ(n)
```

The memoised cost is exactly `D(n)`, because each state is computed once. For Fibonacci, `D(n) = n+1`.

**General statement:** memoising a recursion with `D` distinct subproblems yields `Θ(D + total work per state)`. The exponential blow-up was never real complexity — it was **repeated evaluation of the same value**.

### 1.3 Master theorem cross-check

For a "divide into two equal halves, combine in `Θ(1)`" recursion (binary-tree problems):

```
a = 2, b = 2, f(n) = Θ(1)     n^(log_b a) = n^1 = n
Case 1:  f(n) = Θ(n^0) < Θ(n^1)   ⟹  T(n) = Θ(n)   ✓ matches M(n) = Θ(n)
```

---

## 2. Why the DP must be acyclic

The evaluation order exists iff the dependency graph `G = (states, edges i → j)` has no cycles.

**Proof sketch.** A topological order exists iff the graph is a DAG (standard). A cycle `i → j → i` would mean `dp[i]` depends on `dp[j]` and vice versa — there is no value to compute first, so the system is not well-founded.

**Cycle-free is not enough — the order must be respected.** Consider:

```
dp[i] = dp[i - 1] + dp[i - 2]        fill order: i ascending
```

If you filled `i` **descending**, `dp[i-1]` and `dp[i-2]` would hold stale initial values (e.g. `0`), and the answer would be 0 or garbage. The order is part of the specification.

**The unbounded-knapsack subtlety:**

```
for (int w = 1; w <= W; w++)                 # capacities ASCENDING
    for (int item = 0; item < n; item++)
        dp[w] = max(dp[w], dp[w - item.weight] + item.value)
```

Ascending `w` means `dp[w - item.weight]` has already been updated with `item`, so `item` can be used **repeatedly**. That is the *unbounded* variant and it is what you want for coin change.

Descending `w` gives the *0/1* variant (each item at most once). **Using the wrong order is not a crash — it is a silently different problem.**

---

## 3. Space: rolling arrays and the amortised argument

### Cost of a `k`-window recurrence

```
dp[i] = max { dp[i - j] + c[j] : j = 1..k }      time Θ(nk), space Θ(n)
```

Rolling to a circular buffer of size `k`:

```
space  Θ(k)      time Θ(nk)      (unchanged — the buffer is written n times)
```

The **time is unchanged**; only memory moves. The break-even:

```
Total memory traffic:
   full array:  n writes + n reads of 4 bytes                     = 8n bytes
   buffer:      n writes + n reads of 4 bytes                     = 8n bytes
   IDENTICAL
```

**So rolling arrays do not reduce memory traffic at all for a linear scan** — they only reduce *peak* footprint, which matters for cache residency only if the whole array exceeds L2/L3:

| `n` (ints) | array size | exceeds L2 (1 MB)? | exceeds L3 (8 MB)? | rolling helps? |
|-----------|-----------|--------------------|--------------------|----------------|
| 10³ | 4 KB | no | no | **no** — slower |
| 10⁵ | 400 KB | no | no | **no** |
| 10⁶ | 4 MB | yes | no | **no** — still fits L3 |
| 10⁷ | 40 MB | yes | yes | **yes**, measurably |
| 10⁸ | 400 MB | yes | yes | **yes**, ~30–50% |

**This is the honest answer about space optimisation, and it is worth knowing before you spend an afternoon on it:** rolling arrays only pay above ~10⁷ elements in Java.

### In-place update legality

An in-place update `dp[i] = f(dp[...], dp[i-1], dp[i-2], ...)` is legal **iff every read index is `< i` AND the reads happen before the write**. For Fibonacci, `dp[i] = dp[i-1] + dp[i-2]` satisfies both.

**Counter-example where in-place fails:**

```
dp[i] = max over j in {i-1, i-2, i-3} of dp[i-j] + val[j]     window size 3
```

In-place: at `i = 3` we write `dp[3]`, which is also `dp[i]` for `i=3`; reads are `dp[2], dp[1], dp[0]` — fine. But if a transition ever reads `dp[i + something]` (an unbounded coin change reads `dp[i-c]` with `c > 0`, always `< i`) — also fine.

**In-place fails when the fill order is not the index order**, e.g. coin-change-by-coins:

```
for item in items:            # outer loop is ITEMS
    for w = 1..W:             # ASCENDING: dp[w] reads dp[w-weight] already updated for THIS item
        dp[w] = max(dp[w], dp[w - weight] + value)
```

This is still in-place and correct because the read index `w - weight < w` is already final *for this item*. **The rule is always the same: no state may be read before it is final for the current outer-loop iteration.**

---

## 4. The `Θ(n·k)` shape, quantified

```
      states
    ┌─────────────────────────────
  0 │  base
    │
    │   ── choice j=0 ──> dp[i] ──> dp[i]
  i │   ── choice j=1 ──>
    │   ── choice j=k ──>
    └─────────────────────────────
```

| Problem | `n` | `k` | Total | Memory |
|---------|-----|-----|-------|--------|
| Unbounded coin change | max amount | #coins | `Θ(nk)` | `Θ(n)` |
| Coin-change ways | max amount | #coins | `Θ(nk)` | `Θ(n)` |
| 0/1 knapsack | #items | capacity `W` | `Θ(nW)` | `Θ(W)` |
| LCS | `|A|` | `|B|` | `Θ(nm)` | `Θ(min(n,m))` rolled |
| Edit distance | `|A|` | `|B|` | `Θ(nm)` | `Θ(min(n,m))` rolled |
| Rod cutting | max length | max length | `Θ(n²)` | `Θ(n)` |
| Matrix chain | #matrices | #matrices | `Θ(n³)` | `Θ(n²)` |
| LIS (naive) | `n` | `n` | `Θ(n²)` | `Θ(n)` |
| LIS (binary search) | `n` | `log n` | `Θ(n log n)` | `Θ(n)` |
| Tree DP | #nodes | #states per node | `Θ(nk)` | `Θ(hk)` |

**Every optimisation in lab `08-dp-optimizations` reduces `k`:**
- Divide and conquer optimisation: `k` from `n` → `log n` or `O(1)`.
- Monotone queue / SMAWK: `k` from `n` → `O(1)` amortised.
- WQS / Aliens: removes a state dimension entirely.
- Bitset: `k` from `n` → `n/64`.

---

## 5. State-space counting (how big is the DP?)

Before implementing, count states:

| Problem | #states | #transitions per state | Total | Feasible? |
|---------|---------|----------------------|-------|-----------|
| `fib(n)`, `n = 10⁶` | `10⁶` | 2 | `2·10⁶` | ✓ |
| Coin change, `n = 10⁶`, `k = 8` | `10⁶` | 8 | `8·10⁶` | ✓ |
| 0/1 knapsack, `n = 1000`, `W = 10⁶` | `10⁶` | 1000 | `10⁹` | ✗ (3 s+) |
| Edit distance, `10⁴ × 10⁴` | `10⁸` | 3 | `3·10⁸` | ✗ (memory) |
| Matrix chain, `n = 500` | `250 000` | `~n` | `1.25·10⁸` | ✓ (2 s) |
| LCS, `10⁵ × 10⁵` | `10¹⁰` | 2 | — | ✗ (100 GB) |
| Held–Karp, `n = 20` | `2²⁰` | 20 | `2·10⁷` | ✓ (80 MB) |
| Held–Karp, `n = 30` | `2³⁰` | 30 | `3·10¹⁰` | ✗ |

**The state count is the feasibility test.** If `|states| > ~10⁸`, the DP table will not fit in a JVM heap (default ¼ of physical RAM; a byte DP at `10⁸` states = 100 MB, an `int` DP = 400 MB, a 2-D table with `n = 10⁴` per side = 400 MB).

---

## 6. Infeasibility and sentinels

**Reachability is part of the specification.** `dp[i] = +∞` means "state `i` is unreachable", and the transition must not add to `+∞` without care.

**Overflow arithmetic.** With `INF = Integer.MAX_VALUE`:

```
INF + 1  =  Integer.MIN_VALUE     (overflow)
```

So `Math.min(dp[i], dp[i-c] + 1)` with `dp[i-c] = INF` yields `MIN_VALUE`, i.e. "negative coins". Two correct fixes:

```
INF = Integer.MAX_VALUE / 2     =  1073741823
     INF + 1 is representable and stays huge
```

or an explicit reachability check:

```
if (dp[i - c] < INF) dp[i] = min(dp[i], dp[i - c] + 1)
```

**Never test `dp[i] == INF` for "unreachable" if you also store `-1` for "unreachable" elsewhere.** Pick one convention and use it in the tests too, or the tests will pass a broken implementation.

**For long DP:** `long INF = Long.MAX_VALUE / 4`. The same overflow applies at 2× the scale.

---

## 7. Complexity of the fill

If `dp[i]` is computed with a loop over `j = 1..i` (rod cutting, matrix chain), then

```
T(n) = Σ_{i=1}^{n} O(i)  =  O(n²/2)
```

not `O(n²)` — the constant is 1/2. For matrix chain:

```
T(n) = Σ_{len=2}^{n} (n-len+1) · O(len)
     ≈ O(n³/6)
```

**The `Θ(n²)` triangular fill is 2× cheaper than a naive rectangular fill.** Filling only the upper triangle (`j ≤ i`) and leaving the lower triangle untouched is both correct and measurably faster.

---

## 8. Optimal substructure: what it really means

**Definition.** A problem `P` has optimal substructure if every optimal solution of `P` is composed of optimal solutions of its subproblems. Formally: if `OPT(P) = ⋃ OPT(sub)`, then combining optimal subsolutions gives an optimal solution.

**Consequence.** The DP transition may assume each substate is optimally solved — it is, because we compute it optimally.

**Counter-example: longest common subsequence of a *string and its sorted form*.** Naively, `OPT(A, B)` with `B` sorted has optimal substructure. But the greedy algorithm "always match greedily when possible" **fails**, because the longest-common-subsequence subproblem of an *optimal* solution need not be a *longest* one. This is the classic distinction between:

- **Optimal substructure** (the DP property), and
- **The greedy-choice property** (which is stronger and is what greedy algorithms need).

**Also note:** the *shortest-path* problem has a subtlety — the shortest path from `s` to `t` might use a subpath that is a shortest path from `s` to `v`, but a *shortest path from `s` to `t` via `v`* needs the right `v`. Dijkstra works because weights are non-negative (Bellman–Ford works without that). See `07-dijkstra`.

---

## 9. Quick reference

| Quantity | Value |
|----------|-------|
| Fibonacci characteristic root | `φ = (1+√5)/2 ≈ 1.618` |
| Naive fib complexity | `Θ(φⁿ)` |
| Memoised fib | `Θ(n)` time, `Θ(n)` space, `O(1)` rolled |
| `fib` `int` overflow | `n ≥ 47` |
| `fib` `long` overflow | `n ≥ 93` |
| Distinct states, `fib(n)` | `n + 1` |
| Master theorem for memoised linear recurrence | `a=2, b=2, f=O(1)` → Case 1 → `Θ(n)` |
| Rolling-array break-even (ints) | `n ≳ 10⁷` (exceeds L3) |
| Rolling-array memory traffic | **unchanged** — only peak footprint drops |
| Safe `INF` for `int` DP | `Integer.MAX_VALUE / 2` |
| Triangular fill saving | `2×` on `Θ(n²)` DPs |
| DP feasibility limit | `|states| ≲ 10⁸` (byte DP) / `10⁷` (int DP) |
| Golden ratio closed form instability | past `n ≈ 70` in `double` |