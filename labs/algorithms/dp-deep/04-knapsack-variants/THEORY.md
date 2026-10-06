# Theory — Knapsack Variants

Knapsack is the canonical example of a problem where **one word in the specification — "at most once" vs "as many as you like" — changes the algorithm, the complexity class, and the entire body of theory.** This lab covers all six variants plus the two axes along which you can trade `W` for `n`, `Σwᵢ`, or the profit bound `P`.

---

## 1. 0/1 knapsack

### Statement

Items `1..n` with weights `wᵢ` and values `vᵢ`. Maximise `Σ vᵢ` subject to `Σ wᵢ ≤ W`, each item used at most once. **Weakly NP-complete.**

### DP state and recurrence

> `dp[w]` = the maximum value obtainable from the items processed so far with total weight **at most** `w`.

```
init:   dp[w] = 0        for w = 0..W        (the "at most" convention: empty set is always feasible)
for i = 1..n:
    for w = W down to w[i]:
        dp[w] = max(dp[w], dp[w - w[i]] + v[i])
answer: dp[W]
```

**Time:** `Θ(nW)`. **Space:** `Θ(W)`, or `Θ(min(n,W))` items if you track only the chosen set.

### Why the loop order *is* the specification

`dp[w - w[i]]` must be the value computed **before** item `i` was considered:

- **Descending** `w`: `w - w[i] < w`, and since we are going down, index `w - w[i]` has **not** yet been updated in this item's pass ⇒ it is the previous row ⇒ **0/1 semantics**.
- **Ascending** `w`: `w - w[i] < w` and *has* already been updated in this pass ⇒ it already contains item `i` ⇒ the item can be reused ⇒ **unbounded semantics**.

**This is not an optimisation. It is the definition.** A 0/1 knapsack with an ascending loop silently becomes an unbounded knapsack, and the test that catches it must include an input where the item count matters (`w_i = 1, v_i = 3, W = 10, n = 1` gives `3` for 0/1 and `30` for unbounded).

### "At most" vs "exactly"

| convention | initialisation | unreachable weights |
|-----------|---------------|---------------------|
| `dp[w]` = max value with weight **at most** `w` | `0` | none — every `w` is reachable with value 0 |
| `dp[w]` = max value with weight **exactly** `w` | `-∞` (or `Long.MIN_VALUE`) | must be detected; `dp[W]` may be `-∞` |

The "exactly" version is what you need when the weight must be hit precisely (subset sum, exact-change, bin packing feasibility). **It is strictly more work and must use a proper `-∞` sentinel, not `0`.**

### Reconstruction

Store a `boolean[][] take` of size `n × W` (memory `Θ(nW)`), or a `byte[]` per item. Then walk backwards. **Reconstruction costs `Θ(nW)` space** — the same rolling-array trade as lab `01`.

A cheaper trick: store only, for each item, a `bitset` of the weights at which the value improved (`Θ(nW)` bits instead of `Θ(nW)` bytes — a `64×` saving). This is what real implementations do.

---

## 2. Unbounded knapsack

```
for i = 1..n:
    for w = w[i] to W:              // ASCENDING
        dp[w] = max(dp[w], dp[w - w[i]] + v[i])
```

Same `Θ(nW)`, same `Θ(W)` space. This is the algorithm behind **coin change** (lab `01`), unbounded rod cutting, and maximum-value-in-a-bag (LeetCode 322).

**Transpose trick:** the item-outer/weight-inner order can also be swapped to weight-outer/item-inner, which is a different DP:

```
for w = 0..W:
    for i = 1..n:
        if w >= w[i]: dp[w] = max(dp[w], dp[w - w[i]] + v[i])
```

**These are NOT equivalent for the unbounded case.** The first computes an *optimal* solution; the second computes the "at most" version correctly too, but the **chosen multiset can differ** and the item-outer form is the standard one because it makes the "use item `i` again" step explicit. Test with a tie-heavy instance.

---

## 3. Bounded knapsack

