# EXERCISES — Spanning Trees

## Level 1 — Kruskal by Hand

### 1.1 Trace Kruskal
Graph `V = {a,b,c,d,e}`, edges:
`ab=2, ac=3, ad=6, bc=5, bd=7, cd=9, ce=8, de=10`

**Trace (sorted):** `ab(2)`, `ac(3)`, `bc(5)`, `ad(6)`, `bd(7)`, `ce(8)`, `cd(9)`, `de(10)`
- `ab(2)`: comps {a,b} ∪ {c,d,e} → **accept**. comps: {a,b}, {c}, {d}, {e}
- `ac(3)`: {a,b} ∪ {c} → **accept**. comps: {a,b,c}, {d}, {e}
- `bc(5)`: same component → **reject** (cycle)
- `ad(6)`: {a,b,c} ∪ {d} → **accept**. comps: {a,b,c,d}, {e}
- `bd(7)`: same → **reject**
- `ce(8)`: {a,b,c,d} ∪ {e} → **accept**. comps: {a,b,c,d,e}. **`V−1 = 4` edges → stop.**

**MST = {ab, ac, ad, ce}, total = 2+3+6+8 = 19.** Verify by Prim from `a`: tree {a}, pick `ab(2)`;
crossing {a,b}: `ac(3)` → add c; crossing {a,b,c}: `ad(6)`,`bc(5)`,`cd(9)` → pick `bc(5)`? That
gives `ab, ac, bc` — cycle? No: `ab, ac, bc` forms a triangle cycle. Careful: Prim from `a`
adds `ab`, then from {a,b} the crossing edges are `ac(3), ad(6), bc(5)`. `bc(5)` creates a
cycle only if both `b` and `c` are in the tree — `c` is not yet. So Prim picks `ac(3)` → tree
{a,b,c}. Crossing: `ad(6)`, `bc(5)`, `cd(9)` → pick `bc(5)`, but `b,c` both in tree → `bc` is not
crossing. Crossing = `ad(6)`, `cd(9)` → pick `ad(6)` → {a,b,c,d}. Crossing: `ce(8)`, `de(10)`,
`bd`? `b,d` both in tree. `cd` both. → pick `ce(8)` → total `19`. ✓ Same answer.

### 1.2 Cycle property check
In the graph above, `de(10)` is on cycle `a-b-d-e-c-a`? Confirm `de` is the max on cycle
`a–d–e–c–a` (`ad=6, de=10, ec=8, ca=3`) — yes, `de = 10` is the unique maximum, so `de` is in
**no** MST. Verify it is absent from the Kruskal result. ✓

### 1.3 Cut property check
Cut `(S, V∖S)` with `S = {a, b}`, `V∖S = {c, d, e}`. Crossing edges: `ac(3), bc(5), ad(6),
bd(7), cd(?)` no — `cd` is internal. `ce(8)`, `de(10)`. Minimum crossing is `ac(3)`. Per the cut
property `ac` is in some MST — and indeed it is. ✓

### 1.4 Count distinct MSTs
Build a graph where several MSTs have the same total weight; enumerate them. E.g.
`V = {1,2,3}`, all three edges weight 1 → `3` distinct MSTs, all total `2`.

## Level 2 — Implementations

### 2.1 Union-find
Implement DSU with (a) rank only, (b) path compression only, (c) both. Run `10^6` random
`union`/`find` ops and compare depths and wall time. Report which combination wins and why.

### 2.2 Kruskal with early exit
Add the `V−1` break. Measure the speedup on `K_1000` (complete graph, `E ≈ 500 000`).
Expected: you stop after `999` edges but must still *sort* all `500 000`; the win is in `find`
calls, not sorting.

### 2.3 Prim lazy vs eager
Implement both with `PriorityQueue` (lazy) and with an indexed binary heap supporting
`decrease-key` (eager). On `V = 200 000, E = 400 000`, the lazy heap peaks at ~`E` entries;
instrument and report peak heap size and total pushes.

### 2.4 Array-based Prim
Implement the `O(V²)` version with a `key[]`/`visited[]` pair and a linear scan.
**Compare on `V = 3000, E ≈ 4.5M`:** `V² = 9M` scan steps vs `E log V ≈ 100M` heap ops.
Array Prim should win. Explain why.

### 2.5 Borůvka
Implement and **count the phases** on random graphs. Verify empirically that phases `≤ ⌈log₂V⌉`
and that the count matches `⌈log₂ V⌉` for a graph built as `log V` "rings".

### 2.6 Reverse-delete
Implement using BFS connectivity checks. Count connectivity checks and confirm `O(E)`.
Then state why this is unusable for `E > 10^5`.

## Level 3 — Union-Find Deep Dive

