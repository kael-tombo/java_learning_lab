# Flashcards — Linear-Time Sorts

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Counting sort time complexity | **`Θ(n + k)`** — `k` is the key range, and the prefix-sum pass costs `Θ(k)` |
| 2 | Counting sort space | `Θ(k)` |
| 3 | Counting sort is `Θ(n)` iff | **`k = Θ(n)`** |
| 4 | Counting sort's `k` must be | `max - min + 1` — **never** `max` |
| 5 | Why `Θ(n + k)` and not `Θ(n)`? | The prefix-sum pass is `Θ(k)`, which for 32-bit keys can be 2³² |
| 6 | Stability condition for counting sort | Scatter direction and prefix-sum convention must match (inclusive+backward, or exclusive+forward) |
| 7 | Common counting-sort bug | Mixed conventions → unstable, but still sorted, so naive tests pass |
| 8 | Why it is a non-comparison sort | `count[key]++` reveals `log₂ k` bits about an element's identity, not 1 |
| 9 | `Θ(n)` when? | Radix sort's `Θ(d(n+B))` becomes `Θ(n)` when `d` and `B` are constants, i.e. **fixed-width keys** |
| 10 | LSD radix correctness invariant | After pass `p`, `a` is sorted by `(digit_p, …, digit_0)` |
| 11 | Why LSD must go least-significant first | Earlier passes' ordering must survive later passes — only **stability** guarantees that |
| 12 | LSD radix requires a stable inner sort? | **Yes** — an unstable pass silently breaks multi-digit ordering |
| 13 | MSD radix requires a stable inner sort? | **No** — buckets are physically separated and re-solved by recursion |
| 14 | LSD time / space | `Θ(d(n+B))` / `Θ(n + B)` |
| 15 | MSD time worst case | `Θ(n log_B n)` when all keys are identical — no better than a comparison sort |
| 16 | MSD with cutoff `C` | `Θ(n (1 + log_B C))`; with `B ≈ C` that is **`Θ(n)`** |
| 17 | Optimal radix base | **`2^k ≈ n`**, i.e. `B ≈ n` |
| 18 | Optimal base — the catch | `B ≈ n` means an `O(n)` count array → cache-hostile; real code uses L1-resident `B` |
| 19 | Radix speedup at the analytic optimum | `(log₂ n)² / w` |
| 20 | Measured radix vs `Arrays.sort` crossover for `int[]` | `n ≈ 3·10⁴` |
| 21 | Best `BITS` for 32-bit keys on modern hardware | `11` (`B = 2048`, 8 KB counts, 3 passes) |
| 22 | `BITS = 16` for 32-bit keys | 2 passes, but a 256 KB count array that spills to L2 |
| 23 | Signed-key handling in radix | `key ^ Integer.MIN_VALUE` maps signed → unsigned **order-preservingly** |
| 24 | Radix shift operator for `int` keys | **`>>>`** (unsigned), not `>>` |
| 25 | The shift-count trap in Java | `>>>` masks shift counts to 5 bits, so `>>> 32` is `>>> 0`. Loop `shift < 32` |
| 26 | Bucket sort assumption | Keys are i.i.d. **uniform** on the value range |
| 27 | Bucket sort under concentration `α` | `Θ(n/α)` — degrades without bound |
| 28 | Bucket sort worst case | `Θ(n²)` (all keys in one bucket, with insertion sort per bucket) |
| 29 | Bucket sort on Gaussian keys | `Θ(n^1.5)` — only `Θ(√n)` buckets occupied |
| 30 | Bucket sort in production | Almost never — the distribution bet is unvalidated and unbounded |
| 31 | Stable counting sort on `char[]` | Legitimate but `k = 65 536`, so usually **worse** than comparison sorting |
| 32 | Counting sort's genuine win | Small dense domains: small enums, status codes, chess squares, bools |
| 33 | Hash-based counting sort | `O(d)` space for `d` distinct keys, expected `Θ(n)` — for huge sparse key ranges |
| 34 | LSD vs MSD — when LSD wins | Few distinct values; trivially parallel; no recursion |
| 35 | LSD vs MSD — when MSD wins | Many distinct values; single `Θ(n)` first pass; early termination |
| 36 | Why MSD suits database index builds | Partition by high bits, then sort each contiguous bucket independently in parallel |
| 37 | Why LSD fails for `String[]` | `d = max length`; one long string makes `d` huge. MSD costs `Θ(Σ|sᵢ|)` instead |
| 38 | MSD on variable-length strings | Terminate per string; treat a sentinel `0` byte as the smallest digit |
| 39 | Memory traffic per radix pass | 3 full traversals: count, scatter, copy-back |
| 40 | Why `Arrays.sort(int[])` is faster below `n ≈ 3·10⁴` | No `d`-pass setup; dual-pivot quicksort has low constant factors and is intrinsified |
| 41 | Radix sort on `BigInteger` (512 bits) | Legal — cost depends on **width**, not value. `d = ⌈512/k⌉` |
| 42 | `Arrays.parallelSort` algorithm | Parallel **merge sort** with `Arrays.sort` leaves — never radix |
| 43 | `Arrays.sort(T[])` algorithm | TimSort — stable, adaptive, `Θ(n)` on presorted |
| 44 | `Arrays.sort(int[])` algorithm | Dual-pivot quicksort with insertion-sort cutoff; unstable (irrelevant for primitives) |
| 45 | Radix sort stability | **Yes** — every pass is stable and passes are composed |
| 46 | Counting sort stability | Yes **iff** directions/conventions match; otherwise no |
| 47 | Comparison lower bound escaped by | Any non-comparison sort; the bound is about 1-bit-at-a-time information |
| 48 | Rule of thumb | Counting if `k = O(n)`; radix if fixed-width integers and `n > 10⁴`; otherwise `Arrays.sort` |
| 49 | The guard that prevents counting-sort OOM | `if (k > 4n) throw` and dispatch to radix |
| 50 | Radix on keys spanning digit boundaries | Test with `{0, 1, 2048, 4096}` — catches digit-width and stability bugs |

## Self-test (one line each)

1. Counting sort's true complexity? → **`Θ(n + k)`**
2. Why LSD needs stability but MSD doesn't? → **MSD separates buckets physically and re-solves each; LSD must preserve earlier passes**
3. Optimal radix base, and the practical catch? → **`B ≈ n`**; the count array then doesn't fit in cache
4. Bucket sort with concentration `α`? → **`Θ(n/α)`**
5. Signed radix trick? → **`x ^ Integer.MIN_VALUE` + `>>>`**