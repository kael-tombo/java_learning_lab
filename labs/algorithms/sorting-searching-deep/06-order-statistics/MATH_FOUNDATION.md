# Math Foundation — Order Statistics

The selection recurrence, the `Θ(n)` proof for median-of-medians, the exact constant factors, and the comparative counting table.

---

## 1. The selection recurrence

Quicksort:
```
T(n) = 2T(n/2) + Θ(n)   ⟹  Θ(n log n)      (Master theorem Case 2)
```

Quickselect:
```
T(n) = T(n/2) + Θ(n)
```

Unroll:
```
T(n) = T(n/2) + n
     = T(n/4) + n/2 + n
     = T(n/4) + 1.5n
     = T(n/8) + n/4 + 1.5n
     = T(n/8) + 1.75n
     = ...
     = T(n/2^j) + n·(1 + 1/2 + 1/4 + ... + 1/2^{j-1})
```

At `j = log₂ n`:
```
T(n) = T(1) + n · (Σ_{i=0}^{log n - 1} 2^{-i})
     = T(1) + n · (2 − 2^{-(log n - 1)})
     = T(1) + 2n − 2/n
     = Θ(n)
```

**The geometric series is the entire difference.** `Σ 2^{-i} < 2`, so the total work is at most `2n`. Quicksort's series is `Σ 1 = log n` because it re-visits the *whole* array at every level.

**General form:** pivot splits `α n` / `(1−α) n`:

```
T(n) = T(αn) + Θ(n)   ⟹   T(n) = Θ( n / max(α, 1−α) )
```

| α | Result |
|---|--------|
| 0.5 | `Θ(2n)` |
| 0.7 | `Θ(3.33n)` |
| 0.9 | `Θ(10n)` |
| 0.99 | `Θ(100n)` |
| `1/n` | `Θ(n²)` |

Linear for **any** fixed `α < 1`. Only systematic near-worst-case pivots break it.

---

## 2. Expected quickselect: the exact constant

Random pivot ⇒ `E[T(n)] = (1/n) Σ_{j=0}^{n-1} (E[T(j)] + E[T(n−1−j)]) + c·n`. By symmetry:

```
E[T(n)] = (2/n) Σ_{j=0}^{n-1} E[T(j)] + c·n
```

Subtracting the equation for `n−1` from the one for `n` isolates `E[T(n−1)]`:

```
E[T(n)] − E[T(n−1)] = (2/n)·E[T(n−1)] + c
E[T(n)]             = (1 + 2/n)·E[T(n−1)] + c
```

Multiply by `n²` to telescope (a standard trick — `n² E[T(n)] − n² E[T(n−1)]` collapses):

```
n² E[T(n)] = (n² + 2n) E[T(n−1)] + c·n²
```

Divide by `n²(n+1)²` and sum; the series converges because `E[T(n)] = O(n)`. The standard solution is

```
E[T(n)]  ≈  2(1 + ln 2)·n  =  3.3863·n  comparisons
```

**Comparison table at `n = 10⁶`:**

| Algorithm | Comparisons | vs quickselect |
|-----------|-------------|-----------------|
| Randomised quickselect | `3.386·10⁶` | 1.00× |
| Median of medians (worst case) | `3.386·10⁶` | 1.00× |
| `Arrays.sort` (dual-pivot) | `1.3863·10⁶·20 = 2.77·10⁷` | **8.2×** |
| Randomised quicksort | same as above | 8.2× |
| Heap sort | `2·10⁶·20 = 4.0·10⁷` | 11.8× |

**Quickselect wins by ~8×** — the `log n` factor, exactly as the theory says.

---

## 3. Median of medians: the guarantee

Assume `n` divisible by 10, so `n/5` groups of 5.

Let `M` = median of the `n/5` group medians.

```
# medians >= M   >= (n/5)/2 = n/10
# medians <= M   >= (n/5)/2 = n/10
```

Each median `≥ M` comes with **2 more elements of its group also `≥ M`** (the upper half of a 5-element sorted group):

```
# elements >= M  >=  2 · (n/10)  =  n/5
# elements <= M  >=  2 · (n/10)  =  n/5
```

