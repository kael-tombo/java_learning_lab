# Quiz — Bit Sort & Search

15 questions. Each key gives the reason.

---

## Q1
Why can a bitset set intersection be 64× faster than a `HashSet` intersection, and when is it *slower*?

<details><summary>Answer</summary>

A bitset of `n` bits is `n/64` words, so `A & B` is `Θ(n/64)` word operations. `HashSet.intersection` is `Θ(min(|A|,|B|))` with hashing and boxing.

**Faster** when the sets are dense: `|A| ≳ n/64`. Memory is also `n/8` bytes vs ~48 B/entry — **384× smaller**.

**Slower** when sparse: for `|A| = n/1000`, the bitset costs `n/64 + n/1000 ≈ 0.0166n` vs the hash set's `0.001n` — **16× slower**. Iterating elements is the clearest example: `Θ(n/w + |A|)` vs `Θ(|A|)`.
</details>

## Q2
Branchless partition uses ~8 ALU ops per element vs ~3 for the branchy version, yet it is faster. Explain.

<details><summary>Answer</summary>

**Cycles, not instructions.** At a random partition the branch is ~50% unpredictable, costing ~15–20 cycles per misprediction. Expected cost `≈ 3 + 0.5·17 ≈ 11.5` cycles/element.

Branchless: 8 ops with instruction-level parallelism of ~2–3 ops/cycle ⇒ **~3 cycles/element**.

So branchless executes 2.7× more instructions in **3–4× fewer cycles**. This is the canonical "performance ≠ operation count" example and the reason `Arrays.sort`'s intrinsics win by more than their algorithmic advantage.
</details>

## Q3
`k ^ (k-1)`, `k & (k-1)`, `k & -k` — state the effect of each, and the arithmetic reason.

<details><summary>Answer</summary>

Subtracting 1 from `k`: the lowest set bit (at position `t`) goes to 0, and all bits below `t` (which were all 0) go to 1. Higher bits are unchanged.

| Expression | Effect |
|-----------|--------|
| `k & (k-1)` | clears the lowest set bit |
| `k ^ (k-1)` | yields exactly the bits at and below position `t` |
| `k & -k` | isolates bit `t` (`-k = ~k + 1`) |

**Derived:** `k > 0 && (k & (k-1)) == 0` ⟺ power of two. `for (x = k; x != 0; x &= x-1)` visits each set bit once in `Θ(popcount(k))`.
</details>

## Q4
`numberOfTrailingZeros(0)` returns 32. Why is this the most common bit-operation crash?

<details><summary>Answer</summary>

It is **not an exception** — it returns `w` by design, so the compiler is happy and the code compiles. The failure appears much later as an `ArrayIndexOutOfBoundsException` at an unrelated line, or worse, as a silent wrong index.

Compare with `divideByZero`, which throws immediately and points at the cause.

**Rules:** `numberOfTrailingZeros` / `numberOfLeadingZeros` need a `!= 0` guard; `highestOneBit(0)` returns `0`; `lowestOneBit(0)` returns `0`. **All three have different zero behaviour — memorise it.**
</details>

## Q5
Bitwise partition sort's real complexity on random data, and why the bit-sort does not beat `Arrays.sort`.

<details><summary>Answer</summary>

**`Θ(n · min(log₂ n, w))`.** Only the first `log₂ n` bits produce multi-element buckets; the remaining `w − log₂ n` levels each visit at most one element and stop at the cutoff.

It uses **zero comparisons**, but `Arrays.sort(int[])` is an **intrinsified** dual-pivot quicksort: the JIT emits machine code with no bounds checks, which no amount of branchless cleverness in Java source can match.

Measured: branchless bit sort ≈ 620 ms vs `Arrays.sort` ≈ 75 ms on `int[10⁶]`. The technique is worth knowing (it is the basis of radix-partitioning in databases and of GPU sorting networks) but it does not win in Java.
</details>

