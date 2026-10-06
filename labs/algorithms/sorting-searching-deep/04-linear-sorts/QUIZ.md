# Quiz — Linear-Time Sorts

15 questions. Each key gives the reason.

---

## Q1
Why can counting sort beat the `Ω(n log n)` lower bound, which no comparison sort can beat?

<details><summary>Answer</summary>

The bound applies to **comparison sorts only**. It assumes the only operation available is "which of these two keys is larger?", which yields 1 bit.

Counting sort performs `count[key]++` — an array increment that reveals `log₂ k` bits about that element's identity *and* simultaneously aggregates information about the whole multiset. That is strictly more information per operation.

**Generalisation:** each non-comparison sort's runtime is set by a different property of the input (key range, key *width*, distribution), not by `log₂(n!)`.
</details>

## Q2
Counting sort is `Θ(n)`. Is that right?

<details><summary>Answer</summary>

**No — it is `Θ(n + k)`**, where `k` is the key range.

The prefix-sum pass costs `Θ(k)`. With 32-bit keys and a wide spread, `k` can be `2³²`, so the count array needs 17 GB.

It is `Θ(n)` only when **`k = Θ(n)`**. Always write `k = max - min + 1`, never `k = max`.
</details>

## Q3
State the stability condition for counting sort precisely.

<details><summary>Answer</summary>

Stability holds **iff** the scatter direction and prefix-sum convention are matched:

- **inclusive** prefix (`count[v]` = index one past the last slot of `v`) + **backward** scan (`out[--count[a[i]]] = a[i]`), or
- **exclusive** prefix (`count[v]` = start slot of `v`) + **forward** scan (`out[count[a[i]]++] = a[i]`).

Mixing them (inclusive + forward) is **unstable** yet still produces a sorted array — so only a stability test catches it.
</details>

## Q4
Why must LSD radix sort process the least significant digit first? What breaks if you reverse it?

<details><summary>Answer</summary>

LSD correctness rests on **stability**: after pass `p`, the array is sorted by `(digit_p, …, digit_0)`. Pass `p+1` stably sorts by `digit_{p+1}`, and among keys with equal `digit_{p+1}` the previous order is preserved — which is what makes the lower digits still meaningful.

Reversing the order (MSD-first, LSD style) sorts by the *dominant* digit first and then re-stably-sorts by less significant digits, which **destroys** the higher-digit ordering. Example: `[3, 24]` with 10-bit digits — sorting by the high digit leaves `3` before `24`, then the low-digit pass does nothing.
</details>

## Q5
Give the recurrence for MSD radix sort and its worst case.

<details><summary>Answer</summary>

```
T(n, d, B) = Θ(n + B) + T(n_max, d − 1, B)
```

**Worst case:** all keys identical ⇒ one bucket of size `n` at every level ⇒ `T = d·Θ(n + B) = Θ(n · w / log₂ B) = Θ(n log_B n)` — **no better than a comparison sort**.

This is why every real implementation adds a small-bucket cutoff that switches to a comparison sort, giving `Θ(n(1 + log_B C))`.
</details>

## Q6
Derive the optimal radix base. What is the catch?

<details><summary>Answer</summary>

With `B = 2^k` and `d = ⌈w/k⌉`, cost is `(w/k)(n + 2^k)`. Differentiating gives `k ln2 · 2^k = n`, i.e. **`2^k ≈ n`**, so `B ≈ n`.

Substituting: cost `≈ Θ(n · w / log₂ n)`, a speedup of `(log₂ n)² / w` over comparison sorting.

**The catch:** `B ≈ n` means a count array as large as the input — cache-hostile. In practice you choose `B` so the count array fits in L1 (`2¹¹` = 8 KB for 32-bit keys), and the measured speedup drops from ~12× to 2–4×. The model counts operations, not memory traffic.
</details>

## Q7
Why does counting sort fail catastrophically on `int[] {0, Integer.MAX_VALUE}` and what is the fix?

<details><summary>Answer</summary>

`k = 2³¹`, so `new int[k]` demands 8 GB. You get `OutOfMemoryError` (or severe GC thrashing before that).

**Fixes:**
1. Guard: `if (k > C·n) reject` and dispatch to radix sort instead.
2. Use a `long`-keyed **hash-based** count (`O(d)` space for `d` distinct values, expected `Θ(n)` time).
3. Radix sort by high bits first (MSD), which never allocates more than `B` counts regardless of the value range.

Rule: **counting sort requires `k = O(n)`**.
</details>

## Q8
Signed radix sort: why does `x ^ 0x80000000` make unsigned digit extraction correct?

<details><summary>Answer</summary>

It flips the sign bit, mapping the signed range `[-2³¹, 2³¹)` onto the unsigned range `[0, 2³²)` **order-preservingly**. Two's-complement negatives (`1…1`) become small unsigned values and positives become large ones, so signed ascending order equals unsigned ascending order of flipped keys.

`x ^ 0x80000000` is an involution, so the same operation maps back. For `long` keys use `^ Long.MIN_VALUE` and `>>>` (not `>>`).
</details>

## Q9
Bucket sort is `Θ(n)`. Under what conditions is that statement false, and by how much?