Item `i` has `c[i]` copies available.

### (a) Naive

```
for i = 1..n:
    for w = W down to 0:
        for k = 1 to min(c[i], w / w[i]):
            dp[w] = max(dp[w], dp[w - k*w[i]] + k*v[i])
```

`Θ(W Σ c[i])` — explodes when the counts are large (`c[i] = 10⁶` ⇒ `10⁶ · W`).

### (b) Binary splitting

Replace item `i` (count `c`) with `Θ(log c)` **0/1 bundles** whose sizes represent every count from `0` to `c`:

```
c = 13  ->  bundles of size 1, 2, 4, 6      (1+2+4+6 = 13, and every k in 0..13 is a subset sum)
c = 8   ->  bundles of size 1, 2, 4, 1       (or 1,2,4,1; or 3,5; many valid decompositions)
general:  take 1, 2, 4, ..., 2^(m-1), then the remainder c − (2^m − 1)
```

```
for i = 1..n:
    for each bundle (bw, bv) of item i:
        for w = W down to bw:
            dp[w] = max(dp[w], dp[w - bw] + bv)
```

`Θ(W Σ log c[i])`. **One extra level of nesting and an elegant trick**, and it captures most of the practical benefit of (c).

**Correctness argument:** the bundle sizes `1,2,4,…,2^{m-1}, r` form a "complete" sequence — every integer `0..c` is a subset sum of them. So any feasible choice of `k ≤ c` copies is representable, and any representation uses at most `c` copies. Therefore the bundle problem and the bounded problem have identical optimal values. ∎

**Pitfall:** the bundle decomposition must cover **every** count, not just be a partition. `{1,2,4,6}` covers `0..13`; `{4,4,4}` covers only multiples of 4 and would give a wrong answer. Test with `c = 3` and a `W` that forces exactly 2 copies.

### (c) Monotone queue — `Θ(nW)` regardless of counts

The best bounded knapsack DP. For one item type `i` with weight `p`, value `q`, count `c`:

```
newDp[w] = max over k in [0, c] of ( dp[w - k*p] + k*q )
```

Group by residue `r ∈ {0,…,p−1}` modulo `p`. Write `w = r + t·p`. Let `s = t − k`, so `w − k·p = r + s·p` and `k = t − s`:

```
newDp[r + t*p]  =  max over s in [max(0, t-c), t] of ( dp[r + s*p] + (t-s)*q )
                =  t*q  +  max over s in [t-c, t] of ( dp[r + s*p] - s*q )
```

**A sliding-window maximum of width `c+1` over the sequence `X[s] = dp[r + s*p] − s·q`.**

The monotone deque maintains it in `Θ(1)` amortised per `s`, so each item type costs `Θ(W)`:

```
Time:  Θ(nW)      Space: Θ(W)
```

**This is the same sliding-window trick as lab `03`'s bounded subarray, and as the Knuth optimisation in lab `05`.** The pattern recurs: a `k`-step knapsack transition is a sliding-window extremum once you reparametrise by residue.

**Why the constant matters:** for `n = 200`, `W = 10⁵`, `c = 1000`:
| method | time |
|---|---|
| naive | `2·10¹⁰` ✗ |
| binary splitting | `2·10⁸` (~1 s) |
| **monotone queue** | **`2·10⁷` (~100 ms)** |

---

## 4. Fractional knapsack — greedy, and why

### Statement

Items may be split. Maximise `Σ vᵢ` subject to `Σ wᵢ ≤ W`. **Solvable exactly in `Θ(n log n)`.**

### Algorithm

```
sort items by v[i] / w[i] descending
remaining = W; value = 0
for each item in order:
    if w[i] <= remaining: take it whole; remaining -= w[i]; value += v[i]
    else:                take a fraction; value += v[i] * remaining / w[i]; break
```

### Why greedy is optimal

