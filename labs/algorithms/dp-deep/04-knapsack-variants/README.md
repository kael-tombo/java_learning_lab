# 04 — Knapsack Variants

<div align="center">

**0/1 · Unbounded · Bounded (Binary Splitting) · Monotone-Queue Optimisation · Fractional/Greedy · Multi-Dimensional · Subset Sum**

</div>

---

## Learning Objectives

- Derive the 0/1 knapsack recurrence and explain why the capacity loop must run **descending**
- Explain why ascending turns 0/1 into unbounded, and prove the failure mode
- Implement the three ways to handle **bounded** knapsack: naive 3-loop, binary splitting, monotone queue
- Derive the monotone-queue (sliding-window max) optimisation from the 2-D transition
- Explain when fractional knapsack is `Θ(n log n)` greedy and when 0/1 is NP-hard
- Recognise multi-dimensional knapsack, group knapsack, and dependency knapsack as the same DP with different state shapes
- State the practical limits: `Θ(nW)` is not viable when `W` is large

## Prerequisites

- `01-dp-classics` — the DP framework and fill-order rules
- `03-lis-kadane` — the sliding-window/deque idea (applied again here)
- `06-greedy-algorithms` for the fractional case

## Estimated Time

- **Theory**: 110 minutes
- **Practice**: 150 minutes
- **Exercises**: 90 minutes
- **Total**: 6–7 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| 0/1 knapsack | each item used at most once; `Θ(nW)` DP |
| Unbounded knapsack | each item reusable; ascending capacity loop |
| Bounded knapsack | `c[i]` copies available; naive `Θ(W Σc[i])`, binary splitting `Θ(W Σlog c[i])`, monotone queue `Θ(nW)` |
| Fractional knapsack | items divisible; **greedy by value/weight**, `Θ(n log n)` |
| DP state | `dp[w]` = max value using total weight **at most** `w` |
| DP state (exact) | `dp[w]` = max value using total weight **exactly** `w` — needs `−∞` init |
| Descending loop | makes `dp[w − wi]` read the *previous item's* row ⇒ 0/1 |
| Ascending loop | makes `dp[w − wi]` read the *current item's* updated value ⇒ unbounded |
| Binary splitting | `c = 13 → 1,2,4,6` — turns bounded into `Θ(log c)` 0/1 items |
| Monotone queue | optimises bounded/partition DP by sliding-window max, `Θ(nW)` regardless of `c` |
| Greedy ratio | optimal **only** for fractional; for 0/1 it is a `2`/`1.5`-approximation |
| `Θ(nW)` viability | `n = 100`, `W = 10⁵` ⇒ `10⁷` ✓; `n = 1000`, `W = 10⁶` ⇒ `10⁹` ✗ |

## Complexity Snapshot

| Variant | Time | Space | Comment |
|---------|------|-------|---------|
| 0/1 knapsack (DP) | **`Θ(nW)`** | `Θ(W)` | the standard |
| 0/1 knapsack (branch and bound) | `Θ(2ⁿ)` worst, fast in practice | `O(n)` | good for small `n`, real `W` |
| Unbounded knapsack (DP) | `Θ(nW)` | `Θ(W)` | **ascending** loop |
| Bounded, naive | `Θ(W Σ c[i])` | `Θ(W)` | explodes when `c` is large |
| Bounded, binary splitting | `Θ(W Σ log c[i])` | `Θ(W)` | simple and often enough |
| Bounded, **monotone queue** | **`Θ(nW)`** | `Θ(W)` | optimal for the DP |
| Fractional knapsack | **`Θ(n log n)`** | `Θ(n)` | greedy, exact |
| Multi-dimensional (`d` dims) | `Θ(n Π Wᵢ)` | `Θ(Π Wᵢ)` | dimension-count curse |
| **Exact weight** DP | `Θ(nW)` | `Θ(W)` | `−∞` initialisation |
| Subset sum | `Θ(nW)` | `Θ(W)` | boolean DP, or `Θ(n·W/64)` bitset |
| Subset sum (bitset) | **`Θ(nW/64)`** | `Θ(W/8)` bytes | 64× via word parallelism |
| 0/1 knapsack (meet-in-the-middle) | `Θ(2^{n/2})` | `Θ(2^{n/2})` | only for `n ≤ 40`, arbitrary `W` |
| Knapsack by weight (`W` huge) | `Θ(n · maxWeight)` | `Θ(n)` | swap the axes |
| Knapsack by **value** (profit `P`) | `Θ(nP)` | `Θ(P)` | the right choice when `P ≪ W` |

