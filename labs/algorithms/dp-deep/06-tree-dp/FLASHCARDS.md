# Flashcards — Tree DP

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Why is tree DP easy? | **acyclic ⇒ post-order *is* a topological order**; no uncomputed-state reads |
| 2 | The only correctness risk | the **state definition** |
| 3 | The only engineering risk | `StackOverflowError` — depth = **height**, not size |
| 4 | Universal tree-DP shape | `dp[u][0]` = excluded, `dp[u][1]` = included |
| 5 | Independent set recurrence | `dp0 += max(dp0,dp1)`, `dp1 = w + Σ dp0`, answer `max` |
| 6 | Vertex cover recurrence | **mirror image**: `dp0 += dp1`, `dp1 = 1 + Σ min(dp0,dp1)`, answer `min` |
| 7 | The #1 tree-DP bug | writing one of the mirror recurrences from memory of the other |
| 8 | Max path sum state | `down[u]` plus a **two-largest-children** `through[u]` |
| 9 | Why two largest? | a simple path uses **at most two** child subtrees |
| 10 | Path DP default for the branch values | **`0`** (meaning "don't use it") — not `-∞` |
| 11 | Path DP `best` initialiser | `Integer.MIN_VALUE` — negative node values are legal |
| 12 | Min path sum needs | **both** top-down (`rootTo`) and bottom-up (`down`) |
| 13 | Max path sum needs | bottom-up only |
| 14 | Diameter, two-pass | BFS from `s` → `a`; BFS from `a` → `b`; answer `dist(a,b)` |
| 15 | Two-pass proof | the eccentricity of a diameter endpoint equals the diameter |
| 16 | Rerooting pass 1 | bottom-up `dp[u]` over `u`'s subtree |
| 17 | Rerooting pass 2 | top-down `up[c]` = `dp[u]` minus `c`'s contribution plus `up[u]` |
| 18 | Prefix/suffix sibling sum | `Σ_{j≠i} f(c_j) = prefix[i−1] + suffix[i+1]` — `Θ(1)` per child |
| 19 | Rerooting naive cost | `Θ(n k²)` |
| 20 | Rerooting with prefix/suffix | **`Θ(n k)`** |
| 21 | Prefix/suffix saving on a star `n=10⁵` | **100 000×** |
| 22 | Message-passing view | each edge carries a message summarising "my side, for your query" |
| 23 | Tree knapsack, naive | `Θ(nK²)` |
| 24 | **Tree knapsack, size-capped** | **`Θ(nK)`** |
| 25 | Size-cap saving at `K = 5000` | **5000×** |
| 26 | Size-cap implementation trap | track true `size[]` separately — `knap[u].length−1` saturates at `K` |
| 27 | Small-to-large | **`Θ(n log n)`** — the container size doubles per move |
| 28 | Small-to-large space | `O(n)` **only if you null the consumed bags** |
| 29 | Shape that breaks small-to-large | **caterpillar** (merge into the first child ⇒ `Θ(n²)`) |
| 30 | Iterative post-order | build `order[]` with parents before children, then iterate **in reverse** |
| 31 | Key insight | you need a **topological order reversed**, not a true DFS post-order — BFS works |
| 32 | Most valid DP orders | a **star**: `(n−1)!` |
| 33 | Fewest valid DP orders | a **path**: exactly **1** |
| 34 | Recursion depth is | tree **height** — test with a path, not a random tree |
| 35 | Dominating set states | **3** (`not covered` / `covered by a child` / `covered by itself`) |
| 36 | Counting root-to-leaf paths | `dp[u] = Σ dp[c]`, `= 1` at a leaf; use `long` (`2ⁿ` possible) |
| 37 | Centroid decomposition | `Θ(n log n)` build, `Θ(log n)`–`Θ(log² n)` query |
| 38 | Centroid depth | `Θ(log n)` — each component `≤ n/2` |
| 39 | Virtual tree build | `Θ(k log k)` + `k−1` LCA queries; DP on `O(k)` nodes |
| 40 | Virtual tree node bound | `≤ 2k−1` branching nodes |
| 41 | Rerooting vs centroid | reroot = static, all-at-once; centroid = **dynamic**, per-query |
| 42 | Array adjacency representation | `head[]`/`to[]`/`next[]` — `20n` bytes vs ~`100n` for boxed lists |
| 43 | Boxed `List<List<Integer>>` cost | 24 B per list + 16 B per `Integer` ≈ **100 MB** at `n = 10⁶` |
| 44 | Adjacency iteration order | `for (int e = head[u]; e != -1; e = next[e])` |
| 45 | `topoOrder` queue pattern | `for (int i = 0; i < size; i++)` with `size` mutating inside — BFS |
| 46 | `topoOrder` visited test | `parent[v] != -1` requires initialising to `-1` and marking the root |
| 47 | `maxPathSum` with `best = 0` | returns `0` for all-negative values |
| 48 | `second = Integer.MIN_VALUE` | overflows on addition and is wrong for negative weights |
| 49 | Independent set ↔ vertex cover relation | `vc = n − is` only for unweighted, and only sometimes |
| 50 | `naive rerooting` test | brute-force independent set of `T` with each `v` forced out |
| 51 | The best rerooting test | compare every `answer[v]` against brute force — no other test validates the algebra |
| 52 | Rerooting `prefix`/`suffix` allocation | hoist out of the per-node loop; `Θ(n)` allocations is real GC pressure |
| 53 | Tree knapsack `NEG` sentinel | `Long.MIN_VALUE / 4`, and **check before adding** |
| 54 | Tree knapsack constraint | selecting a node forces selecting all its ancestors (else it is plain knapsack) |
| 55 | Tree knapsack, size-indexed variant | `Θ(n²)`; each node pair charged once at its LCA |
| 56 | Weighted vs unweighted diameter | both `Θ(n)`; negative weights break the two-pass version — use the DP |
| 57 | Two-pass with negative weights | **fails** — "farthest" is not well-defined; use the DP |
| 58 | HLD vs tree DP | HLD answers **path** queries; tree DP answers **subtree/whole-tree** queries |
| 59 | Link-cut trees | dynamic tree DP (`Θ(log n)` amortised per update) |
| 60 | The transferable lesson | the only hard part of tree DP is **rerooting**, and inside it the **prefix/suffix trick** |

## Self-test (one line each)

1. Independent set vs vertex cover recurrence? → **Mirror images**: independent set `dp0 += max(dp0,dp1)`, `dp1 = w + Σdp0`; vertex cover `dp0 += dp1`, `dp1 = 1 + Σ min(dp0,dp1)`
2. Prefix/suffix sibling-sum trick and its saving? → **`Σ_{j≠i} f(c_j) = prefix[i−1] + suffix[i+1]`, turning `Θ(nk²)` rerooting into `Θ(nk)`**
3. Tree knapsack naive vs size-capped? → **`Θ(nK²)` vs `Θ(nK)`** — and track the true `size[]` separately or the cap is wrong
4. Why iterative post-order? → **Recursion depth is the tree's height; a path of `10⁵` overflows. Any parents-before-children order reversed is a valid post-order**
5. Shape that breaks small-to-large? → **Caterpillar** — merging into the first child instead of the largest gives `Θ(n²)`