### 3.1 Prove the inverse Ackermann bound intuition
Without path compression, union by rank gives depth `O(log V)`. With path compression and rank,
depth is `O(α(V))` amortised. Explain why `α` grows so slowly: `α(1)=1, α(2)=2, α(4)=3,
α(2^4)=4, α(65536)=4` — it takes `2^k` elements to add one to `α`. What is `α` for `V = 10^18`?
**Answer:** `5` (since `α(2^65536) = 5`). Practically a constant.

### 3.2 Path halving vs full compression
Implement both. Measure the number of parent-pointer dereferences on a random sequence.

### 3.3 Wrong union strategy
Implement `union` that always attaches `v`'s root under `u`'s root (no rank). Build a chain of
`V` unions in the worst order and show the tree becomes a linear chain, making a later
`find` cost `Θ(V)`. Then show path compression fixes the *next* query but the first one is still
slow — the amortisation is over the sequence, not per-op.

## Level 4 — Edge Cases (all must pass)

| Input | Expected | Trap |
|-------|----------|------|
| `V = 0` | empty MST, total 0 | `V−1 = −1`; break condition never true → loop runs over 0 edges, fine |
| `V = 1`, no edges | total 0, 0 edges | early exit `V−1 = 0` → **break immediately**, correct |
| Single vertex with self-loop | total 0 | self-loop must be skipped: `find(u) == find(v)` already rejects it |
| Disconnected graph | forest, `k` trees, `V−k` edges | detect via `V−1` not reached |
| All equal weights | any spanning tree is an MST | algorithm-dependent output; sort deterministically if required |
| Negative weights | works fine | `Math.abs` accidentally taken somewhere is a bug |
| Parallel edges `{(1,2):5, (1,2):3}` | pick `3` | Kruskal: `3` accepted first, `5` then rejected |
| Huge weights (`10^9 × 10^5`) | `total` overflows `int` | use `long` |
| `w = NaN` | must be rejected up front | sort order undefined → `ClassCastException` in comparator |
| Self-loop as the only edge of a component | never selected | verify |

## Level 5 — Properties as Proofs

### 5.1 Prove the cut property yourself
Write the full proof from `THEORY.md` §2 and then find the *one* place where "unique minimum"
would be needed (it isn't — "minimum" suffices for the cut property).

### 5.2 Distinguish "in some MST" from "in no MST"
Construct an edge that is the max on a cycle but *tied* with another. Show it is in **some** MST
but not all. This is the counter-example to the sloppy version of the cycle property.

**Example:** triangle with edges `ab=5, bc=5, ca=1`. `ab` and `bc` are tied maxima on the cycle.
MSTs: `{bc(5), ca(1)}` total 6 and `{ab(5), ca(1)}` total 6. So `ab` is in *some* MST (the
second) — it is in no *particular* MST.

### 5.3 Show the greedy paradigm generalises
State and prove the "greedy choice is safe" lemma: if every edge the algorithm selects belongs
to at least one MST, the final result is an MST. Then map Kruskal, Prim, and reverse-delete
onto it.

### 5.4 When is a greedy choice NOT safe?
Give a problem where the analogous greedy fails: interval scheduling with weighted profits and
a two-slot constraint; or the "minimum weight spanning tree with a degree bound at vertex v"
problem, which is NP-hard. Contrast with MST's polynomial solvability and explain what makes MST
special (matroid).

## Level 6 — Stretch

6.1 **MST from a spanning forest of a dynamic graph**: support edge insertions, recompute or
      use the dynamic MST (link-cut tree) update. State the amortised cost.
6.2 **Second-best / k-th best spanning tree**: remove the largest edge of the MST, find the
      cheapest replacement (cheapest edge crossing the resulting cut) → the second-best MST.
      Complexity `O(E log V)`. Generalise to the `k`-th best.
6.3 **Bottleneck spanning tree**: a minimum spanning tree is also a *minimum bottleneck* spanning
      tree — prove it, and give the `O(V+E)` threshold algorithm that finds a bottleneck tree
      without Kruskal (union-find without sorting, growing until connected).
6.4 **MST density / expected edges**: on `G(n, p)`, at what `p` does the graph become connected?
      Use the threshold `p ≈ (log n)/n` and note that the MST then contains a long path of
      Θ(log n / log(log n / p)) length — link to random-graph phase transitions.
6.5 **Counting spanning trees (Kirchhoff's theorem)**: the number of spanning trees of a graph is
      `τ(G) = (1/V) · Π_{i=2}^{V} λ_i`, the product of non-zero Laplacian eigenvalues. Note this
      is *counting*, not minimising — a different problem. Give a 3-vertex example: path → 1,
      triangle → 3.