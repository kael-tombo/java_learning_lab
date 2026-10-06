# Math Foundation — Knapsack Variants

The `Θ(nW)` barrier, the amortised proof of binary splitting, the sliding-window algebra of the monotone queue, and the LP geometry of the greedy approximation.

---

## 1. The `Θ(nW)` computation

```
for i = 1..n:
    for w = W down to w[i]:
        dp[w] = max(dp[w], dp[w - w[i]] + v[i])
```

Inner loop executes `W − w[i] + 1` times:

```
T(n, W)  =  Σ_{i=1}^{n} (W − w[i] + 1)  =  nW − Σw[i] + n
          =  Θ(nW)     (when W ≫ mean weight)
Space    =  Θ(W)
```

**The viability wall:**

| `n` | `W` | `nW` | feasible? |
|-----|-----|-------|-----------|
| 100 | 10⁵ | `10⁷` | ✓ 50 ms |
| 1 000 | 10⁵ | `10⁸` | ✓ 500 ms |
| 200 | 10⁶ | `2·10⁸` | ✓ 1 s |
| 10⁴ | 10⁵ | `10⁹` | ~5 s, borderline |
| 1 000 | 10⁹ | `10¹²` | ✗ |
| 10⁴ | 10⁶ | `10¹⁰` | ✗ |

---

## 2. Why the loop order is the specification

Descending `w` ⇒ `dp[w − wᵢ]` is read **before** the current item's write ⇒ 0/1 semantics.
Ascending `w` ⇒ `dp[w − wᵢ]` was already updated for this item ⇒ unbounded semantics.

**Formal:** let `D_i[w]` be the correct value using items `1..i`. Then

```
D_i[w] = max( D_{i-1}[w],  D_{i-1}[w - w_i] + v_i )
```

Descending in-place implements this (both reads come from `D_{i-1}`). Ascending implements

```
D_i[w] = max( D_{i-1}[w],  D_i[w - w_i] + v_i )
```

which is exactly the **unbounded** recurrence. **One loop direction = one different problem.** There is no test that catches this except an instance where the two answers differ, e.g. `n = 1`, `w = 1`, `v = 3`, `W = 10`: `3` vs `30`.

---

## 3. Bounded knapsack: the three costs

### Naive
```
T = Σ_i W · min(c_i, W / w_i)   ≤  W · Σ c_i
```
`c_i = 1000`, `W = 10⁵`, `n = 200` ⇒ `2·10¹⁰`. ✗

### Binary splitting
Decompose `c` into bundles `1, 2, 4, ..., 2^{m−1}, c − (2^m − 1)` where `2^m ≤ c < 2^{m+1}`.

Number of bundles: `m + 1 = ⌊log₂ c⌋ + 1` (or `⌈log₂(c+1)⌉`).

```
T = Σ_i W · (log₂ c_i + 1)   ≤  n W log C_max
```

**Completeness proof.** Claim: the bundle sizes represent every integer in `[0, c]`.

Let the sizes be `1, 2, 4, …, 2^{m−1}, r` with `r = c − (2^m − 1)` and `0 ≤ r < 2^m`.

- Powers of two `1..2^{m−1}` represent every `k ∈ [0, 2^m − 1]` (binary expansion).
- For `k ∈ [2^m, c]`, take `k − r`. Since `c − r = 2^m − 1` and `k ≥ 2^m > c − r`, we have `k − r ≥ 2^m − r > 0` and `k − r ≤ c − r = 2^m − 1`, so `k − r` is representable by the powers; add the `r` bundle. ∎

Therefore the bundle knapsack and the bounded knapsack have **identical optimal values**.

| `c` | bundles | `⌈log₂(c+1)⌉` |
|-----|---------|----------------|
| 1 | 1 | 1 |
| 3 | 1,2 | 2 |
| 8 | 1,2,4,1 | 4 |
| 13 | 1,2,4,6 | 4 |
| 1000 | 1,2,4,8,16,32,64,128,256,489 | 10 |
| 10⁶ | 21 bundles | 20 |

**Speedup:** `log₂ 1000 ≈ 10` ⇒ `100×` over naive. Practical and trivially correct.

### Monotone queue — the algebra

For item `(p, q, c)`, the transition is

```
newDp[w]  =  max over k in [0, c]  of  ( dp[w - k·p] + k·q )
```

