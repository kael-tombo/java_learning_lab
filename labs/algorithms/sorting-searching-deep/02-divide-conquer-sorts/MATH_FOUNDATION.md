# Math Foundation — Divide & Conquer Sorts

The algebra behind `Θ(n log n)`: recurrences, the Master theorem, and the entropy argument that shows `n log n` is unavoidable.

---

## 1. The recurrence template

Any D&C algorithm fits:

```
T(n) = a · T(n/b) + f(n),      T(1) = Θ(1)
```

| Symbol | Meaning | Merge sort | Quick sort (balanced) | Quick sort (worst) |
|--------|---------|-----------|----------------------|--------------------|
| `a` | number of subproblems | 2 | 2 | 1 |
| `b` | shrink factor | 2 | 2 | 1 |
| `f(n)` | non-recursive work | `n` (merge) | `n` (partition) | `n` |

---

## 2. Master theorem

If `f(n) = Θ(n^k)` and `T(1) = Θ(1)`, with `a ≥ 1, b > 1`:

| Case | Condition | Solution |
|------|-----------|----------|
| 1 | `n^k < n^(log_b a)` i.e. `k < log_b a` | `Θ(n^(log_b a))` — recursion dominates |
| 2 | `k = log_b a` | `Θ(n^(log_b a) · log n)` — balanced, `log n` levels |
| 3 | `k > log_b a` | `Θ(n^k)` — the leaf work dominates |

**Merge sort verification.** `a=2, b=2, k=1`. `log₂2 = 1 = k` → **Case 2** → `Θ(n¹ log n) = Θ(n log n)`. ✓

**Binary search verification.** `a=1, b=2, k=0`. `log₂1 = 0 = k` → Case 2 → `Θ(log n)`. ✓ (A beautiful sanity check: binary search is the *same* recurrence shape with one subproblem.)

**Quick sort verification.** `a=2, b=2, k=1` → Case 2 → `Θ(n log n)`. ✓

---

## 3. Unrolling the merge sort recurrence

Expand by levels:

```
T(n) = 2T(n/2) + n
     = 2[2T(n/4) + n/2] + n
     = 4T(n/4) + 2n
     = 8T(n/8) + 4n
     = ...
     = 2^d T(n/2^d) + d·n
```

Set `d = log₂ n` so `n/2^d = 1`:

```
T(n) = n·T(1) + n·log₂ n  =  Θ(n log n)
```

**The two contributions**, and they are both irreducible:
- **`n·T(1)`** — the work at the leaves. Every element is a base case exactly once.
- **`n·log₂ n`** — the work at the `log₂ n` internal levels, `Θ(n)` each.

The `log n` factor is literally the **depth of the recursion tree**. Any comparison sort whose tree is balanced pays `n` per level for `log₂ n` levels.

---

## 4. Quick sort: the balance equation

Let `k` be the size of the left partition:

```
T(n) = T(k) + T(n-k-1) + cn
```

**Perfect balance** (`k ≈ n/2`): Case 2 → `Θ(n log n)`.
**Degenerate** (`k = 0`): `T(n) = T(n-1) + cn`. Unroll:

```
T(n) = T(1) + c·Σ_{i=2}^{n}(i)  ≈  c·n²/2  =  Θ(n²)
```

The swap sum `1 + 2 + ... + n` is the signature of a degenerate partition. **This is why the pivot matters more than the partition code.**

**Randomised expected case.** For a uniform random pivot:

```
E[T(n)] = (1/n)·Σ_{j=0}^{n-1} [ E[T(j)] + E[T(n-1-j)] ] + cn
        = (2/n)·Σ_{j=0}^{n-1} E[T(j)] + cn
```

Guess `E[T(n)] = α·n·log₂ n`. Substitute and check:

```
(2/n)·Σ_{j=0}^{n-1} α j log₂ j  +  cn
≈ (2α/n)·(n²/2)(log₂ n - 1/ln 2) + cn
≈ α n log₂ n - (α/ln 2) n + cn
```

Equating the `n log₂ n` terms requires `1 - 1/ln 2 < 0`, false, so the bound must be scaled:

```
E[T(n)] ≤ 1.3863 · n · log₂ n   (worst-case expected constant)
```
where `1.3863 = 2/ln 2 · 1/2`. This is the **expected constant factor of randomised quick sort**. In practice the average is ≈ `1.39 n log₂ n` comparisons, close to the information-theoretic floor of `≈ 1.0 n log₂ n`.

---

## 5. 3-way quick sort: `Θ(n log d)`

With `d` distinct values and a random pivot:

- Each partition places the pivot value into the final `== v` region; that region is never revisited.
- The remaining work is like a quicksort on `d` "super-values" of weight `≤ n/d`.
- Expected comparisons: **`Θ(n log d)`** — the classic Bentley–Sedgewick bound.

| `d` | `log₂ d` | Relative to all-distinct |
|-----|----------|---------------------------|
| 2 | 1 | 6× fewer comparisons |
| 10 | 3.3 | 5× fewer |
| 1 000 | 10 | 1.7× fewer |
| 10⁶ | 20 | 1× (no benefit) |

