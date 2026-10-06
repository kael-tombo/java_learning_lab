# Theory — Tree DP

Trees are the friendliest structure for dynamic programming: **acyclic by construction**, so there is a unique evaluation order (post-order) and no chance of reading a not-yet-computed state. Every difficulty in tree DP is therefore *not* about correctness of the recurrence — it is about (a) defining the right state, (b) rooting the tree, and (c) escaping `StackOverflowError`.

---

## 1. Why trees are easy

For a general graph or sequence DP you must argue:
1. the state definition is complete,
2. the fill order is a topological order,
3. every transition reads already-computed states.

For a **tree**, (3) is free: there is exactly one path from a node to any descendant, so a post-order traversal (children before parents) is *the* topological order and it is unambiguous. The only remaining risk is `StackOverflowError` from deep recursion.

**Consequence:** tree DP has essentially **no correctness risk** and all of its engineering risk. This is why tree problems dominate interviews and why the state definition is the only thing to get right.

---

## 2. The universal take/skip shape

Almost every tree DP is this:

```
dp[u][0] = best value in u's subtree, given u is NOT selected
dp[u][1] = best value in u's subtree, given u IS selected

base:     dp[u][0] = 0
          dp[u][1] = w[u]
combine:  dp[u][0] = Σ over children c of  max(dp[c][0], dp[c][1])
          dp[u][1] = w[u] + Σ over children c of dp[c][0]
answer:   max(dp[root][0], dp[root][1])
```

**Which problem it solves depends only on the semantics of `w[u]`:**

| problem | `dp[u][0]` | `dp[u][1]` | `w[u]` |
|---------|-----------|-----------|--------|
| Maximum-weight independent set | best excluding `u` | best including `u` | `weight(u)` |
| Minimum vertex cover | min cover of subtree, `u` not in it | min cover with `u` in it | `1` for every node |
| Maximum-weight subgraph | best without `u` | best with `u` | `weight(u)` |
| Maximum `k`-independent set | as above, `dp[u][1] ≤ k` | | |
| **Vertex cover** verification | check `∀ edge (u,v): u ∈ C or v ∈ C` | | |

**The transition encodes the constraint structurally**, not with a separate check:
- Independent set: if `u` is in, **no** child may be in ⇒ children contribute `dp[c][0]`.
- Vertex cover: if `u` is **not** in the cover, **every** child must be ⇒ children contribute `dp[c][1]`.

**PITFALL: the two constraints produce mirror-image recurrences.** Independent set sums `max(dp[c][0], dp[c][1])` in the skip branch and `dp[c][0]` in the take branch; vertex cover does the opposite. Writing one from memory of the other is the most common tree-DP bug.

---

## 3. Path problems

### Maximum root-to-leaf path (the simplest tree DP)

```
down[u] = w[u] + max( 0, max over children c of down[c] )
answer  = max over u of down[u]
```
`Θ(n)`. **Note the `max(0, …)`** — with negative weights you may prefer to stop at `u`. Omitting the `0` forces every leaf to contribute a negative value.

### Maximum path sum (LeetCode 124) — diameter with node weights

```
down[u]  = w[u] + max( 0, max over children c of down[c] )
through[u] = w[u] + (largest positive down[c]) + (second-largest positive down[c])
answer   = max over u of through[u]
```

**The two-largest-children step is the whole algorithm.** A simple path passes through `u` and descends into at most **two** child subtrees; using a third would require branching (which a path cannot do). This is why the diameter is a two-branch quantity and not "the maximum `down`".

**Diameter via two BFS/DFS passes** (unweighted or arbitrary non-negative edge weights):
1. From any node `s`, find the farthest node `a`.
2. From `a`, find the farthest node `b`.
3. The diameter is `dist(a, b)`.

**Proof sketch:** in a tree, the farthest node from any start is an endpoint of some diameter. Intuition: the "sweep" argument — as you walk from `s`, you are always moving toward at least one diameter endpoint.

### Minimum path sum

This one is **top-down**, not bottom-up, because you cannot recover "the path to the root" from the bottom-up state:

```
dp[u] = w[u] + min over c of dp[c]
answer = min over u of rootTo[u],  where rootTo[u] = rootTo[parent] + w[u]
```

**Two different DP shapes for max and min path sum** — an asymmetry worth knowing.

### Counting root-to-leaf paths

```
dp[u] = 1                                if u is a leaf
dp[u] = Σ over children c of dp[c]       otherwise
```
`Θ(n)`. With `long`: the count can be `2^{n}`.

---

## 4. Rerooting — the important technique

### The question it answers

> For **every** node `v`, what is the best answer for a quantity defined over the whole tree, computed **without** using `v`'s parent edge?

Classic instances:
- "the maximum path sum that does not pass through `v`"
- "the answer to the independent-set problem for the forest obtained by deleting `v`"
- "the eccentricity of `v`" (maximum distance to any other node)
- "the number of `v`-centroids" / "the best root"

### Why a single bottom-up pass is insufficient

