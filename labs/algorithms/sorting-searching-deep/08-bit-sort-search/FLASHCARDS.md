# Flashcards — Bit Sort & Search

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Word-RAM model | `w`-bit words, add/shift/AND/compare all `Θ(1)` |
| 2 | Bitwise partition sort complexity | `Θ(n · min(log₂ n, w))` |
| 3 | Bitwise partition comparisons | **zero** — bit tests only |
| 4 | Branchless partition win | ~8 ops but ~3× fewer **cycles** (no 50% mispredicts) |
| 5 | Branchless partition vs `Arrays.sort` | `Arrays.sort` still wins — it is intrinsified |
| 6 | `k & (k-1)` | clear the lowest set bit |
| 7 | `k ^ (k-1)` | the bits at and below the lowest set bit |
| 8 | `k & -k` | isolate the lowest set bit |
| 9 | Power-of-two test | `k > 0 && (k & (k-1)) == 0` |
| 10 | Iterate set bits | `for (x = k; x != 0; x &= x-1)` with `numberOfTrailingZeros` |
| 11 | Submask enumeration | `for (s = k; ; s = (s-1) & k)` — `Θ(2^popcount)` |
| 12 | Submask loop terminator | `if (s == 0) break;` **before** the update, or it loops forever |
| 13 | Bitset set algebra | `Θ(n/w)` — **64×** faster than a hash set when dense |
| 14 | Bitset memory | `n/8` bytes — 384× smaller than `HashSet` |
| 15 | Bitset sparse crossover | wins only when `|A| ≳ n/64` |
| 16 | Two-level bitset summary | makes `firstSet()` `Θ(1)` |
| 17 | `Long.bitCount` | `POPCNT`, `Θ(1)`, **use it** |
| 18 | SWAR popcount | 12 ops/word = 0.1875 ops/bit — **12× worse than `POPCNT`** |
| 19 | `numberOfTrailingZeros(0)` | returns **32** (not an exception) — guard `x != 0` |
| 20 | `highestOneBit(0)` / `lowestOneBit(0)` | both return **0** — different contracts from `TZCNT` |
| 21 | Plain trie node count | `≈ n(w − log₂ n) + 2n` |
| 22 | Patricia trie node count | `≤ 2n − 1` |
| 23 | Plain trie search | `Θ(w)` — 32/64 array reads, no hashing |
| 24 | Patricia trie search | `Θ(log n)` |
| 25 | Trie key order | **unsigned** lexicographic — flip with `^ MIN_VALUE` for signed |
| 26 | What a trie does that `HashMap` cannot | `ceiling`, `floor`, successor, ordered iteration — all `Θ(log n)` |
| 27 | `ceiling(k)` on a trie | follow `k`'s bits; remember the **shallowest** candidate that turns a 0 into a 1 |
| 28 | Morton code definition | `spread(x) | (spread(y) << 1)` |
| 29 | Morton encode cost | `Θ(1)` = 15 ops (5 mask steps) for 2-D |
| 30 | Morton inverse cost | `Θ(log w)` — closed form, 5 compaction steps |
| 31 | Morton locality benefit | a rectangle query in space becomes a **range query on codes** |
| 32 | Morton's cost | over-approximates (1.3–3× false positives); must verify; `Θ(√n)` jumps |
| 33 | Hilbert vs Morton | better locality (`Θ(log n)` jumps, ~1.05× FPR) but **no `Θ(1)` inverse** |
| 34 | GPU Morton reorder win | 2–5× rasterisation throughput |
| 35 | `1 << 31` | **compile error** — use `1L << 31` or `Integer.MIN_VALUE` |
| 36 | `1 << 32` | silently `1 << 0` — Java masks shift counts to 5 bits (`& 31`) |
| 37 | `0xFFFFFFFF` as an `int` | compile error — use `0xFFFFFFFFL` or `-1` |
| 38 | `-Integer.MIN_VALUE` | overflows back to `MIN_VALUE` |
| 39 | `(byte)0xFF` widened to `int` | sign-extends to `-1` — use `& 0xFF` |
| 40 | `>>` vs `>>>` | signed vs logical shift — a bug whenever the sign bit matters |
| 41 | `Integer.reverse` vs `reverseBytes` | bit order within the word vs byte order (`BSWAP`) |
| 42 | Bit-parallel sorting network | `Θ(n log²n · 2/w)` word-ops — theoretical, not a Java win |
| 43 | Held–Karp TSP | `Θ(2ⁿ·n²)` time, `Θ(2ⁿ·n)` memory; feasible to `n ≈ 20–24` |
| 44 | Meet-in-the-middle TSP | `Θ(2^{n/2})` space — feasible to `n ≈ 30` |
| 45 | First differing bit of `a`,`b` | `numberOfTrailingZeros(a ^ b)` |
| 46 | Clear lowest run of 1s | `x & (x + 1)` |
| 47 | Set lowest 0 bit | `x \| (x + 1)` |
| 48 | Elias–Fano encoding | `2n` bits, `O(1)` successor — the best static `long[]` index |
| 49 | Why a plain trie fails at `n = 10⁸`, `w = 64` | `~5·10⁹` nodes ≈ **41 GB** |
| 50 | The right answer for large static sorted ints | sorted `long[]` + `Arrays.binarySearch`, or Elias–Fano |
| 51 | Best boundary values for bit fuzzing | `0, 1, -1, MIN_VALUE, MIN_VALUE+1, MAX_VALUE, 0x55555555, 0xAAAAAAAA, 1<<16` |
| 52 | Byte-range bitset index | `i >>> 6` and `i & 63` |
| 53 | Bitset out-of-range `get` | returns `false` silently — add bounds checks |
| 54 | `andNot` with a larger bitset | `~other` sets the tail lanes — mask before `cardinality()` |
| 55 | JDK 9+ bit intrinsics | `POPCNT`, `TZCNT`, `LZCNT`, `BSWAP`, `ROL` — 5–10× better than JDK 8 |
| 56 | When to reach for bit tricks | when you can pack many logical values into one machine word |
| 57 | What bit tricks are actually for | **data representation**, not algorithmic cleverness |
| 58 | 64× speedup for | bulk set algebra, popcount, membership over dense sets |
| 59 | Never hand-roll in Java | popcount, bit reversal, byte swap, rotate, bit-position |
| 60 | Cross-validation requirement | fuzz with `0` and `MIN_VALUE`; random data alone misses the sign bugs |

## Self-test (one line each)

1. `k ^ (k-1)` effect? → **the bits at and below `k`'s lowest set bit**
2. Branchless partition win measured in what? → **cycles, not instructions** (~3× fewer)
3. Trie key order and the fix? → **unsigned** — insert/search `key ^ MIN_VALUE`
4. Patricia vs plain trie node counts? → **`2n − 1`** vs **`≈ n(w − log₂ n)`**
5. Morton's one weakness vs Hilbert? → **it over-approximates ranges and has `Θ(√n)` jumps**; Hilbert has better locality but no closed-form inverse