# 06 — Tree DP

<div align="center">

**Tree DP Framework · Diameter · Maximum Path Sum · Independent Set · Tree Merging · Rerooting · DP on Trees**

</div>

---

## Learning Objectives

- Recognise the tree-DP shape: state depends on a **node** and a **direction**, computed bottom-up
- Implement diameter, maximum path sum, minimum path sum, and longest root-to-leaf path
- Explain why tree DP is "the DP that cannot fail" — no cycles, one canonical evaluation order
- Implement **rerooting** to answer "for every node, the best answer computed *without* using this node's parent"
- Implement tree DP for independent set, vertex cover, dominating set, and tree knapsack
- Recognise the difference between "the answer for the whole tree" and "the answer for every node"
- Handle `n = 10⁵` without recursion depth problems

## Prerequisites

- `01-dp-classics` — the DP framework
- Trees, DFS, topological order
- `04-knapsack-variants` — tree knapsack is knapsack over subtrees

## Estimated Time

- **Theory**: 100 minutes
- **Practice**: 150 minutes
- **Exercises**: 80 minutes
- **Total**: 6 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| Tree DP state | `dp[u][0]`, `dp[u][1]` — depends on `u` and its subtree only |
| Post-order traversal | children before parents — the **only** valid evaluation order |
| "Take / skip" | the universal binary tree-DP shape |
| Root choice | tree DP results can depend on the root; rerooting removes that |
| Rerooting | compute the answer for every node in `Θ(n)` via a second top-down pass |
| Message passing | "what is the best my subtree can send upward?" — one value per node |
| Diameter | `Θ(n)` two-pass or one-pass DP |
| Independent set on a tree | `Θ(n)` take/skip |
| Tree knapsack | `Θ(n · K)` — with size-based merging, often `Θ(nK)` total |
| Virtual tree | compress a tree to `O(k)` nodes for `k` marked nodes, in `Θ(k log k)` |
| Small-to-large | merge small into large, `Θ(n log n)` |

## Complexity Snapshot

| Problem | Time | Space | Notes |
|---------|------|-------|-------|
| Tree diameter (2-pass DFS) | `Θ(n)` | `Θ(n)` | any tree, any edge weights |
| Diameter (one-pass DP) | `Θ(n)` | `Θ(n)` | needs weights |
| Maximum path sum | `Θ(n)` | `Θ(n)` | LeetCode 124 |
| Minimum path sum | `Θ(n)` | `Θ(n)` | top-down DP |
| Root-to-leaf max path | `Θ(n)` | `Θ(n)` | simplest tree DP |
| Maximum sum **root-to-leaf** path | `Θ(n)` | `Θ(n)` | LeetCode 112, recursion risk |
| Independent set on a tree | `Θ(n)` | `Θ(n)` | take/skip |
| Vertex cover on a tree | `Θ(n)` | `Θ(n)` | take/skip |
| Dominating set on a tree | `Θ(n)` | `Θ(n)` | 3 states |
| Counting root-to-leaf paths | `Θ(n)` | `Θ(n)` | |
| **Rerooting: max over all nodes** | `Θ(n)` | `Θ(n)` | two passes |
| **Tree knapsack** | `Θ(n · K²)` naive, **`Θ(nK)`** sized | `Θ(nK)` | merge by subtree size |
| Tree knapsack, best-known | **`Θ(nK)`** | `Θ(nK)` | size-based merging |
| Small-to-large merging | `Θ(n log n)` | `Θ(n)` | |
| Virtual tree | `Θ(k log k)` build, `Θ(k)` DP | `Θ(k)` | from LCA |
| Centroid decomposition | `Θ(n log n)` | `Θ(n)` | |

## Algorithms Covered

### The universal shape
```
dp[u][0] = value for u's subtree, given u is EXCLUDED
dp[u][1] = value for u's subtree, given u is INCLUDED

base:    dp[u][0] = 0
         dp[u][1] = w[u]
combine: dp[u][0] = Σ over children c of max(dp[c][0], dp[c][1])
         dp[u][1] = w[u] + Σ over children c of dp[c][0]
answer:  max(dp[root][0], dp[root][1])
```
**Which problem this is depends only on `w[u]` and what `dp[u][0/1]` mean.** Independent set, vertex cover, dominating set, and maximum-weight subgraph are all this.

### Maximum path sum (diameter with weights)
```
down[u] = the maximum sum of a path starting at u and going down into its subtree
down[u] = w[u] + max(0, max over children c of down[c])
answer  = max over u of ( top two positive down[] values at u, or 0 if none )
```

**The two-positive-values step is the whole trick** — a path through `u` uses at most two child subtrees.

### Rerooting
**Problem:** for every node `v`, compute the best answer for the tree *with `v` removed* (or with an edge weight, or "the best path that does not pass through `v`").

**Mechanism:**
1. **Bottom-up pass** computes `dp[u][0]`, `dp[u][1]` for each `u`.
2. **Top-down pass** propagates from `u` to each child `c` the information `fromParent[c][0/1]` — what `c`'s subtree can expect from *outside* its own subtree.

```
for each child c of u:
    fromParent[c][0] = fromParent[u][0] + Σ over siblings s of max(dp[s][0], dp[s][1]) + max(dp[u][1] − dp[c][0] − ..., ...)
```

The "exclude one child's contribution and add the rest" pattern is the standard rerooting idiom. `Θ(n)` total.

### Tree knapsack
```
knapsack[u] = a list where index k = max value achievable with exactly k selected nodes in u's subtree
knapsack[u][0] = 0
knapsack[u][1] = w[u]
for each child c:
    knapsack[u] = maxPlusConvolution(knapsack[u], knapsack[c])
```
**Naive:** `Θ(n K²)`. **Size-based merging:** only merge up to `min(K, size[u])` entries ⇒ **`Θ(nK)` amortised total**, because each merge's cost is proportional to the *product of the two subtree sizes*, and the sum of those products over the whole tree is `Θ(nK)`.

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