# 04 — Linear-Time Sorts

<div align="center">

**Counting Sort · Radix Sort · Bucket Sort · LSD/MSD Variants · Hybrid Sorts**

</div>

---

## Learning Objectives

- Recognise when a problem admits an `O(n + k)` solution by exploiting key *range* rather than comparison
- Implement counting sort correctly, including the off-by-one that silently drops the minimum
- Implement LSD radix sort and explain why the pass order must be least-significant-digit-first
- Implement MSD radix sort and explain its Θ(n) count-sort advantage and its stack cost
- Derive radix sort's `Θ(d · (n + b))` bound and compute the crossover against `Θ(n log n)`
- Design a hybrid: introsort for long runs, radix for short digit keys
- State precisely why these algorithms are *not* comparison sorts and what that implies

## Prerequisites

- `02-divide-conquer-sorts` for the `Θ(n log n)` baseline
- Digit extraction: bit shifts and masks for radix `2^k`
- The information-theoretic bound from `MATH_FOUNDATION.md` of lab 02

## Estimated Time

- **Theory**: 90 minutes
- **Practice**: 135 minutes
- **Exercises**: 75 minutes
- **Total**: 5–6 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| Non-comparison sort | Learns information about keys beyond pairwise comparison — escapes the `log₂(n!)` bound |
| Key range `k` | Number of distinct values the keys can take (counting/bucket) or the base `b` (radix) |
| Prefix sum | Converts frequency counts into cumulative *end positions* — the crux of counting sort |
| Stability | Counting sort is stable **iff** you accumulate from input forward or scan backward |
| LSD radix | Sort by digit `0`, then digit `1`, ... — requires a **stable** inner sort |
| MSD radix | Sort by digit `d-1` first, then recurse per bucket — doesn't need stability |
| Passes `d` | Number of digits: `d = ⌈log_B (maxValue+1)⌉` for base `B` |
| Base choice | `B = 10^k` (decimal) or `B = 2^k` with `k` chosen so `B ≈ √n` |
| Crossover | Radix beats comparison sorting when `n` is large and keys are fixed-width integers |
| `Introsort`-style hybrid | Detect a monotonic run, insertion-sort it, then radix the remainder |

## Complexity Snapshot

| Algorithm | Best | Average | Worst | Space | Stable | Key assumption |
|-----------|------|---------|-------|-------|--------|-----------------|
| Counting sort | `Θ(n + k)` | `Θ(n + k)` | `Θ(n + k)` | `Θ(k)` | Yes* | keys in `[0, k)` |
| Radix sort (LSD, base `B`) | `Θ(d(n + B))` | `Θ(d(n + B))` | `Θ(d(n + B))` | `Θ(n + B)` | Yes | fixed-width integer keys |
| Radix sort (MSD) | `Θ(n log n)` worst | — | `Θ(n(B/log n)^{log_B d})` | `Θ(n + B)` | Yes | as above |
| Bucket sort (uniform) | `Θ(n)` | `Θ(n)` | `Θ(n²)` | `Θ(n)` | Yes | uniform distribution |
| TimSort (adaptive) | `Θ(n)` | `Θ(n log n)` | `Θ(n log n)` | `Θ(n)` | Yes | run structure |
| Hybrid introsort+radix | `Θ(n log n)` | `Θ(d(n+B))` | `Θ(n log n)` | `Θ(n+B)` | Yes | either regime |

\* Counting sort is stable iff the scatter loop reads the input **forward** (with cumulative ends) or **backward** (with cumulative starts).

## Algorithms Covered

### Counting Sort (Two-Pass)
1. **Count.** `count[v]++` for every key `v`.
2. **Prefix-sum.** `count[v] += count[v-1]` → `count[v]` is now the *end position* for value `v`.
3. **Scatter.** Walk the input **backward**: `out[--count[v]] = a[i]`.

`Θ(n + k)` time, `Θ(k)` space. **Trap:** iterating the scatter loop forward with cumulative *starts* also works and is equally stable — mixing the two conventions is the #1 bug.

### Radix Sort (LSD)
```
for (p = 0; p < d; p++)          // p = 0 is the LEAST significant digit
    stableCountingSort(a, digit = (key >> (p * k)) & (B - 1))
```
- **Why LSD first:** after the first pass, keys are sorted by digit 0. The second pass is stable, so it sorts by digit 1 *while preserving* digit-0 order. Hence by induction the array is sorted after pass `d`.
- **Proof sketch:** let `P(p)` = "after `p+1` passes, `a` is sorted by the lowest `p+1` digits". `P(0)`: digit-0 sorting. `P(p) ⇒ P(p+1)`: pass `p+1` stably sorts by digit `p+1`; among keys with equal digit `p+1` values the previous order (by lower digits) is preserved. ∎

### Radix Sort (MSD)
```
countingSortByDigit(a, 0, n, d-1)
  → then recurse on each bucket with digit d-2
```
- **Advantage:** the first pass is a single Θ(n) counting pass; recursion on tiny buckets is cheap. **No stability requirement** — each bucket is solved independently, so you can use an unstable inner sort.
- **Cost:** recursion depth `d` and per-level bucket overhead. MSD alone is *not* faster for short keys; the win comes from using a comparison sort on small buckets (a common hybrid).

### Bucket Sort
1. Compute min/max; bucket width `w = (max - min + 1) / k`.
2. Distribute each key into `⌊(key - min) / w⌋`.
3. Sort each bucket with insertion sort (buckets are `O(n/k)` on average).
4. Concatenate in bucket order.

`Θ(n)` expected, **`Θ(n²)` worst case** (all keys in one bucket). Only worth it under a distributional assumption.

### Base selection for radix sort
`Θ(d(n + B))` with `B = 2^k` and `d = ⌈32/k⌉` for 32-bit keys. Optimise `k`:

```
cost(k) = (32/k) · (n + 2^k)
d(cost)/dk = 0  ⟹  32·2^k = 32n  ⟹  2^k = n  ⟹  k = log₂ n
```

**Optimal base `B ≈ n`**, giving `Θ(n · log_B n)`. For `n = 10⁶` (20 bits), `B = 2²⁰ = 1 048 576` — a single pass, but a 4 MB count array. The memory/cache trade usually pushes practitioners to `B = 2¹¹ = 2048` (3 passes, 8 KB counts that stay in L1).

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/linear-sorts/` | Counting, radix (LSD/MSD), bucket implementations |
| `src/test/java/com/alglab/linear-sorts/` | JUnit 5 tests |
| `SOLUTION/` | Worked exercise solutions |
| `TESTS/` | Negative-value, huge-key, all-duplicate suites |
| `BENCHMARK/` | Radix vs `Arrays.sort` crossover curve |
| `MINI_PROJECT/` | Digit-visualising sorter |
| `REAL_WORLD_PROJECT/` | Radix-partitioned shuffle for a database index build |
| `CHALLENGE/` | American-flag / inplace MSD radix, parallel radix |
| `DIAGRAMS/` | LSD pass diagrams, bucket distribution plots |