Regroup by residue `r = w mod p`. Write `w = r + t·p`. Substituting `s = t − k` (so `k = t − s`, and `w − k·p = r + s·p`):

```
newDp[r + t·p]  =  max over s in [t−c, t]  of  ( dp[r + s·p] + (t−s)·q )
               =  t·q  +  max over s in [t−c, t]  of  ( dp[r + s·p] − s·q )
```

Define `X_r[s] = dp[r + s·p] − s·q`. Then

```
newDp[r + t·p] = t·q + max{ X_r[s] : s in [max(0, t−c), t] }
```

**A sliding-window maximum of width `c+1` on each residue class.**

**Amortised deque cost:** each `s` is pushed once and popped at most once ⇒ `Θ(W)` per residue class, and the residue classes partition the `W+1` states ⇒ **`Θ(W)` per item type, `Θ(nW)` total.**

**Algebraic proof it equals the naive bound:** the window `[t−c, t]` contains exactly `c+1` terms, matching `k ∈ [0, c]`. ∎

| `n` | `W` | `c` | naive | binary split | monotone queue |
|-----|-----|-----|-------|--------------|----------------|
| 200 | 10⁵ | 1 000 | `2·10¹⁰` ✗ | `2·10⁸` ~1 s | **`2·10⁷` ~100 ms** |
| 200 | 10⁵ | 10⁶ | `2·10¹³` ✗ | `2·10⁸` | **`2·10⁷`** |

**Cost is independent of `c`.** That is the entire selling point.

---

## 4. Fractional knapsack and the greedy proof

### LP form

```
maximise  Σ vᵢ xᵢ
s.t.      Σ wᵢ xᵢ ≤ W
          0 ≤ xᵢ ≤ 1            (fractional)
```

**Optimality of greedy.** At an optimal basic feasible solution, at most one variable is fractional (there are two constraints: the capacity and the box `0 ≤ x ≤ 1`, so a vertex has at most 2 fractional variables, one of which is typically the capacity binding). The greedy solution has that form: take items in decreasing ratio until one is split.

**Exchange argument (self-contained).** Let `S` be optimal, and let `a, b` be items with `v_a/w_a > v_b/w_b`, `a` taken at fraction `< 1`, `b` taken at fraction `> 0`. Move `δ = min(1 − x_a, x_b)` of weight from `b` to `a`:

```
Δvalue = δ(v_a − v_b·(w_a/w_b)) = δ·w_a·(v_a/w_a − v_b/w_b) > 0
```

Contradiction. So an optimal solution exists in greedy order. ∎

### The `2`-approximation (0/1)

Greedy by ratio on 0/1 gives a solution at least `OPT_F / 2` where `OPT_F` is the fractional optimum. Proof: the greedy fractional solution is a relaxation, so `OPT_F ≥ OPT_01`; the greedy 0/1 solution takes whole items in decreasing-ratio order, and the fractional solution obtained by "completing" it differs only in one item, whose value is at most `v_max`. A standard argument gives `greedy ≥ (OPT_F − v_max)/2`... the clean statement is:

```
greedy_01  ≥  OPT_F / 2  ≥  OPT_01 / 2
```

So greedy is a **2-approximation**. Standard.

### Martello–Toth: the tighter `11/9` bound

Martello & Toth (1998) sharpened this: the greedy solution satisfies

```
greedy_01  ≥  (11/9) · OPT_01  −  (6/9) · v_max
```

and in particular

```
greedy_01  ≥  (11/9) · OPT_01      when OPT_01 ≥ 6 · v_max
```

Worst-case ratio `11/9 ≈ 1.2222`. This is the best known general bound for the ratio greedy and it is **tight** — the extremal instance has a single item whose split determines the outcome.

**Practical value:** `Θ(n log n)` with a `1.2222` guarantee beats a `Θ(nW)` exact answer whenever `W` makes the DP infeasible. That is a real engineering trade, not a theoretical nicety.

---

## 5. Bitset subset sum — the `w`-fold speedup

### Word-parallel derivation

Boolean DP:
```
bits_i[w]  =  bits_{i-1}[w]  OR  bits_{i-1}[w - x_i]
```

Pack `W+1` bits into `⌈(W+1)/64⌉` words, `bits[w]` = bit `w & 63` of word `w >>> 6`. Then the whole update is

```
bits |= bits << x_i
```

which is `Θ(W/64)` word operations (one shift + one OR per word, plus carry propagation).

