# Math Foundation — Heap Sort

The linear-time heap build, the amortised push bound, and the accounting that makes both fall out of one geometric series.

---

## 1. Height distribution in a complete binary tree

A complete binary tree with `n` nodes has height `H = ⌊log₂ n⌋`. The number of nodes at **exact** height `h` is:

```
N(h) = min(2^h,  n - (2^h - 1))
     = ⌈n / 2^(h+1)⌉            for the standard bound we need
```

Sanity check for `n = 13`: `N(0) = 7` leaves, `N(1) = 3`, `N(2) = 2`, `N(3) = 1`. Total `13`. ✓

| `h` | Nodes at height `h` (`n = 10⁷`) | Fraction |
|-----|------------------------------|----------|
| 0 | `5 000 000` | 50% |
| 1 | `2 500 000` | 25% |
| 2 | `1 250 000` | 12.5% |
| 3 | `625 000` | 6.25% |
| … | halves each level | … |
| 23 | `1` | ~0% |

**Half of all nodes are leaves**, whose `siftDown` is one comparison and returns. That single observation is the intuition behind `Θ(n)`.

---

## 2. Floyd's build: the derivation

Work at height `h` = `N(h) · O(h)`:

```
            ⌊log₂ n⌋
T_build  =   Σ       O( h · n / 2^(h+1) )
          h = 0
        = O( n · S )
```

where `S = Σ_{h≥0} h / 2^(h+1)`.

**Evaluate `S` via the generating function** `Σ_{h≥0} h x^h = x/(1-x)²`:

```
                x            (1/2)
S   =  Σ h x^(h+1)   =  x · x/(1-x)²   =  x²/(1-x)²
            h≥0
      (1/2)²            (1/2)²
  =   ─────    =   ─────────  =  1
     (1-1/2)²      (1/2)²
```

So `S = 1` and

```
T_build = Θ(n)
```

**Substituting directly, layer by layer** (a good sanity check):

```
h=0:  n/2 · 0 = 0
h=1:  n/4 · 1 = n/4
h=2:  n/8 · 2 = n/4
h=3:  n/16 · 3 = 3n/16
h=4:  n/32 · 4 = n/8
...
Σ    ≈ n/4 + n/4 + 0.1875n + 0.125n + ... ≈ 0.94 n  →  Θ(n)
```

**Why it beats repeated `push`:**

```
T_push = Σ_{i=1}^{n} ⌊log₂ i⌋  =  n log₂ n − (n − 1) + O(log n)  =  Θ(n log n)
```

| Method | Bound | Constant (`n = 10⁶`) |
|--------|-------|----------------------|
| Floyd bottom-up | **Θ(n)** | ≈ 1.0 n |
| Repeated `push` | `Θ(n log n)` | ≈ 17.7 n |

**The general lesson:** `Θ(n log n)` arises from `n` items each doing `log n` work *regardless of depth*. `Θ(n)` arises from work *proportional to depth*, because depth grows only logarithmically while the node count decays exponentially.

---

## 3. Amortised `push`: the sharp bound

Naively, push `i` costs `O(log i)`. Summed, that's `Θ(n log n)` — which contradicts the well-known O(1) amortised result. The resolution:

**Correct accounting.** Over a sequence of `n` pushes into an empty heap, the total number of *levels traversed by sifts* is:

```
Σ_{h=0}^{⌊log₂ n⌋}  (number of sift-steps crossing level h)
```

Each element can move **up** across level `h` at most once (as a newly inserted element) and **down** across level `h` at most once (as the displaced parent). Total crossings at level `h` ≤ `2 · 2^h` (there are `2^h` edges at level `h`).

```
Total crossings  ≤  Σ_{h=0}^{H} 2 · 2^h  =  2(2^(H+1) − 1)  <  4n
```

```
Amortised cost per push  =  Total / n  <  4   =  Θ(1)
```

**Worst case for a single push:** `Θ(log n)` — insert a new maximum into a full perfect heap; it travels from depth `⌊log₂ n⌋` to the root. Amortised ≠ worst case; the sequence of pathological pushes cannot repeat indefinitely because each one changes the tree.

**Potential-function proof.** Let `Φ(heap) = size`. Then:
- `push`: actual cost `c`, `ΔΦ = +1`, amortised `c + 1`.
- `pop`: actual cost `O(log n)`, `ΔΦ = −1`, amortised `O(log n) − 1`.
- Over any sequence, `Σ amortised = Σ actual + Φ_final − Φ_initial = Σ actual + O(n)`.
- Hence `n` pushes cost `O(n)` total. ✓

---

## 4. `pop`: always Θ(log n)

Unlike `push`, `pop` has no cheap best case. `pop` replaces the root with the last leaf and sifts it down. The worst case (it belongs at the bottom) is always reachable by choosing the input. So `pop` is `Θ(log n)` amortised *and* worst case — there is no amortisation to exploit.

**Key identity for heapsort.** `n` pops at `Θ(log n)` each:

```
T_heapsort = T_build + Σ_{i=1}^{n-1} Θ(log i)
           = Θ(n) + Θ(n log n)
           = Θ(n log n)
```

