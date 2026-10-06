# Flashcards — Heap Sort

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Left child of node `i` (0-based) | `2i + 1` |
| 2 | Right child of node `i` | `2i + 2` |
| 3 | Parent of node `i` | `(i - 1) >>> 1` |
| 4 | Height of a complete binary tree with `n` nodes | `⌊log₂ n⌋` |
| 5 | Nodes at exact height `h` | `⌈n / 2^(h+1)⌉` |
| 6 | Fraction of nodes that are leaves | ≈ `1/2` |
| 7 | First leaf index in an `n`-node heap | `n >>> 1` |
| 8 | Last **internal** node index | `⌊n/2⌋ - 1` (NOT `(n-1)>>>1` when `n` is odd) |
| 9 | Max-heap property | `a[i] >= a[2i+1]` and `a[i] >= a[2i+2]` — local only, parent vs own children |
| 10 | Does the heap property imply sortedness? | **No** — `[9,1,8]` is a valid max-heap |
| 11 | Does it guarantee the root is the global max? | **Yes** — by transitivity along the path to the root |
| 12 | What order is heap order? | A **partial** order; a heap has many valid linear extensions (hence instability) |
| 13 | `peek` | `Θ(1)` — read index 0 |
| 14 | `push` worst case | `O(log n)` — insert a new max into a full heap |
| 15 | `push` amortised | **`O(1)`** — total crossings `< 4n` over `n` pushes |
| 16 | `pop` worst and amortised | Both `O(log n)` — the worst case is always reachable |
| 17 | Floyd build complexity | **`Θ(n)`** |
| 18 | Floyd build vs repeated push | `Θ(n)` vs `Θ(n log n)` |
| 19 | The identity behind `Θ(n)` build | `Σ_{h≥0} h/2^(h+1) = 1` |
| 20 | Why does Floyd's build work? | Decreasing index order ⇒ children (higher indices) are already valid heaps |
| 21 | Heapsort total complexity | **`Θ(n log n)` in all cases** — no best case |
| 22 | Heapsort space | **`O(1)`** — in-place, no allocation |
| 23 | Heapsort stability | **No** — `swap(a[0], end)` moves the max across equal elements |
| 24 | Heapsort loop invariant | `a[0..end]` is a max-heap; `a[end+1..n-1]` holds the largest elements in final order |
| 25 | Heapsort's classic bug | Passing `a.length` to `siftDown` instead of the shrinking `end` |
| 26 | Heapsort on sorted input | Still `Θ(n log n)` — the max is at the root and must be moved each time |
| 27 | Hole `siftDown` writes per descent of depth `h` | `h + 1` (vs `2h` for the swap version) — ~11% faster |
| 28 | Why does heapsort lose to quicksort in practice? | Cache misses on the `2k+1` descent + branch mispredictions |
| 29 | Heapsort's comparison count vs the lower bound | `≈ 2 n log₂ n` vs floor `≈ n log₂ n` — ratio ≤ 2, near-optimal |
| 30 | Why is heapsort's problem *not* comparisons? | Memory access, not comparison count — its comparison count is nearly optimal |
| 31 | Best D-ary fanout and why | **`d = 4`** — halves descent depth vs binary while 4 siblings share a cache line |
| 32 | Height with fanout `d` | `log_d n = log₂ n / log₂ d` |
| 33 | Optimal heap when `n < 10⁶` | Plain **binary** heap — everything is cached |
| 34 | Pairing heap | Best empirical `pop`, poor locality, no worst-case guarantee |
| 35 | Fibonacci heap's purpose | Dijkstra with decrease-key: `push`/`decreaseKey` `O(1)` amortised ⇒ `O(m + n log n)` |
| 36 | Binary-heap Dijkstra | `O((m + n) log n)` |
| 37 | Why nobody implements Fibonacci heaps | `O(n)` space, terrible constants; the `log n` gain only matters when `m >> n` |
| 38 | `PriorityQueue.remove(Object)` | `O(n)` — linear scan then sift. No index map is maintained |
| 39 | `PriorityQueue` iteration order | Heap-array order, **not** sorted. Drain with `poll()` |
| 40 | Dijkstra with `PriorityQueue` trick | Push duplicates; on pop skip entries where `entry.dist != dist[node]` |
| 41 | K-way merge pattern | One heap of size `k`; `Θ(N log k)` total |
| 42 | Top-k streaming pattern | Min-heap of size `k`; offer then evict the min if size > k |
| 43 | Top-k streaming complexity | `Θ(n log k)` time, `O(k)` space |
| 44 | When is quickselect better than a top-k heap? | When the data is **already in memory** and input order is irrelevant |
| 45 | `removeAt(i)` after swapping in the last element | Sift **up** if the new value is smaller than its parent, else sift **down** |
| 46 | Why is the sift direction choice needed? | Always `siftDown` leaves a value below its parent; always `siftUp` leaves it above a child |
| 47 | `pop` memory-leak pitfall | Forget `store[size] = null` → the array pins every object ever stored |
| 48 | `push` off-by-one pitfall | `siftUp(size)` must happen **before** `size++`, or the wrong node is sifted |
| 49 | Growth factor for the backing array | 1.5× (`cap + (cap>>1)`) — never 1×, which makes `pushAll` `Θ(n²)` |
| 50 | `pushAll` optimisation | Append then Floyd-build ⇒ **`Θ(k)`**, not `Θ(k log k)` |
| 51 | Parallel heapsort | Bucket-parallel heapsort is bad — merging `p` roots costs `O(p log p)` per extraction |
| 52 | Parallel heapsort done right | Parallel per-block heapsort + `k`-way merge with a heap of size `p` |
| 53 | Introsort's fallback | Heapsort, at a depth limit of `2 log₂ n` |
| 54 | Introsort's two guarantees | `O(n log n)` worst-case time **and** `O(log n)` stack |
| 55 | Why is `PriorityQueue` not sorted-iterable? | Draining in order requires `n` pops at `O(log n)` each |
| 56 | Heap with `n` elements: how many `siftDown` calls in the build do nothing but compare? | ~`n/2` — one per leaf |
| 57 | Binary heap on `10⁷` elements: descent depth | `log₂(10⁷) ≈ 23.3` → ~23 cache lines per extraction |
| 58 | 4-ary heap on `10⁷` elements: descent depth | `log₄(10⁷) ≈ 11.7` → ~12 cache lines |
| 59 | Select min from a heap | `peek()` then `pop()`, or `poll()` — `O(1)` + `O(log n)` |
| 60 | Rule of thumb in Java | `PriorityQueue` by default; 4-ary heap only above `10⁶` with measurements |

## Self-test (one line each)

1. Floyd build bound and the identity behind it? → **`Θ(n)`**, from `Σ h/2^(h+1) = 1`
2. `push` amortised vs worst? → **`O(1)` amortised, `O(log n)` worst**
3. Heapsort's stability and the mechanism? → **Unstable — `swap(a[0], end)` crosses equal elements**
4. Heapsort's heapsort bug? → **Passing `a.length` instead of the shrinking `end` to `siftDown`**
5. Best D-ary fanout for `n > 10⁶`? → **`d = 4`** (cache lines, not comparisons)