```
Time:  Θ(n · W / 64)   vs  Θ(nW)        ->  64x fewer word operations
Space: Θ(W/8) bytes    vs  Θ(W) bytes   ->  64x smaller
```

**Descending word order is required** so the source word is not already updated for this item — the same 0/1 rule.

**Carry propagation:** `bits << x` across words:
```
wordShift = x >>> 6, bitShift = x & 63
for i = last down to wordShift:
    shifted  = bits[i - wordShift] << bitShift
    if bitShift != 0 and i - wordShift - 1 >= 0:
        shifted |= bits[i - wordShift - 1] >>> (64 - bitShift)
    bits[i] |= shifted
```

`bitShift == 0` must be special-cased because `>>> 64` in Java is `>>> 0` (shift counts masked to 5/6 bits), producing `bits[i-1]` instead of `0`.

**This is the DP-to-bit-parallel transformation in its purest form: a boolean state array of `W` entries becomes `W/64` machine words, and the whole `Θ(nW)` recurrence collapses to `Θ(nW/64)`.**

---

## 6. Trading the axes

| formulation | time | space | choose when |
|---|---|---|---|
| by weight `W` | `Θ(nW)` | `Θ(W)` | default |
| by profit `P = Σvᵢ` | `Θ(nP)` | `Θ(P)` | `P ≪ W` |
| by weight, capped at `Σwᵢ` | `Θ(n·min(W, Σwᵢ))` | `Θ(min(W, Σwᵢ))` | few heavy items |
| meet-in-the-middle | `Θ(n 2^{n/2})` | `Θ(2^{n/2})` | `n ≤ 40`, huge `W` |
| branch and bound | `O(2ⁿ)` | `O(n)` | `n` large, `W` large, ratio-tight instances |
| greedy by ratio | `Θ(n log n)` | `Θ(n)` | anytime, `11/9` guarantee |

### By-profit DP, exact recurrence

```
dp[p] = minimum total WEIGHT to achieve total value AT LEAST p
init:  dp[0] = 0, dp[p] = +INF  for p > 0
for i = 1..n:
    for p = P down to v[i]:
        dp[p] = min(dp[p], dp[p - v[i]] + w[i])
answer: max{ p : dp[p] <= W }
```

`Θ(nP)`. Note the DP now tracks a **minimum cost for a given benefit**, which is the dual of the original — same machinery, swapped roles.

### Meet-in-the-middle

```
Time:  Θ(2^{n/2} · n)         (sorting the first half dominates: 2^{n/2} log 2^{n/2} = n·2^{n/2})
Space: Θ(2^{n/2})
```

| `n` | `2^{n/2}` | time | space |
|-----|----------|------|-------|
| 30 | 32 768 | `10⁶` | 1 MB |
| 40 | `2²⁰` = `10⁶` | `4·10⁷` | 16 MB |
| 46 | `2²³` = `8.4·10⁶` | `3.9·10⁸` | 134 MB |
| 50 | `2²⁵` = `3.4·10⁷` | `1.7·10⁹` | 537 MB |
| 56 | `2²⁸` = `2.7·10⁸` | `1.5·10¹⁰` | **4.3 GB** ✗ |

**Crossover vs `Θ(nW)`:** `n·2^{n/2} < nW ⟺ 2^{n/2} < W`. So meet-in-the-middle wins when `2^{n/2} < W`, i.e. `n < 2 log₂ W`. For `W = 10⁹`: `n < 60`. Consistent with the table.

---

## 7. Multi-dimensional blow-up

`d` dimensions, capacities `W₁..W_d`:

```
States: Π Wᵢ        Time: Θ(n · Π Wᵢ)        Space: Θ(Π Wᵢ)
```

| `d` | `Wᵢ = 100` | states | `n = 100` time |
|-----|-----------|--------|-----------------|
| 1 | 100 | 100 | `10⁴` ✓ |
| 2 | 100 | `10⁴` | `10⁶` ✓ |
| 3 | 100 | `10⁶` | `10⁸` ~0.5 s |
| 4 | 100 | `10⁸` | `10¹⁰` ✗ |
| 5 | 100 | `10¹⁰` | `10¹²` ✗ |

**The dimension count is brutal**, and this is why real multi-constraint allocation problems (portfolio optimisation, ad allocation, packing) use **LP relaxation + branch and bound** rather than DP. The DP is only viable for `d ≤ 2` with modest `Wᵢ`.