**Lower bound on the `Σ log i` term.** Heapsort performs `⌊log₂ k⌋` comparisons on average per extraction of the `k`-th largest element (standard result: `2⌊log₂ k⌋` comparisons). Summing:

```
Σ_{k=1}^{n} 2⌊log₂ k⌋ = 2(n log₂ n − 1.4427 n + O(log n)) = Θ(n log n)
```

Compare with the information-theoretic floor `log₂(n!) ≈ n log₂ n − 1.4427 n`. Heapsort's *comparison count* is asymptotically **optimal** (within a factor of 2, and the comparison lower bound is respected) — it just wastes time on cache misses, not on comparisons.

---

## 5. The comparison-lower-bound reconciliation

| Algorithm | Comparisons (`n = 10⁶`) | `log₂(n!)` lower bound | Ratio |
|-----------|------------------------|------------------------|-------|
| `Arrays.sort` (dual-pivot) | ≈ 1.39 n log₂ n ≈ 23.1e6 | 18.5e6 | 1.25 |
| Heapsort | ≈ 2.0 n log₂ n ≈ 33.2e6 | 18.5e6 | 1.79 |
| Insertion sort | ≈ n²/4 ≈ 2.5e11 | 18.5e6 | 13 500 |

Heapsort's ratio is near the theoretical limit of **2** for any comparison sort that must locate an arbitrary element in a heap-shaped array. Mergesort's ratio is ≈ 1.05 — it is asymptotically optimal in comparisons. **Heapsort's problem is memory access, not comparison count.**

---

## 6. Space-time accounting for the in-place property

```
Heapsort peak auxiliary space = O(1)
  ├─ loop index i, hole, child:            O(1) words
  ├─ recursive-free siftDown:              0 stack
  └─ no aux array:                         0
Mergesort peak auxiliary space = Θ(n)
  └─ aux buffer (reused across all merges): n words
```

**Why in-place matters.** A Θ(n) buffer for `n = 10⁸` `int`s is 400 MB — beyond typical heap budgets, forcing GC pressure or an `OutOfMemoryError`. Heapsort's O(1) space is why it is the algorithm of last resort in memory-constrained or embedded contexts (and why it is the textbook fallback for introsort's introspective depth limit, which is itself O(log n) stack).

---

## 7. D-ary heap: height vs branching factor

Height with fanout `d`: `H_d = log_d n = log₂ n / log₂ d`.

`SiftDown` comparisons with fanout `d`: `O(d · H_d) = O( d · log₂ n / log₂ d )`.

| `d` | `H` for `n = 10⁷` | comparisons `≈ d·H` | memory lines touched |
|-----|------------------|--------------------|----------------------|
| 2 | 23.3 | 47 | 23 |
| 4 | 11.7 | 47 | 12 |
| 8 | 7.8 | 62 | 8 |
| 16 | 5.8 | 93 | 6 |

**The trade-off:** comparisons grow as `d/log d`, but the number of *cache lines* touched by the descent shrinks monotonically. Since a cache miss (~100 cycles) costs more than ~10 comparisons, the optimum sits at small `d` — measured optimum is **`d = 4`**.

Amortised `push` with fanout `d`: `O(d · log_d n)` actual, `O(log_d n)` amortised — better than binary for `d > 2`.

---

## 8. Fibonacci heaps and Dijkstra's bound

| Priority queue | `push` | `decreaseKey` | `pop` | Dijkstra total |
|----------------|--------|---------------|-------|----------------|
| Binary heap | O(log n) | O(log n) | O(log n) | **O((m + n) log n)** |
| Fibonacci heap | O(1) amortised | O(1) amortised | O(log n) amortised | **O(m + n log n)** |

Improvement factor: `(m + n) log n / (m + n log n)`. For a dense graph (`m = n²`) this is `(n² + n) log n / (n² + n log n) ≈ log n` — a **factor of `log n`**, i.e. huge. For a sparse graph (`m = n`) it is a factor of ~2.

**The price:** a Fibonacci heap needs `O(n)` space (a circular doubly-linked root list plus a consolidation array of size `⌈log_d n⌉`), and constant factors 5–20× worse than a binary heap. Real implementations therefore use binary heaps or 4-ary heaps and accept `O((m+n) log n)`. The theory wins only when `m/n` is large.

---

## 9. Quick reference

| Quantity | Value |
|----------|-------|
| Height of a complete binary tree | `⌊log₂ n⌋` |
| Nodes at height `h` | `⌈n / 2^(h+1)⌉` |
| Fraction of nodes that are leaves | ≈ `1/2` |
| Last internal node index | `⌊n/2⌋ − 1` |
| `Σ_{h≥0} h / 2^(h+1)` | `1` |
| Floyd build | **`Θ(n)`** |
| Build by repeated push | `Θ(n log n)` |
| `push` amortised / worst | **`O(1)`** / `O(log n)` |
| `pop` amortised / worst | `O(log n)` / `O(log n)` |
| `peek` | `Θ(1)` |
| Heapsort | **`Θ(n log n)` all cases**, `O(1)` space, unstable |
| D-ary optimum | `d = 4` (cache-driven) |
| Fibonacci-heap Dijkstra | `O(m + n log n)` vs binary's `O((m + n) log n)` |