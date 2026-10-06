# Math Foundation — Binary Search Variants

The halving recurrence, the exact iteration counts, the log-sum identities that power the compound searches, and the overflow arithmetic.

---

## 1. The recurrence

```
T(n) = T(n/2) + Θ(1),   T(1) = Θ(1)
```

Master theorem: `a = 1`, `b = 2`, `f(n) = 1`. `n^(log_b a) = n^(log₂1) = 1`. Since `f(n) = Θ(1) = Θ(1)`, this is **Case 2**:

```
T(n) = Θ( n^(log₂1) · log₂ n ) = Θ(log n)
```

**Binary search is Case 2 with `a = 1`.** That is the structural difference from merge sort: one subproblem, not two, so the per-level work `Θ(1)` accumulates over `log₂ n` levels.

---

## 2. Exact iteration count

Let `w_t = hi_t − lo_t` be the width before iteration `t`. Under `lo < hi` (half-open convention):

```
mid = lo + ⌊w/2⌋
if a[mid] < key:  lo = mid + 1   ⟹  w_{t+1} = hi − lo − 1 = w − ⌊w/2⌋ − 1 = ⌈w/2⌉ − 1
else:             hi = mid       ⟹  w_{t+1} = ⌊w/2⌋
```

Either way `w_{t+1} ≤ ⌈w_t/2⌉ − 1`. Iterating:

```
w_t  ≤  ⌈w_0 / 2^t⌉ − 1
```

Set `w_t = 0` (loop exit):

```
⌈n / 2^t⌉ = 1   ⟹   2^t ≥ n   ⟹   t = ⌈log₂ n⌉
```

**Checks:**

| `n` | `⌈log₂ n⌉` | manual count |
|-----|------------|--------------|
| 1 | 0 | 0 |
| 2 | 1 | 1 |
| 3 | 2 | 2 |
| 10 | 4 | 4 |
| 1 000 | 10 | 10 |
| 2²⁰ | 20 | 20 |
| 10⁶ | 20 | 20 |

**Best case** is `⌈log₂ n⌉ − 1` (target found at the last comparison) plus one successful test; **worst case** is exactly `⌈log₂ n⌉` failures. There is no asymptotic difference — the *worst case is the normal case*.

---

## 3. Information-theoretic optimality

Binary search asks one yes/no question per iteration: "is the answer ≤ `mid`?" With `R` possible answers, a binary decision tree needs depth `≥ log₂ R`. Binary search attains `⌈log₂ R⌉`.

```
Lower bound  = ⌈log₂ R⌉
Binary search = ⌈log₂ R⌉
Gap           = 0            ← binary search is EXACTLY optimal
```

This is why binary search is the gold standard for "find the threshold in a monotone predicate": no algorithm using only comparisons can do better.

---

## 4. Compound searches: the log-sum identity

Two problems in this lab have a `log` of a `log`. The identity that explains them:

```
log_a(b · c) = log_a b + log_a c
```

### 4.1 Binary search over a range of *indices* into an *array*

"Search a sorted array of size `n`" = "binary search over `[0, n-1]`" = `log₂ n` steps. One log.

### 4.2 Binary search **on the answer** where `f` itself costs `log n`

"Minimum `k` such that `countDistinct(k) ≥ k`", where `countDistinct(x)` is a sort of `x` elements costing `Θ(x log x)`.

```
Total = Θ( log R ) evaluations of f, each costing Θ( n log n )
      = Θ( log R · n log n )
```

**This is not a double logarithm** — it is a product of a log and the cost of the predicate. Confusion here is the source of most bad complexity claims in this area. `log R · log n` only arises when `f` itself is a `Θ(log n)` operation (e.g. a `Set.size()`-style binary search), which is rare.

### 4.3 The genuinely `Θ(log² n)` case: binary search over a *log-structured* space

Search a **balanced BST** of size `n`: `Θ(log n)`. Search it `k` times: `Θ(k log n)`. If instead you binary search a **sorted array of size `n` for each of `k` independently unsorted queries**, each query is `Θ(log n)`, total `Θ(k log n)`.