## Q6
Signed vs unsigned: why does a bit trie come out in the wrong order?

<details><summary>Answer</summary>

Trie traversal compares bit strings from the MSB down — that is **unsigned** lexicographic order. Java's `Integer.compare` is **signed**.

So `-1` (all ones) sorts as `0xFFFFFFFF` = the largest value in the trie, but as `-1` it is the smallest under `Integer.compare`.

**Fix:** insert and search `key ^ Integer.MIN_VALUE`. That flip is involutive and order-preserving, mapping signed order onto unsigned order.
</details>

## Q7
Plain trie vs Patricia trie: node counts and when each is viable.

<details><summary>Answer</summary>

A plain trie over `n` random `w`-bit keys has `≈ n(w − log₂ n) + 2n` nodes — for `w = 64`, `n = 10⁸`: `~5·10⁹` nodes ≈ **41 GB**. Infeasible.

A **Patricia (compressed) trie** stores only branching points: `≤ 2n − 1` nodes ⇒ 32 MB for `n = 10⁶`. It also searches in `Θ(log n)` rather than `Θ(w)`.

**Rule:** plain trie for `n < 10⁴` or `w ≤ 16`; Patricia or a sorted array + `lowerBound` above that.
</details>

## Q8
What can a bit trie do that a `HashMap` cannot, and at what cost?

<details><summary>Answer</summary>

**Can:** `ceiling(k)`, `floor(k)`, predecessor/successor, ordered iteration, range scans — all `Θ(log n)` (Patricia) or `Θ(w)` (plain trie). `HashMap` cannot do any of these without an `O(n)` scan, and Java provides no ordered-map primitive at all (`TreeMap` is `Θ(log n)` but pays node allocation and pointer chasing).

**Cost:** for `get` alone, `HashMap` wins — `Θ(1)` expected with one multiply and one probe versus `Θ(log n)` array reads. **Use a trie when you need order, not just membership.**
</details>

## Q9
Morton codes: state the benefit, the cost, and the operation it makes cheap.

<details><summary>Answer</summary>

**Benefit:** spatial locality — nearby points get nearby codes, so a **rectangle query in space becomes a range query on codes** (one binary search + a verification scan).

**Cost:** the code range **over-approximates** the rectangle (false-positive ratio 1.3–3× for Morton, ~1.05× for Hilbert), so every candidate must be verified. And the Z-curve has `Θ(√n)` average jump length, so locality is good on average and bad in places.

**Encoding:** `Θ(1)` (15 ops) per 2-D point with the magic-number spread; **inversion** is `Θ(log w)` — closed form. Hilbert has better locality but **no `Θ(1)` inverse**, which is the practical reason Morton wins in libraries.
</details>

## Q10
Why does GPU vertex reordering by Morton code give a 2–5× speedup?

<details><summary>Answer</summary>

Vertex cache misses dominate rasterisation. Vertices are processed in submission order, which has no relationship to screen-space locality, so every triangle fetches a scattered set of vertices.

Reordering by the Morton code of each vertex's **screen-space position** clusters spatially-near vertices into nearby memory. The vertex cache hit rate rises 2–5×, and rasterisation throughput rises with it.

**Cost:** `Θ(n)` Morton encode + `Θ(n log n)` sort, amortised over many frames. This is a real, shipping optimisation in every serious renderer (GPU Gems 3 ch. 20, DirectX/Vulkan best-practice docs).
</details>

## Q11
Submask enumeration: complexity, the termination bug, and the algorithm it powers.

<details><summary>Answer</summary>

`for (int s = k; ; s = (s-1) & k)` enumerates all `2^popcount(k)` submasks in `Θ(2^popcount(k))` total, `Θ(1)` per step.

**Termination bug:** after `s = 0`, `(0−1) & k = k`, so the loop restarts. You must `if (s == 0) break;` **before** the update.

