# MATH_FOUNDATION — Spanning Trees

## 1. Counting Objects (for contrast with optimising them)

### 1.1 Cayley's formula
The number of spanning **trees** of the complete graph `K_V` on `V` labelled vertices is

```
V^(V−2)
```

`K₃ → 3² = 3` ✓ (three 2-edge trees). `K₄ → 4² = 16` ✓. `K₂ → 2⁰ = 1` ✓.

### 1.2 Matrix-Tree Theorem (Kirchhoff)
For any graph `G`, build the Laplacian `L`: `L[i][i] = deg(i)`, `L[i][j] = −1` if `i~j`, else `0`.
Delete any one row and column to get an `(V−1)×(V−1)` minor `M`. Then the number of spanning
trees is

```
τ(G) = det(M)
```

*Sanity checks:* `G = K₃`: `L = [[2,−1,−1],[−1,2,−1],[−1,−1,2]]`, delete row/col 3 →
`M = [[2,−1],[−1,2]]`, `det = 4 − 1 = 3` ✓. `G` = path `a–b–c`: `M = [[1,−1],[−1,2]]`,
`det = 2 − 1 = 1` ✓.

**Why the span of the free part matters:** the Laplacian is singular (its rows sum to zero),
so `det(L) = 0` always. The cofactor version removes the trivial null direction.

### 1.3 Eigenvalue form
Since `L` is symmetric positive semidefinite with eigenvalues `λ₁ = 0 ≤ λ₂ ≤ … ≤ λ_V`,
the product of the non-zero eigenvalues equals `V · τ(G)`:

```
τ(G) = (1/V) · Π_{i=2}^{V} λ_i
```

**Check on `K_V`:** `L = V·I − J`, eigenvalues `0` (once, on the all-ones vector) and `V`
(with multiplicity `V−1`). So `τ = (1/V)·V^{V−1} = V^{V−2}` ✓ — recovers Cayley exactly. Nice.

### 1.4 Expected number of spanning trees in `G(n, p)`
Each tree on `n` labelled vertices (`n^{n−2}` of them) is present with probability `p^{n−1}`, so by
linearity of expectation

```
E[τ(G(n,p))] = n^(n−2) · p^(n−1)
```

Set `= 1` and solve: `p ≈ n^{−2/(n−1)} · n^{1/(n−1)} ≈ exp((log n − 2 log n)/n) → 1` as `n → ∞`.
So at **any** `p < 1` the expected tree count explodes, even though connectivity needs
`p ≈ (log n)/n`. **Expected value and typical behaviour differ wildly** here — a nice lesson
about expectations of heavy-tailed counts.

## 2. Union-Find: The Amortised Bound

### 2.1 Without path compression (union by rank only)
If `y` is a child of `x` then `rank(y) ≤ rank(x)`. Along any path from root to leaf, ranks are
non-increasing, and the rank increases by ≥ 1 at each level. `rank ≤ log V` because a rank-`k`
node's subtree has `≥ 2^k` elements. So depth `≤ log₂ V`, giving `O(log V)` **worst case** per
operation.

### 2.2 The inverse Ackermann function
Define the Ackermann-like tower

```
A(0) = 1,  A(k) = 2^{A(k−1)}  ⟹  A(0)=1, A(1)=2, A(2)=4, A(3)=16, A(4)=65536, A(5)=2^65536
α(n) = min{ k : A(k) ≥ n }
```

Table: `α(4) = 3`, `α(65536) = 5`, `α(2^65536) = 6`. So for `n ≤ 10^18 < 2^60`, `α(n) ≤ 6`.
Practically, `α` is a constant for every input that can be stored.

### 2.3 Why the bound holds (sketch)
Amortised cost is `Σ actual / m`. Tarjan–van Leeuwen's analysis shows that with both techniques,
along any path, the operations that *do not* compress the path (because they pay for it) double
the size of the subtree below a node. A node's rank can therefore increase at most `α(n)` times,
and each such increase is charged `O(1)`. Total over all operations:

```
Total = Σ over nodes of (rank increases × cost) = O(V · α(V)) amortised per-op → O(α(V))
```

**Amortised, not worst case:** there *are* sequences where a single `find` costs `Θ(log V)`;
the bound is on the average over the sequence.

### 2.4 Kruskal's total cost
```
T(E, V) = O(E log E)          [sort]
        + O((E + V) α(V))     [union-find: ≤ E finds, ≤ V−1 unions]
        = Θ(E log E)
```
Note the practical detail: after the sort, the union-find part is *tiny* — `E·α(V)` is roughly
`2E` elementary steps versus `E log E ≈ 20E` for the sort. **Kruskal is a sorting problem wearing
a graph costume.**

## 3. Complexity Cross-Comparison