`Θ(log² n)` genuinely appears when you **binary search over `Θ(log n)` candidates, each requiring `Θ(log n)` to evaluate** — e.g. parametric search where each feasibility test is itself a binary search, or online convex hull point-location with `log log` outer and `log` inner. Worth naming so you recognise it; rare in practice.

### 4.4 The important identity for this lab: log-sum over passes

**Radix sort** (lab 04) uses the same identity in reverse:

```
w bits, d passes of k bits each:   d · k = w   ⟹   d = w/k = w / log₂ B
cost = d · (n + B) = (w / log₂ B)(n + B)
```

Different `log`, same algebra. The two labs are the same idea — *how many bits do you extract per operation* — from opposite directions.

---

## 5. Overflow arithmetic

The naive midpoint:

```
mid = (lo + hi) / 2        // overflows when lo + hi > Integer.MAX_VALUE
```

For 32-bit signed ints, `lo + hi` overflows iff `lo + hi > 2³¹ − 1 ≈ 2.147·10⁹`. Since each of `lo, hi` is a valid `int`, `lo + hi` can be as large as `2³² − 2`.

**Correct forms:**

```
mid = lo + (hi - lo) / 2                 // int-safe: (hi-lo) is in [0, MAX]
mid = lo + ((hi - lo) >>> 1)             // unsigned shift, same result for non-negative hi-lo
mid = (int)(((long) lo + hi) >>> 1)      // also safe; useful when the span exceeds int range
```

| `lo` | `hi` | `(lo+hi)/2` | `lo+(hi-lo)/2` |
|------|------|-------------|-----------------|
| 0 | 10 | 5 | 5 |
| 2³¹−11 | 2³¹−1 | **−2 147 483_638** (overflow) | 2 147 483_638 |

**Truncation trap:** for negative `(hi - lo)` Java's `/` truncates toward zero, so `(-3)/2 = -1` not `-2`. Using `>>>` on a negative value gives a *different* (also wrong for the intent) answer. Guard: never let `hi < lo` inside the midpoint expression.

**Where it actually bites:** index arithmetic over `long` ranges, external sort file offsets, and `int`-typed virtual memory offsets. It *cannot* happen with `int[]` indices because `n ≤ 2³¹ − 1` means `lo + hi ≤ 2n − 2` can still overflow for `n > 2³⁰`. **So it can happen even with plain arrays** if `n > 1_073_741_824`. Use the safe form everywhere.

---

## 6. Sentinel formulation (why `hi = n` is safe)

Convention B sets `hi = n`, which is **one past the last valid index**. Why can we compare `a[mid]` without checking `mid < n`?

Because `lo < hi` implies `mid = lo + ⌊(hi-lo)/2⌋ ≤ lo + (hi - lo - 1) = hi - 1 ≤ n - 1`. The sentinel never needs to be *dereferenced*; it only bounds the interval. This is what removes an entire class of `mid >= a.length` checks.

Compare with the alternative "sentinel element" technique in the classic Knuth formulation:

```
int i = 0, j = n;  while (i < j) ...   // j is a virtual +infinity
```

Both are correct; the half-open interval version has fewer special cases because `lo == hi` is the *only* exit state.

---

## 7. The upward-biased midpoint and its termination proof

For "smallest feasible `x`":

```
lo = 0; hi = R;
while (lo < hi) {
    mid = lo + (hi - lo + 1) / 2;      // UPWARD bias
    if (f(mid)) lo = mid; else hi = mid - 1;
}
```

**Termination proof.** Under `lo < hi`, we have `hi − lo ≥ 1`, so `⌊(hi−lo)/2⌋ + 1 ≤ hi − lo`, hence

```
mid = lo + ⌊(hi-lo)/2⌋ + 1  ≤  lo + (hi - lo)  =  hi
```

and `mid ≥ lo + 1`. So:
- `f(mid) = true ⟹ lo ← mid ≥ lo + 1` ⟹ `lo` strictly increases.
- `f(mid) = false ⟹ hi ← mid − 1 ≤ hi − 1` ⟹ `hi` strictly decreases.