**Powers:** Held–Karp TSP — `Θ(2ⁿ·n²)` time, `Θ(2ⁿ·n)` memory; feasible to `n ≈ 20–24`. Also all-subset enumeration for n ≤ 20, and bitmask-based scheduling/knapsack.
</details>

## Q12
SWAR popcount versus `POPCNT`. When is SWAR the right choice?

<details><summary>Answer</summary>

`POPCNT` is 1 op per 64 bits = **0.0156 ops/bit**. SWAR is 12 ops per word = **0.1875 ops/bit** — **12× worse**.

SWAR wins only when:
- **No hardware `POPCNT`** (pre-2010 x86, ARMv7 without `+popcnt`, baseline WASM).
- **Bulk operations `POPCNT` cannot express** — e.g. computing a *byte-wise* popcount array in two passes, or propagating counts across lanes with SWAR, which no single-instruction approach can do.

In Java, **always use `Long.bitCount`**. On JDK 8 and earlier `Integer.bitCount` fell back to SWAR; on JDK 9+ it is an intrinsic.
</details>

## Q13
Why does `Integer.reverseBytes` matter, and what is the `Integer.reverse` distinction?

<details><summary>Answer</summary>

`Long.reverseBytes(x)` is a single `BSWAP` instruction — it reverses the **byte order** within the word. It is what you use for endianness conversion (network byte order ↔ host) and for hashing where byte order matters.

`Integer.reverse(x)` reverses the **bit order** within the word (also a single instruction via `ROL`-based tricks or a lookup). It is what you need for bit-reversal FFT permutations (labs `29-fft`) and for CRC/DCT tables.

Both are `Θ(1)` intrinsics. A hand-rolled loop over 32 bits is 32× slower.
</details>

## Q14
Your `n = 10⁸` element index needs point lookups *and* range queries. What do you build?

<details><summary>Answer</summary>

**Not a bit trie** — at `w = 64` a plain trie is 41 GB and even a Patricia trie is 1.6 GB.

Options, in order of preference:
1. **Sorted `long[]` + `Arrays.sort`** — 800 MB, build `Θ(n log n)`, `get` is `O(log n)` via `Arrays.binarySearch`, ranges are contiguous slices. **This is the right answer for most systems.**
2. **Compressed sorted array** (delta + Elias–Fano / stream-vbyte) — 100–200 MB, `Θ(log n)` lookup.
3. **Elias–Fano encoding** — `2n` bits with `O(1)` successor and `O(log(n/m))` predecessor. The theoretically best answer for a static sorted `long[]`.
4. **Patricia trie** if you also need dynamic inserts.

The bit-level representation question (Elias–Fano, succinct rank/select structures) is exactly where this lab's skills pay off — and it is not where a plain trie does.
</details>

## Q15
Enumerate every bit pitfall you can, and for each say what a test would catch it.

<details><summary>Answer</summary>

| Pitfall | Symptom | Catching test |
|---------|---------|---------------|
| `>>` vs `>>>` | negatives sort/hash as huge unsigned | include `MIN_VALUE`, `MIN_VALUE+1`, `-1` |
| missing `^ MIN_VALUE` flip | negatives out of order | same |
| `1 << 31` | compile error | — (caught by the compiler, the best case) |
| `1 << 32` / `>>> 32` | silently `>> 0` | loop `shift < w` |
| `numberOfTrailingZeros(0)` | `AIOOBE` far from the cause | fuzz with `0` |
| `-MIN_VALUE` | overflows to `MIN_VALUE` | include `MIN_VALUE` |
| `0xFFFFFFFF` as `int` | compile error | — |
| `(byte)0xFF` widened | sign extension | `& 0xFF` |
| `~x` in a comparison | negative when `x` is positive | unsigned compare |
| non-terminating submask loop | hang | run with `timeout` |
| bitset out-of-range index | silent `false` | bounds checks |
| `compactBy2` missing a mask step | non-invertible | round-trip test |