### Pareto frontier alternative

Instead of a full grid, maintain the set of **non-dominated** `(weight, value)` pairs:

```
Pareto after item i  =  nondominated( Pareto_{i-1} ∪ { (w + w_i, v + v_i) : (w,v) ∈ Pareto_{i-1} } )
```

The frontier is a staircase, and merging two staircases is `Θ(|P_{i-1}|)`. So:

```
Time: Θ(n · |P|)          Space: Θ(|P|)
```

`|P|` can be exponential, so this is not asymptotically better — but it is **far** better in practice when the frontier is small, which is the normal case for real allocation problems. **Measure the frontier size before choosing.**

---

## 8. Complexity summary

| Variant | Time | Space | Notes |
|---------|------|-------|-------|
| 0/1 knapsack | `Θ(nW)` | `Θ(W)` | descending loop |
| Unbounded knapsack | `Θ(nW)` | `Θ(W)` | ascending loop |
| Bounded, naive | `Θ(W Σ cᵢ)` | `Θ(W)` | explodes |
| Bounded, binary split | `Θ(W Σ log cᵢ)` | `Θ(W)` | bundles cover `[0, c]` |
| Bounded, **monotone queue** | **`Θ(nW)`** | `Θ(W)` | independent of `c` |
| Fractional | **`Θ(n log n)`** | `Θ(n)` | greedy, exact |
| 0/1 greedy | `Θ(n log n)` | `Θ(n)` | `11/9` guarantee |
| By profit `P` | `Θ(nP)` | `Θ(P)` | when `P ≪ W` |
| Meet-in-the-middle | `Θ(n 2^{n/2})` | `Θ(2^{n/2})` | `n ≤ 45`, huge `W` |
| Branch and bound | `O(2ⁿ)` | `O(n)` | practical for `n = 100` |
| Subset sum boolean | `Θ(nW)` | `Θ(W)` bits | — |
| **Subset sum bitset** | **`Θ(nW/64)`** | `Θ(W/8)` B | 64× |
| Multi-dim `d` | `Θ(n Π Wᵢ)` | `Θ(Π Wᵢ)` | `d ≤ 2` only |
| Group knapsack | `Θ(nW)` | `Θ(W)` | group loop **inside** w loop |
| Pareto frontier | `Θ(n·\|P\|)` | `Θ(\|P\|)` | for multi-objective |

---

## 9. Quick reference

| Quantity | Value |
|----------|-------|
| 0/1 recurrence | `dp[w] = max(dp[w], dp[w−wᵢ] + vᵢ)`, **descending** `w` |
| Unbounded | same, **ascending** `w` |
| Exact-weight convention | init `dp[w] = −∞`, not `0` |
| Bundle count for count `c` | `⌈log₂(c+1)⌉` |
| Bundle completeness | `{1,2,4,…,2^{m−1}, c−(2^m−1)}` covers `[0, c]` |
| Monotone-queue reparametrisation | `newDp[r+t·p] = t·q + max{ dp[r+s·p] − s·q : s ∈ [t−c, t] }` |
| Monotone-queue cost | `Θ(W)` per item type, `Θ(nW)` total |
| Greedy (fractional) | `Θ(n log n)`, **exact** |
| Greedy (0/1) approximation | `2`, tightened to **`11/9`** (Martello–Toth) |
| Bitset subset sum | `Θ(nW/64)` word ops, `Θ(W/8)` bytes |
| Bitset loop direction | **descending** (0/1 rule) |
| Bitset carry pitfall | `>>> (64 − bitShift)` needs `bitShift != 0` guard |
| Meet-in-the-middle | `Θ(n 2^{n/2})`; wins when `2^{n/2} < W` i.e. `n < 2 log₂ W` |
| Group knapsack | group loop **inside** the weight loop |
| Multi-dim limit | `d ≤ 2` with `Wᵢ ≤ 10⁴` |
| Viability wall | `nW ≲ 10⁹` for Java (`~5 s`) |

## Sources

- Bellman (1957) / Dantzig (1957) — dynamic programming formulation.
- Martello & Toth (1990, 1998) — the `11/9` bound on ratio greedy.
- Pisinger (1997) — linear-time bounded knapsack with breakpoint dynamic programming (the practical alternative to the monotone queue when weights are bounded).
- Horowitz & Sahni (1974) — meet-in-the-middle.