## Algorithms Covered

### 0/1 knapsack
```
dp[w] = max value using total weight <= w
init:  dp[w] = 0 for all w            (the "at most" convention)
for each item (weight wi, value vi):
    for w = W down to wi:              // DESCENDING
        dp[w] = max(dp[w], dp[w - wi] + vi)
answer: dp[W]
```
**Why descending:** `dp[w - wi]` must be the value computed **before** this item was added. Descending guarantees `w - wi < w` has not yet been updated in this item's pass.

### Unbounded knapsack
```
for each item (wi, vi):
    for w = wi to W:                  // ASCENDING
        dp[w] = max(dp[w], dp[w - wi] + vi)
```
**Why ascending:** `dp[w - wi]` was already updated for this item, so the item can be used repeatedly.

### Bounded knapsack — three implementations

**(a) Naive:**
```
for each item i with count ci:
    for w = W down to 0:
        for k = 1 to min(ci, w / wi):
            dp[w] = max(dp[w], dp[w - k*wi] + k*vi)
```
`Θ(W Σ cᵢ)`.

**(b) Binary splitting:** replace item `i` with `⌊log₂ cᵢ⌋ + O(1)` 0/1 bundles whose sizes cover all counts. `c = 13 → 1, 2, 4, 6`. `Θ(W Σ log cᵢ)`. Elegant, one-line change, 90% of the benefit.

**(c) Monotone queue:** for one item type, the transition is
```
newDp[w] = max over k in [0, ci] of  ( dp[w - k*wi] + k*vi )
```
Group by residue `r = w mod wi`: writing `w = r + t*wi` and `j = w - k*wi = r + (t-k)*wi`, set `s = t - k`:
```
newDp[r + t*wi] = max over s in [t-ci, t] of  ( dp[r + s*wi] - s*vi ) + t*vi
                = t*vi + max over s in [t-ci, t] of ( dp[r + s*wi] - s*vi )
```
**A sliding-window maximum** over the sequence `dp[r + s*wi] - s*vi` with window `ci + 1`. Monotone deque per residue ⇒ `Θ(W)` per item type ⇒ `Θ(nW)` total, **independent of the counts**.

### Fractional knapsack — greedy
Sort by `vi / wi` descending; take whole items until capacity is exhausted, then a fraction of the next.
**Optimal** because the LP relaxation is the fractional problem and greedy solves it (the LP is totally unimodular for the fractional variant). `Θ(n log n)`.

**And 0/1 knapsack is weakly NP-hard** — no known polynomial algorithm. **Proving that the greedy ratio is a `2`-approximation** (and, with the Martello–Toth bound, at worst `1.5` relative to the fractional optimum, `11/9` relative to the true optimum) is a genuinely useful result.

### Subset sum — bitset
```
bits = 1                      // bit 0 set: sum 0 achievable
for x in a:
    bits |= bits << x         // ONE machine word op per item for w <= 64
answer: (bits >> W) & 1
```
`Θ(nW/64)` word operations. **This is the single best bit-parallel DP example in the course** and the direct justification for lab `08-bit-sort-search`.

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/knapsack/` | All six variants |
| `src/test/java/com/alglab/knapsack/` | Cross-validation + invariants |
| `SOLUTION/` | Worked solutions |
| `TESTS/` | Edge cases (`W = 0`, all items too heavy, counts = 0) |
| `BENCHMARK/` | Variant-by-variant timings, the `nW` viability wall |
| `MINI_PROJECT/` | Knapsack visualiser with the DP table and the chosen items |
| `REAL_WORLD_PROJECT/` | Capacity-constrained portfolio / ad-budget allocator |
| `CHALLENGE/` | Meet-in-the-middle, branch and bound, Pareto fronts |
| `DIAGRAMS/` | Item-selection animations, monotone-queue traces |