**Exchange argument.** Suppose `S` is an optimal solution and item `a` has a higher ratio than item `b`, but `S` includes `b` and not all of `a`. Swapping a small amount of `b` for the same weight of `a` does not decrease the value. Repeating, we get an optimal solution that fills items in decreasing-ratio order — which is exactly the greedy solution. ∎

**LP view:** fractional knapsack is the LP relaxation of 0/1 knapsack, and its optimal basic feasible solution has at most one fractional variable. The greedy solution has exactly that form.

### The approximation guarantee (for 0/1)

Greedy-by-ratio on 0/1 knapsack gives:
- a **`2`-approximation** versus the fractional optimum (trivially, since greedy solves the relaxation),
- and the **Martello–Toth (1998) bound** tightens this: the solution is within `11/9 ≈ 1.2222` of the true 0/1 optimum, and the worst case is attained when a single item causes the split.

**This is genuinely useful in production** where an exact `Θ(nW)` is infeasible — a knapsack heuristic within 22% in `Θ(n log n)` beats a slow exact answer.

---

## 5. Subset sum and the bitset

### Boolean DP
```
bits[w] = true iff sum w is achievable using items 1..i
init:   bits[0] = true
for i:  for w = W down to w[i]:  bits[w] |= bits[w - w[i]]
```
`Θ(nW)`, `Θ(W)` bits (`W/8` bytes).

### Word-parallel bitset

Pack the `W+1` booleans into `(W+1)/64` longs and do the whole item in **one shift-and-or per word**:

```java
long[] bits = new long[(W >>> 6) + 1];
bits[0] = 1;                                  // sum 0 achievable
for (int x : a) {
    int wordShift = x >>> 6, bitShift = x & 63;
    for (int i = bits.length - 1; i >= wordShift; i--) {
        long shifted = bits[i - wordShift] << bitShift;
        if (bitShift != 0 && i - wordShift - 1 >= 0)
            shifted |= bits[i - wordShift - 1] >>> (64 - bitShift);   // carry across words
        bits[i] |= shifted;
    }
}
return ((bits[W >>> 6] >>> (W & 63)) & 1L) != 0;
```

**Complexity:** `Θ(n · W/64)` word operations — a **`64×` speedup**, and the code is shorter than the boolean DP.

**Descending loop is essential** so `bits[i-wordShift]` is not already updated for this item — the same 0/1 requirement as the scalar DP.

**Pitfall:** the carry propagation `>>> (64 - bitShift)` with `bitShift == 0` would shift by 64, which Java silently reduces to 0 (producing garbage). The explicit `if (bitShift != 0)` guard is required.

**This is the canonical bit-parallel DP** and the reason lab `08-bit-sort-search` exists: **when a DP's state is boolean, pack 64 states per machine word and the complexity drops by a factor of `w`.**

---

## 6. Trading the capacity: three alternative axes

The `Θ(nW)` barrier is only a barrier if you insist on the weight axis.

### (a) By value (`P` = total profit)

```
dp[p] = minimum weight needed to achieve value AT LEAST p
init:  dp[0] = 0, dp[p] = +INF
for i: for p = P down to v[i]: dp[p] = min(dp[p], dp[p - v[i]] + w[i])
answer: largest p with dp[p] <= W
```

`Θ(nP)` time, `Θ(P)` space. **Use when `P ≪ W`** — e.g. small monetary budgets, small counts.

### (b) By sum of weights (`S = Σ wᵢ`)

Same idea: `Θ(n·min(W, S))`. Use when weights are large but few.

### (c) Meet-in-the-middle (`Θ(2^{n/2})`)

Split the `n` items in half. Enumerate all `2^{n/2}` subsets of each half with their `(weight, value)`, sort the first by weight, and for each of the `2^{n/2}` subsets of the second half binary-search the best first-half partner.

- Time: `Θ(2^{n/2} log 2^{n/2}) = Θ(n 2^{n/2})`
- Space: `Θ(2^{n/2})`

**For `n = 40`, `W = 10⁹`:** `Θ(40 · 10⁶) = 4·10⁷` — feasible. `Θ(nW) = 4·10¹⁰` — not.