For `E = Θ(V^2)` (dense):
| Algorithm | Bound | Evaluated at `V = 10^4` |
|-----------|--------|-------------------------|
| Kruskal | `Θ(V² log V)` | `10^8 · 14 ≈ 1.4·10^9` |
| Prim (array) | `Θ(V²)` | `10^8` |
| Prim (lazy heap) | `Θ(V² log V)` | `1.4·10^9` |

For `E = Θ(V)` (sparse):
| Algorithm | Bound |
|-----------|--------|
| Kruskal | `Θ(V log V)` |
| Prim (any heap) | `Θ(V log V)` |
| Prim (array) | `Θ(V²)` — **loses by a factor `V`** |

**Crossover:** array-Prim wins when `V² < E log V`, i.e. `E > V²/log V`. For sparse graphs
`E ≈ cV`, so array-Prim loses unless `c > V/log V` — essentially never. Hence: **Prim-array for
dense, everything else for sparse.**

## 4. Borůvka Phase Analysis

Let `c_k` = components after phase `k`, `c_0 = V`. Each phase: every component picks its cheapest
outgoing edge. The selected edges form a graph on components with minimum degree ≥ 1, so each
connected piece has ≥ 2 components:

```
c_{k+1} ≤ c_k / 2        ⟹        c_k ≤ V / 2^k
```

Total phases `K` is the smallest `k` with `c_k = 1`, so `K ≤ ⌈log₂ V⌉`. Phase cost:
one pass over `E` edges with two `find`s each — `O(E·α(V))`. Total:

```
T = O(E · α(V) · log V)
```

**Tightness:** the halving is tight. Build `V/2` disjoint pairs each joined by a light edge, and
give every pair exactly one outgoing edge to a neighbouring pair of weight `2`. Phase 1 merges
each pair (halving). Repeat with weights `3, 4, …` — `log V` phases, each doing useful work.
So `Θ(log V)` phases is achievable, not an artifact.

## 5. Reverse-Delete Analysis

Naive:
```
T = E deletions × O(V + E) connectivity check  =  O(E(V + E)) = O(E²) for dense
```
For `K_1000`: `E = 5·10^5`, so `T ≈ 2.5·10^11`. Unusable.

Improved via dynamic connectivity (Euler-tour trees or Holm–de Lichtenberg–Thorup):
amortised `O(log n)` per edge update → `O(E log V)` total. Same asymptotic as Kruskal but with a
far heavier constant and a much more complex data structure. **Reverse-delete is the teaching
implementation, not the production one.**

## 6. MST vs Shortest-Path Tree (the classic confusion)

| | MST | Shortest-path tree (Dijkstra) |
|---|---|---|
| Objective | minimise `Σ w(e)` over edges | minimise `Σ w(e)` over the *path* to each vertex |
| Local rule | lightest edge crossing any cut | lightest edge from the settled set to each frontier vertex |
| Same greedy family? | Yes — cut property | Yes — Dijkstra's proof is also cut-based |
| Both correct on | undirected, non-negative | Dijkstra needs non-negative; MST doesn't |
| Result | one tree for all vertices | one tree for all vertices |

They coincide on the special case where every edge has the same weight, or where the graph is a
path — worth tracing both algorithms on a 4-vertex graph to see they disagree.

**Example:** `s–a = 10, s–b = 1, a–b = 1`. Dijkstra from `s`: shortest `a` is via `b`
(`s–b–a = 2`). MST: picks `a–b(1)`, `s–b(1)` → total 2, tree `{a–b, s–b}` — same here.
Better: `s–a = 1, a–t = 100, s–t = 3`. Dijkstra: `t` via `s` = 3. MST: `s–a(1)`, `s–t(3)` = 4.
Same. Use `s–a=1, a–t=1, s–t=5`: Dijkstra gives `a`=1, `t`=2 via `a`. MST gives `s–a(1), a–t(1)`
= 2. Still same. The clean divergence: `s–a=2, a–t=2, s–t=1, s–x=100`. Dijkstra: `t` via `s`=1.
MST: `s–t(1)`, then cheapest crossing is `s–a(2)` → total 3, and `a` is *not* adjacent to `t` in
the MST. So the MST path `s→a` has length 2 while the shortest path is 2 — but pick
`s–a = 10, a–t = 1, s–t = 2`: MST = `s–t(2)` + `a–t(1)` = 3, so MST path to `a` is
`s→t→a` = 3, whereas the shortest path `s→a` = 10. **Clear divergence.**

## 7. MST Cost in Practice

`Θ(E log E)` comparisons for Kruskal. For `E = 10^7` (a real network graph) that is
`~2.3·10^8` comparisons ≈ 0.5–2 s in Java with a primitive sort, plus the memory for the edge
array (16 bytes/edge = 160 MB — often the real bottleneck). This is why production MST code
uses packed primitive sorts or borrows a library with parallel sort.