The bottom-up `dp[u][0/1]` is defined on `u`'s **subtree**, which depends on the choice of root. To answer a whole-tree question for every `u`, you need each `u`'s value to include its parent side.

### The mechanism: up + down messages

**Pass 1 (bottom-up).** For every `u`, compute `dp[u][0]` and `dp[u][1]` over `u`'s subtree — as usual.

**Pass 2 (top-down).** Propagate from `u` to each child `c`:

```
up[c][0] = (u's best contribution toward c's subtree, with u NOT selected)
up[c][1] = (u's best contribution toward c's subtree, with u selected)
```

Concretely, for independent set:

```
up[u][0] = value c's subtree gets from above, with u excluded
up[u][1] = value c's subtree gets from above, with u included

contribution from u to a child c, when c is EXCLUDED:
    max(up[u][0], up[u][1]) + Σ over siblings s != c of max(dp[s][0], dp[s][1]) + (u excluded? 0 : w[u])
```

That is: **`dp[u]` with `c`'s contribution removed and `up[u]` added.**

**Implementation shape:**

```java
// Pass 2, at node u with children c1..ck:
// 1. build prefix and suffix sums over max(dp[ci][0], dp[ci][1])
// 2. for each child ci, siblingsSum = prefix[i] + suffix[i+1]
// 3. up[ci][0] = max(up[u][0], up[u][1]) + siblingsSum
// 4. up[ci][1] = up[u][0] + siblingsSumWithoutCi...
```

**The prefix/suffix trick is what makes it `Θ(n)`.** Naively, computing "the sum over siblings" for each child is `Θ(k)` per child ⇒ `Θ(k²)` per node ⇒ `Θ(n²)` for a star. With prefix/suffix sums it is `Θ(1)` per child ⇒ **`Θ(n)` total.**

**This prefix/suffix trick is the single most useful idiom in all of competitive programming.** It appears here, in "product of all elements except self" (LC 135), in "sum of subarray minimums' sibling totals", and in rerooting everywhere.

### The general formulation

Rerooting is **message passing on a tree**:

```
Each edge carries a message.  The message from u to v summarises
"u's side of the tree, for the purpose of answering the query at v".
```

`Θ(n)` messages, each `Θ(1)` given prefix/suffix sums. **If your state has `k` values, the rerooting is `Θ(nk)` plus prefix/suffix sums over `k` states — still `Θ(nk)`.**

---

## 5. Tree knapsack

### The problem

Each node has a weight `w[u]` and a cost `c[u]`. Choose a subset of nodes with total cost `≤ K`, maximising total weight, **where if you select `u` you must select all its ancestors** (the "connected to root" constraint) — or without the constraint (then it is just `Θ(nK)` plain knapsack).

### DP with size-based lists

```
knapsack[u] = array indexed by cost; knapsack[u][k] = max weight using exactly cost k,
              with u selected (and hence all ancestors up to u selected)
```

```
knapsack[u][c[u]] = w[u]                          // select only u
for each child c of u:
    knapsack[u] = maxPlusConvolution(knapsack[u], knapsack[c])
```

`maxPlusConvolution(A, B)[k] = max over a+b=k of ( A[a] + B[b] )`.

**Naive cost:** `Θ(n K²)`.

**Size-based cost:** only merge up to `min(K, subtreeSize)`. The key amortised argument:

```
Σ over all merges of min(|A|, K) · min(|B|, K)
```

With `|A|` = size of the accumulated part and `|B|` = size of the child's subtree, and the merge structure of a tree, **this sum is `Θ(nK)`** — because a node's "small" side can only be merged a bounded number of times before it becomes large, and the total over all nodes is bounded by `nK`.

This is the same small-to-large idea as mergeable heaps. **Without the size cap, the DP is `Θ(nK²)` and you will time out at `n = K = 5000`.**

---

## 6. Small-to-large merging

For DP states that must be **merged** (multiset unions, "which colours appear in the subtree"):

```
For each node, keep the largest child's structure and merge the others into it,
moving elements from the smaller to the larger.
```

**Cost:** each element is moved at most `log₂ n` times (each move at least doubles the size of the structure containing it) ⇒ **`Θ(n log n)` total.**

**Applies to:** colour-count maps over subtrees ("for each colour, is it present at least twice below `u`?"), DSU-on-tree for "subtree queries", and mergeable heaps.

**The canonical problem:** "for each node, list the colours that appear at least twice in its subtree". Naive `Θ(n log n)` per node with maps; small-to-large gives `Θ(n log n)` total with `O(n)` space.

---

## 7. Virtual trees — `Θ(k)` states for `k` marked nodes

### The problem

Given a tree with `n` nodes and `k` **marked** nodes, run a DP over the minimal subtree containing the marks. For `k = 2`, "all the nodes on the path between them" can be `Θ(n)` — but you only need the **compressed** structure.

### Mechanism