**For `n = 60`:** `2³⁰ = 10⁹` subsets = 16 GB. Infeasible.

**This is the right answer for small `n` and large `W`**, and it is exactly the same idea as Held–Karp (lab `01` `32-exact-exponential`).

### (d) Branch and bound

Sort by ratio, do DFS with an optimistic bound from fractional knapsack on the remaining items, prune when the bound ≤ incumbent. `O(2ⁿ)` worst but solves `n = 100` with realistic weights in milliseconds.

### Choosing

| Situation | Best method | Cost |
|-----------|-------------|------|
| `n`, `W` both moderate (`n ≤ 200`, `W ≤ 10⁵`) | 0/1 DP | `Θ(nW) ≤ 2·10⁷` |
| small `n` (≤ 40), huge `W` | **meet-in-the-middle** | `Θ(n 2^{n/2})` |
| large `n`, huge `W`, "good enough" | greedy by ratio | `Θ(n log n)`, within `11/9` |
| `n` large, `Σ vᵢ` small | DP by value | `Θ(nP)` |
| huge `n`, `W` huge, need speed | greedy + local search | `Θ(n log n)` |
| subset sum, `W ≤ 10⁶` | **bitset** | `Θ(nW/64)` |
| unbounded / coin change | ascending DP | `Θ(nW)` |
| bounded with large counts | **monotone queue** | `Θ(nW)` |
| fractional | greedy | `Θ(n log n)` |

---

## 7. Multi-dimensional and structural variants

### `d`-dimensional knapsack
```
dp[w1][w2][...][wd] = max value with Σ weights in each dimension within its cap
time  Θ(n Π Wᵢ)
space Θ(Π Wᵢ)
```
The dimension-count curse is brutal: `d = 3`, `Wᵢ = 100` ⇒ `10⁶` states × `n = 100` = `10⁸`. `d = 4` is 10¹⁰. Real problems use LP relaxation + branch and bound, not DP.

### Group knapsack
Choose at most one item from each group. **Item loop inside, weight loop outside** — this is the reverse of 0/1 and is *the* detail that distinguishes it:

```java
for (group : groups)
    for (w = W; w >= 0; w--)
        for (item : group)
            if (w >= item.weight) dp[w] = max(dp[w], dp[w - item.weight] + item.value);
```

Putting the group loop *inside* the weight loop silently allows taking two items from one group.

### Dependency knapsack
Items have prerequisites. Turn it into a **max closure / min cut** problem (`Θ(nm)` on the dependency graph), or use a topological-order DP.

### Minimum-cost knapsack
Swap the roles: `dp[v] = min weight to achieve value `v`, or `dp[w] = min cost to reach weight `w`. Same `Θ(nW)` shape.

### Pareto / multi-objective
Maximise value subject to weight **and** a second constraint. The DP no longer collapses to one dimension — you need either `Θ(nW₁W₂)` or a **Pareto frontier** maintained as a staircase of non-dominated `(weight, value)` pairs. The frontier size is the parameter; the honest answer for real problems is `Θ(n · |frontier|)`.

---

## 8. The meta-lesson

Across all variants the structure is identical:

```
Θ(n · k)  where k is the state dimension's inner extent
```

and every optimisation reduces `k`:
- capacity → profit (`Θ(nP)`) when `P ≪ W`
- weight → subset sum on the smaller of `n`, `W`
- boolean state → 64 states per word (`Θ(nW/64)`)
- `k`-step bounded transition → sliding window (`Θ(nW)` from `Θ(Wc)`)
- `n` small, `W` huge → `Θ(n 2^{n/2})`

**And the framing question — "0/1, unbounded, fractional?" — is a specification question that determines the complexity class.** Greedy for fractional, `Θ(nW)` DP for bounded and unbounded, `Θ(n log n)` greedy-with-`11/9`-guarantee when neither is affordable, and NP-hard above all of that.