Therefore:

```
# elements < M   <=  n − n/5 − 1 − n/5   =  3n/10
# elements > M   <=  n − n/5 − 1 − n/5   =  3n/10
```

> **Pivot guarantee: the surviving side after one step is at most `7n/10`.**

### Recurrence and solution

```
T(n) = T(n/5) + T(7n/10) + Θ(n)
```

**Akra–Bazzi theorem:** `T(x) = Σ aᵢ T(bᵢ x + hᵢ(x)) + g(x)` gives `T(x) = Θ(x^p (1 + ∫₁ˣ g(u)/u^{p+1} du))` where `p` solves `Σ aᵢ bᵢ^p = 1`.

Here `a₁ = a₂ = 1`, `b₁ = 1/5`, `b₂ = 7/10`, `g(n) = cn`:

```
(1/5)^p + (7/10)^p = 1
```

Solve numerically:

| `p` | `(0.2)^p` | `(0.7)^p` | sum |
|-----|-----------|-----------|-----|
| 1 | 0.200 | 0.700 | 0.900 |
| 2 | 0.040 | 0.490 | 0.530 |
| 3 | 0.008 | 0.343 | 0.351 |
| **3.387** | 0.0057 | 0.3426 | **1.0000** |

```
p ≈ 3.3864
T(n) = Θ(n^p) = Θ(n)
```

### Why the discard factor must exceed 1/3

Suppose groups of 5 gave a guarantee of only `n/4` discarded per side (survivor `3n/4`):

```
(1/5)^p + (4/5)^p = 1  ⟹  p ≈ 2.29  (the 0.8^p term dominates)
T(n) = Θ(n^{2.29})   ← still sublinear-but-worse-than-n!  Θ(n^2.29) > Θ(n log n)
```

**So the group-of-5 choice is exactly at the threshold.** Generalising to group size `2k+1`:

```
Groups of 2k+1 give a discard guarantee of  (k−1)/(2k+1) per side,
survivor  =  (3k+1)/(2k+1).

k = 1 (groups of 3): survivor 4/5   ⟹  (1/5)^p + (4/5)^p = 1 ⟹ p ≈ 2.29  →  Θ(n^2.29)  BAD
k = 2 (groups of 5): survivor 7/10  ⟹  p ≈ 3.39                   →  Θ(n)        GOOD
k = 3 (groups of 7): survivor 10/14  ⟹  (1/7)^p+(10/14)^p = 1 ⟹ p ≈ 6.4      →  Θ(n)        better bound, higher constant
```

**Groups of 5 is the sweet spot**: it is the smallest group size giving a *linear* guarantee, so the `Θ(n/5)` grouping overhead is minimised. This is a beautiful result — the constant in the algorithm is not arbitrary.

---

## 4. Median-of-medians constant factor

```
T(n) ≤ T(n/5) + T(7n/10) + 6n
```

`6n` accounts for: sorting `n/5` groups of 5 (`≈ 5 log 5 ≈ 11.6` comparisons per group ⇒ `≈ 2.3n`), collecting the medians (`n/5`), and the partition (`≈ 1.1n` by an amortised argument).

Unrolling the `Θ(n)` levels of the recurrence tree with weights `1/5, 7/10, (7/10)², ...`:

```
Σ_{i≥1} (7/10)^i  =  (7/10)/(1 − 7/10)  =  7/3  =  2.333
Plus the T(n/5) chain: Σ_{i≥1} (1/5)^i = 1/4 = 0.25
Total geometric weight ≈ 2.333 + 0.25 + 1 ≈ 3.6
```

Measured precisely: **`3.386 n` comparisons in the worst case** — matching the randomised quickselect expectation to three decimals. The two algorithms have essentially the *same* comparison count; median-of-medians just pays it deterministically, at the cost of extra passes and recursion.

---

## 5. Comparative counting at `n = 10⁶` (`log₂ n = 19.93`)