<details><summary>Answer</summary>

It assumes keys are i.i.d. uniform. If a fraction `α` of the range holds the keys, the effective bucket count is `αk` and

```
E[T] = αk · Θ((n/αk)²) = Θ(n²/(αk)) = Θ(n/α)     with k = n
```

| `α` | Time |
|-----|------|
| 1 | `Θ(n)` |
| 0.01 | `Θ(100n)` |
| 10⁻⁴ | `Θ(10⁴n)` — **worse than `Θ(n log n)`** |

Gaussian keys give `Θ(n^1.5)` because only `Θ(√n)` buckets are occupied.
</details>

## Q10
LSD radix needs stability; MSD does not. Explain.

<details><summary>Answer</summary>

LSD processes less significant digits first, so the ordering established by earlier passes must *survive* later passes — that is exactly what stability guarantees.

MSD processes the most significant digit first and then **recurses independently into each bucket**. The buckets are physically separated, so within a bucket the previous passes' ordering is irrelevant — the recursion re-derives it. Hence MSD can use an unstable, faster inner sort (and it does: it switches to a comparison sort).
</details>

## Q11
Why does sorting `String[]` with MSD radix work but LSD radix does not?

<details><summary>Answer</summary>

LSD needs `d = max length` because it processes every digit of every key. One 1 MB string makes `d = 10⁶` — 10⁶ full-array passes. Catastrophic.

MSD descends by character position and **terminates per string** when the bucket contains one string, so cost is proportional to the *total* number of characters, `Θ(Σ|sᵢ|)`, not `n · max|s|`.

Treat a sentinel `0` byte as the smallest digit so that string termination is naturally handled.
</details>

## Q12
Given `n = 10⁶` 32-bit keys and a 32 KB L1 cache, what radix configuration do you pick and why?

<details><summary>Answer</summary>

**`k = 11` bits per digit, `B = 2048`, `d = 3`.**

The count array is `2048 × 4 B = 8 KB` — comfortably L1-resident, so the prefix-sum pass never misses. `k = 16` needs only 2 passes but a 256 KB count array, which spills into L2 and adds ~4 extra cache lines per bucket; the saved pass does not compensate on most machines. `k = 8` fits L1 trivially but needs 4 passes, i.e. 4× the memory traffic.

Verify on your hardware — this optimum is not portable. And measure: `Arrays.sort` may still win at `n = 10⁶`.
</details>

## Q13
Your keys are `BigInteger` of at most 512 bits. Can radix sort help?

<details><summary>Answer</summary>

**Yes.** Radix cost depends on the key **width** `w` (known, fixed), not the key **value**. With `B = 2¹¹` and `w = 512`, `d = 47` passes — a lot, but still `Θ(47n)` with **no comparison and no allocation beyond two `BigInteger[]` buffers**.

Better: convert once to `long[8]` limbs, radix sort by limb with `w = 64`, `d = 6` — then the keys are 64-bit. Extract the limbs once with `bitLength`/`getBits` rather than `compareTo`.

The trap is reaching for `compareTo` because "BigIntegers are big" — the bit length is a known parameter; the value is not.
</details>

## Q14
A reviewer claims "radix sort is `O(n)` so it's always the fastest sort." Refute.

<details><summary>Answer</summary>

Three independent reasons:

1. **`O(n)` hides constants.** Radix is `Θ(d(n + B))` — `d` passes, each touching the whole array **three times** (count, scatter, copy-back). For `d = 3`, that is 9 full array traversals. `Arrays.sort` does ~`1.39 n log₂ n = 27n` comparisons but only ~1–2 traversals with perfect locality.

2. **Below the crossover, radix loses.** Measured crossover for `int[]` is `n ≈ 3·10⁴`. At `n = 10³` the `d` passes' setup dominates.

3. **The bound only applies to fixed-width integer keys.** For `String`, `Record`, or a `Comparator`-defined ordering, radix sort does not apply at all, and you are back to `Θ(n log n)`.

**Also:** the `B ≈ n` optimum requires an `O(n)` count array, so for `n = 10⁹` the "optimal" configuration allocates 4 GB.
</details>

## Q15
Your input is `10⁸` 64-bit row IDs, near-random, built into a database index. LSD or MSD?

<details><summary>Answer</summary>

**MSD with a small-bucket cutoff**, and chunk the work:

- **Near-random IDs** ⇒ after 1–2 high digits, buckets are near-singletons, so MSD terminates after ~2 levels: `Θ(n)` total. LSD must do all `d = ⌈64/k⌉ ≈ 6` passes regardless.
- **MSD's first pass is a single `Θ(n)` counting scatter** — the best possible locality.
- **Chunk for parallelism:** split by high bits first (that *is* the MSD first pass), then sort each bucket independently on separate threads. Each bucket is contiguous, so each thread works on its own slice with no coordination. This is the standard database technique and it is why MSD beats LSD for index builds.
- **Memory:** MSD allocates a buffer per recursion level, so keep the cutoff at 64–256 to bound it to 2–3 levels.

LSD's advantage (trivially parallel per pass, no recursion) is outweighed here because the work per pass is already small relative to the index-build I/O.
</details>