1. Sort the `k` marked nodes by DFS order (`Θ(k log k)`).
2. Compute the **LCA** of each adjacent pair and add those `≤ k−1` LCAs.
3. Sort the `≤ 2k` nodes by DFS order and build the virtual tree by a single stack pass — `Θ(k)`.
4. Run your DP on the virtual tree.

**Total: `Θ(k log k + LCA-query cost)`.**

**Use:** competitive programming for "k updates, then answer a global query"; "the path between two marked nodes"; batched queries on a big static tree. `Θ(k log n)` if the LCA is by binary lifting, `Θ(k)` with an `O(1)` LCA (Euler tour + sparse table, `Θ(n log n)` preprocessing).

---

## 8. Centroid decomposition

Not DP, but the natural companion: `Θ(n log n)` preprocessing that answers "the best value in the subtree of distance ≤ `k` from `u`" for **all** `u` in `Θ(log n)` per query.

**Mechanism:** pick the centroid `c`, precompute for each node its distance to `c`, answer all queries "within distance `k` of `u` that pass through `c`" with a sorted-array binary search, then **recurse on each component after removing `c`**.

**Depth is `Θ(log n)`** (each component is at most half the size), so total work is `Θ(n log n)`.

**Use:** "count/largest value of nodes within distance `k`", dynamic diameter, tree `k`-path problems.

---

## 9. Escaping recursion — the real engineering problem

A tree of `10⁵` nodes in a **chain** is `10⁵` deep. Java's default thread stack (`~512 KB–1 MB`, one frame ≈ 50–100 bytes for a simple recursive method) overflows around **`10⁴`** frames.

### Solution: iterative post-order

```java
// 1. Build parent[] and an order[] array with an explicit stack.
// 2. Process order[] in REVERSE -- that is a valid post-order for a tree.
int[] parent = new int[n];
int[] order  = new int[n];
int size = 1;
order[0] = root;
parent[root] = -1;
for (int i = 0; i < size; i++) {                 // BFS-ish, or use a real stack for DFS
    int u = order[i];
    for (int v : adj[u]) {
        if (v == parent[u]) continue;
        parent[v] = u;
        order[size++] = v;
    }
}
// order[] is a topological order (parents before children).
// Reverse iteration gives children before parents -- the post-order you need.
for (int i = size - 1; i >= 0; i--) { compute(u = order[i]); }
```

**This is the pattern you should use in production.** It is 6 lines, immune to stack depth, and usually **faster** than recursion (no frame setup, better cache locality on `order[]`).

**The reverse-order trick is the key insight**: any order with parents before children can be reversed to get a valid DP evaluation order. You do not need a true DFS post-order — you need a topological order, and BFS works.

---

## 10. Summary table

| Problem | States | Time | Space | Direction |
|---------|--------|------|-------|-----------|
| Max root-to-leaf path | `down[u]` | `Θ(n)` | `Θ(n)` | bottom-up |
| Max path sum (diameter) | `down[u]`, `through[u]` | `Θ(n)` | `Θ(n)` | bottom-up |
| Diameter (2-pass DFS) | — | `Θ(n)` | `Θ(n)` | two passes |
| Min path sum | `rootTo[u]`, `down[u]` | `Θ(n)` | `Θ(n)` | **both** directions |
| Independent set | `dp[u][0..1]` | `Θ(n)` | `Θ(n)` | bottom-up |
| Vertex cover | `dp[u][0..1]` | `Θ(n)` | `Θ(n)` | bottom-up |
| Dominating set | `dp[u][0..2]` | `Θ(n)` | `Θ(n)` | bottom-up |
| Counting paths | `dp[u]` | `Θ(n)` | `Θ(n)` | bottom-up |
| **Rerooting (all nodes)** | `dp[u][·]`, `up[u][·]` | **`Θ(n)`** | `Θ(n)` | both passes |
| Tree knapsack (naive) | `knap[u][k]` | `Θ(nK²)` | `Θ(nK)` | bottom-up |
| **Tree knapsack (size-capped)** | `knap[u][k ≤ min(K,|subtree|)]` | **`Θ(nK)`** | `Θ(nK)` | bottom-up |
| Small-to-large merging | multiset | `Θ(n log n)` | `O(n)` | bottom-up |
| Virtual tree | `O(k)` nodes | `Θ(k log k)` | `Θ(k)` | — |
| Centroid decomposition | per-centroid data | `Θ(n log n)` build, `Θ(log n)` query | `Θ(n log n)` | — |

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/treedp/` | All problems |
| `src/test/java/com/alglab/treedp/` | Cross-validation vs brute force for small trees |
| `SOLUTION/` | Worked solutions |
| `TESTS/` | Chains (depth `n`), stars, single nodes, negative weights |
| `BENCHMARK/` | Recursive vs iterative, rerooting throughput |
| `MINI_PROJECT/` | Tree visualiser with the DP table per node |
| `REAL_WORLD_PROJECT/` | Dependency-graph risk propagation / org-chart critical path |
| `CHALLENGE/` | Virtual trees, centroid decomposition, small-to-large |
| `DIAGRAMS/` | Post-order evaluation, rerooting message flow |