Either way the interval `[lo, hi]` shrinks by ≥ 1, and it is bounded below by 0 ⇒ termination. ✓

**Without the `+1`:** `mid = lo + ⌊(hi−lo)/2⌋` equals `lo` whenever `hi = lo + 1`. If `f(lo)` is true we set `lo ← mid = lo` and loop forever. **This is the infinite-loop bug.**

**Iteration count:** same halving, so `⌈log₂(R + 1)⌉`.

---

## 8. Information content of binary search

The decision tree of binary search over `R` outcomes is a **complete balanced binary tree** of depth `⌈log₂ R⌉`. Its leaves are the possible answers, so the information delivered is exactly `log₂ R` bits.

Compare with the other searches in the academy:

| Algorithm | Bits per operation | Total bits for `n` distinct keys |
|-----------|--------------------|----------------------------------|
| Binary search | 1 (`≤ mid?`) | `log₂ n` per query — optimal |
| Linear search | 1 | `O(n)` — `n/2` expected |
| Hash lookup | `log₂(load factor)` | `O(1)` expected, no worst case |
| Comparison sort | 1 | `log₂(n!) ≈ n log₂ n` — optimal |
| Counting sort | `log₂ k` | `n log₂ k` — **superlinear information** |

**Binary search is the only search where each step extracts exactly the maximum information available.** That is the cleanest statement of why it is optimal.

---

## 9. Compound cost table for this lab

| Problem | Outer | Inner | Total |
|---------|-------|-------|-------|
| Binary search a sorted array | — | — | `Θ(log n)` |
| Binary search on the answer, `f` = O(1) | `Θ(log R)` | — | `Θ(log R)` |
| Binary search on the answer, `f` = `Θ(log n)` (e.g. `Set.size` on a BST) | `Θ(log R)` | `Θ(log n)` | `Θ(log R · log n)` |
| Binary search on the answer, `f` = `Θ(n)` (e.g. a feasibility simulation) | `Θ(log R)` | `Θ(n)` | `Θ(n log R)` |
| `k`-th smallest of `n`, `f` = `Θ(n)` count | `Θ(log n)` | `Θ(n)` | `Θ(n log n)` — same as sorting! |
| `k`-th smallest with a Fenwick tree, `f` = `Θ(log n)` prefix query | `Θ(log n)` | `Θ(log n)` | `Θ(log² n)` |
| Exponential search, answer at distance `k` | `Θ(log k)` doubling + `Θ(log k)` binary | | `Θ(log k)` |
| Parallel binary search (`p` queries, sorted answers) | — | `Θ(log n)` rounds × `Θ(n + p)` per round | `Θ((n + p) log n)` work, `Θ(log n)` depth |

**The `k`-th-smallest row is the punchline:** binary searching on an answer whose predicate costs `Θ(n)` is *no better than sorting*. Structure (a Fenwick tree, a sorted array, a prefix-sum array) must make `f` sublinear or the trick buys nothing.

---

## 10. Quick reference

| Quantity | Value |
|----------|-------|
| Recurrence | `T(n) = T(n/2) + Θ(1)` — Master theorem Case 2 |
| Result | `Θ(log n)` |
| Exact iteration count (half-open) | `⌈log₂ n⌉` |
| Best case | `⌈log₂ n⌉ − 1` — the same up to constants |
| Information per step | exactly 1 bit — optimal |
| Overflow-safe midpoint | `lo + ((hi - lo) >>> 1)` |
| Overflow threshold | `lo + hi > 2³¹ − 1`; possible for arrays with `n > 2³⁰` |
| Upward-biased midpoint | `lo + (hi - lo + 1) / 2` — the `+1` prevents an infinite loop |
| Exponential search | `Θ(log k)` for an answer at distance `k` |
| Predicate search | `Θ(log R · cost(f))` |
| When `Θ(log² n)` genuinely appears | `Θ(log)` candidates × `Θ(log)` cost per feasibility test |
| Rotated search worst case (with duplicates) | `Θ(n)` — information-theoretically necessary |