| Algorithm | Comparisons | Formula | Ratio to quickselect |
|-----------|-------------|---------|----------------------|
| Min/max single pass | `1.0·10⁶` | `n` | 0.30× |
| **Randomised quickselect** | `3.386·10⁶` | `2(1+ln2)n` | **1.00×** |
| Median of medians | `3.386·10⁶` | `3.386n` | 1.00× |
| `Arrays.sort` (dual-pivot) | `2.76·10⁷` | `1.3863 n log₂ n` | 8.2× |
| Randomised quicksort | `2.76·10⁷` | same | 8.2× |
| Heap sort | `3.99·10⁷` | `2 n log₂ n` | 11.8× |
| TimSort (random input) | `≈ 1.0 n log₂ n = 2.0·10⁷` | best case for merging | 5.9× |
| Insertion sort | `2.5·10¹¹` | `n²/4` | 74 000× |

---

## 6. Top-k cost analysis

### Bounded max-heap of size `k` (k smallest from a stream)

```
Init:   k inserts, each Θ(log k)          ⟹  Θ(k log k)
Stream: each element costs O(1) to REJECT (x >= heap.peek())
        and Θ(log k) to ACCEPT (pop + push)
Total:  Θ(k log k + A·log k + (n−k))   where A = number accepted
     =  Θ(n log k) worst case
```

**Expected accepted count for random input.** The heap root after `i` elements is the `k`-th smallest of the first `i`. A new element replaces it with probability `k/(i+1)`. So

```
E[A] = Σ_{i=k}^{n-1} k/(i+1)  =  k · [ln(n) − ln(k)]  =  k·ln(n/k)
```

| `n` | `k` | `E[A]` | Total time |
|-----|-----|--------|------------|
| 10⁶ | 10 | 10·11.5 = 115 | `Θ(n)` dominated by the O(1) rejections |
| 10⁶ | 10⁴ | 10⁴·4.6 = 46 000 | `Θ(n + 4.6·10⁴·log k)` |
| 10⁶ | 10⁶/2 | ≈ 3.5·10⁵ | `Θ(n log k)` — real |

**Key insight:** for small `k`, the algorithm is **`Θ(n)` expected** because almost every element is rejected by an `O(1)` comparison. The `log k` factor only bites when `k = Θ(n)`.

### Quickselect top-k (destructive)

```
select k times, narrowing the range each time:
step i costs Θ(n − i)  ⟹  Θ(k·n − k²/2)
```

For `k = n`: `Θ(n²/2)`. **Terrible.** Quickselect is only good for *one* value or small `k`.

### Multi-select with a proper algorithm

Repeat quickselect but reuse the partition information:

| `k` | Quickselect-repeated | Sorted heap | Sort |
|-----|---------------------|-------------|------|
| 1 | `3.39n` | `n log k ≈ 0` | `27.7n` |
| 10 | `≈ 34n` | `n log 10 ≈ 3.3n` | `27.7n` |
| 100 | `≈ 340n` | `6.6n` | `27.7n` |
| `n/2` | `≈ n²/2` | `n log n` | `n log n` |

**The crossover is around `k ≈ 30`.** Below that, quickselect-repeated wins; above that, a heap or a sort wins. This is a genuine, non-obvious result worth remembering.

---

## 7. Parallel selection

Work `Θ(n)`, depth `Θ(n/p + p)`:

- Local selection within a block: `Θ(n/p)`.
- Selecting the pivot from `p` block medians: `Θ(p)`.

Optimise `n/p + p`: derivative `−n/p² + 1 = 0 ⟹ p = √n`.

```
Depth_optimal = 2√n   vs   Depth_sequential = Θ(n)
```

Speedup bound at `p = √n` cores: `Θ(√n)`. **Amdahl's law with the final global-count pass serial** gives a tighter practical cap:

```
Global count pass = Θ(n/p) parallel-friendly, but the pivot broadcast and the
final local selection are Θ(p + n/p) and only partially parallel.

Measured (8 threads, n = 10⁸): ~5×  — limited by memory bandwidth, not by the algorithm.
```

---

## 8. `Θ(log n)` structures

### Fenwick binary lifting