For `d = 2` (booleans, low-cardinality enums) 3-way quicksort is essentially **one linear pass** — an enormous practical win over 2-way quicksort's Θ(n²).

---

## 6. The information-theoretic lower bound

A deterministic comparison sort induces a **binary decision tree** of depth `d`. A binary tree of depth `d` has at most `2^d` leaves. There are `n!` permutations of `n` distinct keys and the tree must distinguish all of them:

```
2^d ≥ n!   ⟹   d ≥ log₂(n!)
```

By Stirling's approximation:

```
n! = √(2πn)·(n/e)ⁿ·(1 + 1/(12n) + ...)
log₂(n!) = n log₂ n - n log₂ e + ½ log₂(2πn) + O(1/n)
         ≈ n log₂ n - 1.4427 n + ½ log₂(2πn)
```

**Numbers:**

| `n` | `log₂(n!)` | `n log₂ n` | ratio |
|-----|-----------|------------|-------|
| 10 | 21.79 → 22 | 33.22 | 0.66 |
| 100 | 524.76 → 525 | 664.39 | 0.79 |
| 1 000 | 8 528.6 → 8 529 | 9 965.8 | 0.86 |
| 10⁶ | 19 521 558 | 19 931 569 | 0.98 |

**Conclusion.** The `n log n` factor is not an artefact of merge sort's structure — it is the number of bits of information in a permutation (`log₂(n!)` bits, by definition of entropy). Only **non-comparison sorts** escape it, by reading keys more informatively than pairwise comparison (counting/radix sort on bounded keys, or hashing).

**Asymptotic optimality of merge sort.** Worst-case mergesort satisfies `⌈log₂ n!⌉ ≤ C(n) ≤ ⌈log₂ n!⌉ + 2n` for `n ≥ 2` — within `O(n)` of the lower bound. So merge sort is *asymptotically optimal* in the comparison model.

---

## 7. Inversions, and the adaptive bound

Insertion sort's work is exactly `n - 1 + inv(a)` where `inv(a)` is the inversion count. Merge sort computes `inv(a)` in `Θ(n log n)` by the standard merge counting:

```
when a[i] > a[j] (take from right):  inv += (mid - i + 1)
```

**Natural merge sort / TimSort** is therefore adaptive: input with `k` ascending runs costs `Θ(n log k)`, and `k = 1` gives **Θ(n)**.

**Organ-pipe adversary.** The maximum of `inv(a)` is `n(n-1)/2`, attained by reverse-sorted input, which is why non-adaptive sorts have no hope on adversarial data.

---

## 8. Space and the in-place question

Merge sort's `Θ(n)` buffer is not incidental — it is what makes the merge linear.

- **Merge without a buffer** requires alternating *forward* and *backward* passes through the two runs (like in-place quicksort or the "cycle-leader" in-place merge), which takes `Θ(n log n)` per level → `Θ(n log² n)` total. **In-place merge is possible but asymptotically worse.**
- Quick sort gets its in-place property from partitioning, which permutes within a single array — no second buffer, no log factor.

Amortised accounting for the buffer: you can *reuse* one global `aux` array across calls (the recursion is depth-first and each merge completes before its parent's), so peak memory is `Θ(n) + Θ(log n)`, not `Θ(n log n)`.

---

## 9. Cost-model constants (why quicksort wins in practice)

Asymptotic equality hides a factor of ~1.4–2 in *bytes touched*:

| Algorithm | Bytes touched per element per level |
|-----------|--------------------------------------|
| Merge sort | `4` read (`a`) + `4` write (`aux`) + `4` read (`aux`) + `4` write (`a`) = **16 B** |
| Quick sort | `4` read + ≤`8` write (swap) = **~12 B** |
| Quick sort (Hoare) | `4` read + ≤`4` write = **~8 B** |

At 10 GB/s effective bandwidth and `n = 10⁸` `int`s (400 MB), merge sort moves ≈ 1.6 GB/level × 27 levels ≈ 43 GB ≈ **4.3 s** of pure memory traffic; Hoare-partitioned quicksort moves roughly half that. This is the entire empirical case for quicksort, and it is *not* visible in the O() notation.

---

## 10. Quick reference

| Question | Answer |
|----------|--------|
| Merge sort recurrence | `2T(n/2) + Θ(n)` |
| Master theorem case | Case 2 (`k = log_b a = 1`) |
| Result | `Θ(n log n)` |
| Worst-case quick sort recurrence | `T(n-1) + cn` → `Θ(n²)` |
| Randomised quick sort expected | `≤ 1.3863 · n log₂ n` comparisons |
| 3-way quick sort | `Θ(n log d)`, `d` = distinct values |
| Lower bound | `⌈log₂(n!)⌉ ≈ n log₂ n - 1.4427 n` |
| Merge sort's gap to the bound | `O(n)` — asymptotically optimal |
| Insertion sort work | `n - 1 + inv(a)` |
| Natural merge sort work | `Θ(n log k)`, `k` = number of runs |
| In-place merge cost | `Θ(n log² n)` — strictly worse |
| Peak memory, top-down array merge | `Θ(n)` buffer (reused) + `Θ(log n)` stack |