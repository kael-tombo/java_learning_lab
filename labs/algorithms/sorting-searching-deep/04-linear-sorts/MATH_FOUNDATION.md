# Math Foundation — Linear-Time Sorts

The generating functions, the base-selection calculus, and the crossover mathematics that decides radix vs comparison sorting.

---

## 1. The comparison lower bound, restated

From lab 02:

```
Ω(n log n)   with   n log₂ n − 1.4427 n ≤ log₂(n!) ≤ n log₂ n
```

This bounds **comparison** sorts only. It says: *if the only operation you can perform on two keys is "which is larger?", then you need `log₂(n!)` such operations.*

**Information accounting.** Sorting must map `n!` input permutations to one output order. A comparison reveals 1 bit. Hence `Ω(log₂ n!)` comparisons.

**Non-comparison sorts break the assumption**, not the theorem. Counting sort's inner operation is "compute `count[key]++`" — an array increment that reveals `log₂ k` bits about that element's identity, and it simultaneously tells you something about the *global* multiset (a comparison tells you nothing about the rest of the array).

---

## 2. Counting sort: exact accounting

```
T(n, k) = Θ(n)   [count pass]
        + Θ(k)   [prefix sum]
        + Θ(n)   [scatter pass]
        = Θ(n + k)
```

**Space:** `Θ(k)`.

**The term you must not forget.** With 32-bit keys, `k` can be `2³² ≈ 4.3·10⁹`, so `Θ(k)` = 17 GB. Counting sort is therefore **only** applicable when `k = O(n)`. Restated:

```
Counting sort is Θ(n)  ⟺  key range k = Θ(n)
```

| Algorithm | `n = 10⁶` | Time | Space |
|-----------|-----------|------|-------|
| Comparison sort | | `Θ(20·10⁶)` comparisons | `O(1)`–`Θ(n)` |
| Counting sort, `k = 10⁶` | | `Θ(2·10⁶)` | `4·10⁶` bytes |
| Counting sort, `k = 2³²` | | `Θ(n)` formally | **17 GB** — impossible |

**Stability and the direction convention.** With the inclusive prefix sum `count[v] = #{a_i ≤ v}`, `count[v]` is the *end* position. Filling with `--count[a[i]]` while scanning **backward** places equal keys in ascending input order. If you scanned **forward** you'd reverse them. The formal statement:

```
Stable  ⟺  (scan direction) and (prefix-sum convention) are matched
```

---

## 3. Radix sort: the full cost model

```
T(n, w, B) = d · Θ(n + B)     with  d = ⌈w / log₂ B⌉  and  w = key width in bits
Space      = Θ(n + B)
```

**Case `n = 2²⁰`, `w = 32` bits, `B = 2¹¹`:**

```
d = ⌈32/11⌉ = 3
T = 3 · (1 048 576 + 2048) ≈ 3.15·10⁶ elementary steps
```

versus `Arrays.sort` at `≈ 1.39 · n · log₂ n ≈ 2.9·10⁷` comparisons. **≈ 9× fewer operations**, and counting passes have no unpredictable branches, so the wall-clock ratio is typically 2–4×.

---

## 4. Optimal base selection (calculus)

Treat `k = log₂ B` as a continuous variable, `d = w/k`:

```
cost(k) = (w/k) · (n + 2^k)
```

**Differentiate:**

```
cost'(k) = w · d/dk [ (n + 2^k) / k ]
         = w · [ k · ln2 · 2^k − (n + 2^k) ] / (k ln2)²
```

**Set to zero:**

```
k ln 2 · 2^k  =  n + 2^k
k ln 2 · 2^k  =  n
2^k            =  n / (k ln 2)
```

For large `k`, `k ln 2 ≈ k`, so **`2^k ≈ n/k`**, i.e. slightly below `n`. Numerically solving `k ln 2 · 2^k = n`:

| `n` | `k` | `B = 2^k` | `d = ⌈32/k⌉` | `cost` (units of `n`) |
|-----|-----|-----------|--------------|---------------------|
| 10³ | 6.6 | 97 | 5 | 5.10 |
| 10⁴ | 9.6 | 776 | 4 | 4.03 |
| 10⁶ | 14.9 | 31 000 | 3 | 3.09 |
| 10⁷ | 18.0 | 262 144 | 2 | 2.05 |
| 10⁸ | 21.2 | 2.4·10⁶ | 2 | 2.24 |

**At the optimum:**

```
cost ≈ (w / log₂ n) · 2n  =  Θ( n · w / log₂ n )
```

**Speedup over comparison sorting:**

```
                 n log₂ n
ratio  =  ───────────────────────  =  (log₂ n)² / w
             n · w / log₂ n
```

| `w = 32`, `n` | `(log₂ n)² / 32` |
|---------------|------------------|
| 10³ | 3.1× |
| 10⁵ | 11× |
| 10⁶ | 12.5× |
| 10⁹ | 34× |

**The caveat that erases most of this gain:** `B ≈ n` implies a count array the size of the input. That is **cache-hostile**. Working set = `n` for the counts + `n` for the data = 2× the array, versus TimSort's 2× (but sequential) or quicksort's 1×. The cost model above is an **operation count**, not a memory-traffic count. Choosing `B` so that `B · 4 ≤ 32 KB` (L1) gives `k = 11`, and the measured speedup drops to 2–4×.

---

## 5. Crossover radix vs comparison sort

```
d · (n + B) = c · n log₂ n          (c ≈ 1.39 for dual-pivot quicksort)

With B << n:   d · n = 1.39 n log₂ n   ⟹   d = 1.39 log₂ n
With d = ⌈32/log₂ B⌉:                  ⟹   ⌈32/log₂ B⌉ = 1.39 log₂ n
                                       ⟹   32/log₂ B ≈ 1.39 log₂ n
                                       ⟹   log₂ B ≈ 23 / log₂ n
```

| `n` | `log₂ n` | `log₂ B` | `B` | `d` | Verdict |
|-----|----------|-----------|-----|-----|---------|
| 10² | 6.6 | 3.5 | 11 | 10 | Comparison wins (setup cost) |
| 10³ | 10 | 2.3 | 5 | 14 | Comparison wins |
| 10⁴ | 13.3 | 1.7 | 3 | 19 | Comparison still wins |
| 10⁵ | 16.6 | 1.4 | 3 | 23 | **Crossover** |
| 10⁶ | 20 | 1.15 | 2 | 32 | Radix wins |

**Measured crossover: `n ≈ 3·10⁴`.** Above that, 2-pass or 3-pass LSD radix beats `Arrays.sort(int[])`.

---

## 6. MSD radix: the recurrence and its worst case

```
T(n, d, B) = Θ(n + B) + T(n_max, d−1, B)
```

where `n_max` is the largest bucket.

**Best case** — all distinct: after the first digit every bucket has 1 element ⇒ `T = Θ(n + B)`.

**Worst case** — all identical: one bucket holds everything, for all `d` levels:

```
T(n, d) = d · Θ(n + B) = Θ( (w / log₂ B) · n ) = Θ( n · w / log₂ B )
```

This is **no better than a comparison sort** in the worst case, which is why the standard formulation adds a cutoff:

```
T(n, d) = Θ(n + B) if the largest bucket ≤ C
          T(n, d−1, B) + Θ(n + B)   otherwise
```

With cutoff `C`, the number of levels that recurse is `log_B (n/C)`, and:

```
T(n) = Θ( (n + B) · log_B (n/C) + n log C )
     = Θ( n · (1 + log_B C) )     for B << n
```

Setting `B ≈ C` (so `log_B C = 1`) gives **`Θ(n)`** — MSD radix with a small-bucket comparison cutoff is a linear-time sort.

---

## 7. Bucket sort: the assumption made visible

Keys i.i.d. uniform on a range of size `R`. Bucket count `k`, bucket width `w = R/k`. A bucket receives `n/k` keys. Insertion sort per bucket:

```
E[T] = k · Θ((n/k)²) + Θ(n) = Θ(n²/k + n)
```

`k = n` ⇒ **`Θ(n)`**.

**Now break the assumption.** If keys are concentrated in a fraction `α` of the range:

```
Effective buckets     = αk
Keys per bucket       = n/(αk)
E[T]                 = αk · Θ(n²/(αk)²) = Θ(n²/(αk))
```

With `k = n`: **`Θ(n/α)`**.

| Concentration `α` | Expected time |
|--------------------|---------------|
| 1 (uniform) | `Θ(n)` |
| 0.1 | `Θ(10n)` |
| 0.01 (99% of keys in 1% of range) | `Θ(100n)` |
| 0.0001 | `Θ(10⁴ n)` — **worse than `Θ(n log n)`** |

**This is the whole risk of bucket sort:** it is a bet on the input distribution, and the payout is unbounded. Gaussian keys put `Θ(√n)` of the `n` buckets in play, giving `Θ(n^1.5)` — slower than TimSort. Never deploy bucket sort without validating the distribution.

---

## 8. Key-width, not key-value

The cleanest way to state when radix sort is safe:

```
radix cost  =  Θ( (w / log₂ B) · (n + B) )
```

- It depends on **`w`, the key width in bits** — fixed and known.
- It does **not** depend on the key *values*.

| `w` (bits) | Max key | `d` at `B = 2¹¹` | Feasible? |
|------------|---------|-----------------|-----------|
| 8 | 255 | 1 | yes, often just counting sort |
| 16 | 65 535 | 2 | yes |
| 32 | 4.3·10⁹ | 3 | yes |
| 64 | 1.8·10¹⁹ | 6 | yes |
| 128 | — | 12 | yes |
| 512 (BigInteger) | — | 47 | yes but `d` dominates |

**Practical consequence:** a `BigInteger` key is perfectly radix-sortable — you just pay more passes. Do not fall back to `compareTo` out of laziness; the bit length is a *known* parameter, unlike the key value which is unbounded.

---

## 9. Comparison of the Θ terms

| Algorithm | `n` term | `k`/`B` term | `d` term | Dominant risk |
|-----------|---------|--------------|----------|---------------|
| Counting | `n` | `+k` | — | `k` unbounded ⇒ 17 GB |
| LSD radix | `d·n` | `+d·B` | `w/log₂ B` | passes × memory traffic |
| MSD radix | `n` per level | `+B` per level | `log_B(n/C)` levels | identical keys ⇒ `log_B n` levels |
| Bucket | `n` | `+n` | — | **distribution**, not size |
| Comparison | `n log₂ n` | — | — | adversarial inputs (stable) |

Note the asymmetry: **comparison sorting is the only one of these whose cost is independent of the input's *values*.** That is exactly why it is the safe default, and exactly why every production system that can prove something about its keys uses something else.

---

## 10. Quick reference

| Quantity | Value |
|----------|-------|
| Comparison lower bound | `log₂(n!) ≈ n log₂ n − 1.4427 n` |
| Counting sort | `Θ(n + k)` time, `Θ(k)` space |
| Counting sort is `Θ(n)` iff | `k = Θ(n)` |
| Radix (LSD) | `Θ( d (n + B) )`, `d = ⌈w / log₂ B⌉` |
| Radix (MSD, with cutoff `C`) | `Θ( n (1 + log_B C) )` |
| Radix optimal base | `2^k ≈ n`, i.e. `B ≈ n` |
| Radix speedup at the optimum | `(log₂ n)² / w` |
| Measured crossover vs `Arrays.sort` | `n ≈ 3·10⁴` |
| `Σ_{h≥0} h/2^(h+1)` | `1` |
| Bucket sort (uniform) | `Θ(n)` |
| Bucket sort (concentration `α`) | `Θ(n/α)` |
| Bucket sort worst case | `Θ(n²)` |
| Practically best `B` for 32-bit keys | `2¹¹`–`2¹⁶` (L1/L2-resident counts) |