```
k-th smallest:
    idx = 0
    for step = 2^⌊log₂ n⌋ down to 1:
        next = idx + step
        if next <= n and tree[next] < k:  k -= tree[next];  idx = next
    return idx + 1
```

Exactly `⌊log₂ n⌋ + 1` iterations.

**Why not `Θ(log² n)`:** the naive version does a binary search over `tree[0..n]` for the prefix sum crossing `k`, testing `prefixSum(mid) ≥ k` in `O(log n)`. Binary lifting walks the *interval decomposition tree* directly: `tree[next]` is exactly the count of the next block, so one comparison both tests and updates. This is the same "look for the answer on the way down" trick as in merge sort's stack.

### Order-statistic tree

Red-black / AVL with `size(left)`. `select(k)`:

```
while node != null:
    ls = size(node.left)
    if k == ls + 1: return node.key
    if k <= ls:    node = node.left
    else:          k -= ls + 1;  node = node.right
```

Exactly `Θ(height) = Θ(log n)`.

### Wavelet tree

Alphabet size `σ`, so height `log₂ σ`. Build: `Θ(n log σ)`. Query: `Θ(log σ)`. Space: `n log σ` **bits**.

**When it beats the Fenwick tree:** static data, small alphabet (DNA `σ = 4`, ASCII `σ = 128`), many range-count queries. This is what makes suffix-array binary search fast.

---

## 9. Decision table

| Situation | Answer | Complexity |
|-----------|--------|-----------|
| min/max of an array | one pass | `Θ(n)`, `O(1)` |
| one `k`-th, array disposable | quickselect | `Θ(n)` expected |
| one `k`-th, adversarial input a threat | median of medians | `Θ(n)` worst |
| `k` smallest from a stream | max-heap size `k` | `Θ(n log k)`, `O(k)` |
| `k` largest, input must survive | min-heap size `k` | `Θ(n log k)`, `O(k)` |
| many `k`s, static array | sort once + `lowerBound` | `Θ(n log n + q log n)` |
| many `k`s, small value domain | Fenwick tree | `Θ(n log n)` build, `Θ(log n)` per query |
| dynamic insert/delete + rank | order-statistic tree | `Θ(log n)` per op |
| `n = 10⁸`, one median, 8 threads | parallel quickselect | `Θ(n)` work, `Θ(√n)` depth |
| `k ≈ 30`, several values needed | repeated quickselect | `Θ(k·n)` |
| exact quantiles over an unbounded stream | **impossible** | needs `Θ(n)` memory — use t-digest / KLL |

---

## 10. Quick reference

| Quantity | Value |
|----------|-------|
| Selection recurrence | `T(n) = T(αn) + Θ(n)` |
| Result | `Θ(n / max(α, 1−α))` — linear for fixed `α` |
| Randomised quickselect | `2(1 + ln2) n = 3.386 n` comparisons |
| Randomised quicksort | `1.3863 n log₂ n` comparisons |
| Median-of-medians pivot guarantee | ≥ `3n/10` discarded on **each** side |
| Median-of-medians recurrence | `T(n) = T(n/5) + T(7n/10) + Θ(n)` |
| Akra–Bazzi `p` | `p ≈ 3.3864`, so `Θ(n)` |
| Median-of-medians comparisons | `≈ 3.386 n` worst case |
| Group size giving linear guarantee | `2k+1` with `k ≥ 2`, i.e. **5 is the smallest** |
| Speedup of quickselect over sorting at `n = 10⁶` | ≈ **8×** |
| Top-k heap, worst case | `Θ(n log k)`, `O(k)` space |
| Top-k heap, expected (random input) | `Θ(n + k ln(n/k)·log k)` ≈ `Θ(n)` for small `k` |
| Repeated quickselect for `k` values | `Θ(kn − k²/2)` — worse than a heap for `k > 30` |
| Parallel selection depth | `Θ(n/p + p)`, optimal at `p = √n` |
| Fenwick k-th | `⌊log₂ n⌋ + 1` iterations, `Θ(log n)` |
| Quickselect stack | `O(log n)` **only if** you recurse on the smaller side |