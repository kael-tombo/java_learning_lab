# Quiz — Tree DP

15 questions. Each key gives the reason.

---

## Q1
Why is tree DP "the DP that cannot fail"? What is left to worry about?

<details><summary>Answer</summary>

A tree is **acyclic by construction**, so a post-order traversal *is* a topological order and the "did I read an uncomputed state?" failure mode is impossible.

What is left:
1. **The state definition** — the only real correctness risk.
2. **`StackOverflowError`** — the only real engineering risk, because tree DP recursion depth is the tree's *height*, and a path of `10⁵` nodes overflows a Java stack at `~10⁴` frames.
</details>

## Q2
State the universal take/skip shape and say what determines which problem it solves.

<details><summary>Answer</summary>

```
dp[u][0] = best with u EXCLUDED;  dp[u][1] = best with u INCLUDED
dp[u][0] = Σ over children c of  max(dp[c][0], dp[c][1])
dp[u][1] = w[u] + Σ over children c of  dp[c][0]
answer  = max(dp[root][0], dp[root][1])
```

**Which problem it solves depends only on what `dp[u][0/1]` mean**, which is set by the constraint:
- Independent set: `u` in ⇒ **no** child in.
- Vertex cover: `u` **not** in ⇒ **every** child in.

**The two recurrences are mirror images.** Writing one from memory of the other is the #1 tree-DP bug.
</details>

## Q3
Why does maximum path sum need the **two largest** child `down` values, not just the largest?

<details><summary>Answer</summary>

A simple path passes through `u` and can descend into at most **two** child subtrees — it cannot branch. So the best path through `u` is

```
w[u] + (largest positive down) + (second largest positive down)
```

Both defaults must be **`0`**, meaning "do not use that branch". Using `Integer.MIN_VALUE` as the default overflows on the addition and for negative weights is wrong anyway.
</details>

## Q4
Why does minimum path sum need *both* a top-down and a bottom-up DP, while maximum does not?

<details><summary>Answer</summary>

Maximum: `down[u] = w[u] + max(0, max down[c])` recovers "the best path from `u` downward", and the answer is `max over u`. One pass suffices.

Minimum: "the cheapest path **from the root**" cannot be recovered from a bottom-up state, because the bottom-up value does not know the accumulated cost from the root. You need `rootTo[u] = rootTo[parent] + w[u]` **top-down**, combined with `down[u]`.

**The asymmetry is real and worth memorising:** maximum is bottom-up-only, minimum needs both directions.
</details>

## Q5
The two-pass diameter algorithm. State it and sketch the proof.

<details><summary>Answer</summary>

1. From any node `s`, find a farthest node `a`.
2. From `a`, find a farthest node `b`.
3. Diameter = `dist(a, b)`.

**Claim:** the eccentricity of a diameter endpoint equals the diameter. Proof sketch: if `dist(a,x) > D` for some `x`, consider the point `p` on the path `a→x` at distance `D` from `a`; one of `dist(p,u)`, `dist(p,v)` exceeds `D` unless `p` lies on the diameter `u–v`, in which case `dist(x,u)` or `dist(x,v)` exceeds `D`, contradicting maximality. ∎

`Θ(n)`, works for arbitrary non-negative edge weights, and **simpler than any DP**.
</details>

## Q6
State the prefix/suffix sibling-sum trick and why it is the key rerooting primitive.

<details><summary>Answer</summary>

At `u` with children `c₁..c_k`, you need `Σ_{j≠i} f(c_j)` for **every** `i`.

**Naive:** `Θ(k)` per child ⇒ `Θ(k²)` per node ⇒ **`Θ(n²)`** for a star.
**Prefix/suffix:** build in `Θ(k)`, answer in `Θ(1)` ⇒ **`Θ(k)` per node ⇒ `Θ(n)`**.

**At `n = 10⁵` with a star this is a `100 000×` saving.** It is the single most useful idiom in tree DP and appears in rerooting, "product/sum of all elements except self", and many others.
</details>

## Q7
State the rerooting mechanism and its cost in terms of the state count `k`.

<details><summary>Answer</summary>

**Pass 1 (bottom-up):** `dp[u][0..k−1]` over `u`'s subtree.
**Pass 2 (top-down):** propagate `up[c][0..k−1]` — the value `c`'s subtree receives from *outside* it, computed as `dp[u]` with `c`'s contribution removed and `up[u]` added, with sibling sums from prefix/suffix arrays.

| | cost |
|---|---|
| naive (recompute siblings per child) | `Θ(n k²)` |
| **prefix/suffix** | **`Θ(n k)`** |

**At `k = K = 1000` (tree knapsack) that is a `1000×` saving** — the state count is what makes prefix/suffix worth doing.
</details>

## Q8
The message-passing view of rerooting. State it.

<details><summary>Answer</summary>

Each **edge carries a message**. The message from `u` to `v` summarises "`u`'s side of the tree, for the purpose of answering the query at `v`".

There are `Θ(n)` messages, each `Θ(1)` given prefix/suffix sums ⇒ `Θ(n)` total for a constant number of states, `Θ(nk)` for `k` states.

**This generalises beyond trees** to any graph if you accept `Θ(m k²)` for the message set. It is the same idea as belief propagation and as the message-passing formulation of the tree metric.
</details>

## Q9
Tree knapsack: naive vs size-capped complexity, and why the cap works.

<details><summary>Answer</summary>

| | time |
|---|---|
| naive (arrays of length `K` everywhere) | **`Θ(nK²)`** |
| **size-capped (length `min(K, \|subtree\|)`)** | **`Θ(nK)`** |

The amortised argument: a merge of parts of size `a` and `b` costs `Θ(min(a,K)·min(b,K))`. Once a part exceeds `K`, only `K` elements of the other side are ever touched, and each element can be on the "capped side" only a bounded number of times — giving a total of `Θ(nK)`.

**At `n = K = 5000` this is `1.25·10¹¹` → `2.5·10⁷`: a `5000×` saving.**

**The implementation trap:** track the **true** subtree size in a separate `size[]` array. Deriving it from `knap[u].length − 1` saturates at `K` and silently breaks the cap.
</details>

## Q10
Small-to-large merging: the `Θ(n log n)` proof.

<details><summary>Answer</summary>

Charge each insertion to the element being moved. The merge always inserts **into the larger structure**, so the size of the structure containing that element **at least doubles** at each move. An element can therefore move at most `⌊log₂ n⌋` times.

```
Total  ≤  n · ⌊log₂ n⌋  =  Θ(n log n)
```

**Space:** `O(n)` **only if you null out the consumed bags.** Keeping every node's map is `Θ(n log n)` memory — a real leak in a long-running service.
</details>

## Q11
Which tree shape breaks small-to-large if you merge into the first child instead of the largest?

<details><summary>Answer</summary>

A **caterpillar** — a chain where each node has one leaf and one large child.

If you merge into the leaf, you insert the entire accumulated subtree into a size-1 structure at every level ⇒ `Θ(n)` per node ⇒ **`Θ(n²)`**.

Balanced trees are safe (all children are similar size). **The adversary picks an unbalanced shape.**
</details>

## Q12
Why must tree DP be iterative, and what is the pattern?

<details><summary>Answer</summary>

Recursion depth equals the tree's **height**, and a **path** has height `n`. Java overflows around `10⁴` frames.

**Pattern:**
1. Build `parent[]` and an `order[]` array with parents **before** children (BFS works).
2. Iterate `order[]` **in reverse**.

**The insight:** you do not need a true DFS post-order — you need a **topological order, reversed**. BFS gives you one for free.
</details>

## Q13
What tree shape has the most valid DP evaluation orders? The least?

<details><summary>Answer</summary>

**Most:** a star rooted at the centre gives `(n−1)!` orders (any permutation of the leaves).

**Least:** a **path** gives exactly **one** order (the hook-length formula gives `n! / Π|subtree(v)| = 1` for a path).

**Consequence:** the number of valid orders says nothing about recursion depth risk; **height** does. A star has `(n−1)!` orders and depth 2; a path has 1 order and depth `n`.
</details>

## Q14
State the virtual tree construction and its cost.

<details><summary>Answer</summary>

1. Sort the `k` marked nodes by DFS order — `Θ(k log k)`.
2. Add the `k−1` LCAs of adjacent pairs — `≤ k−1` new nodes.
3. Sort the `≤ 2k` nodes by DFS order and build the tree by one stack pass — `Θ(k)`.
4. Run the DP on the virtual tree.

**Total `Θ(k log n)`** (dominated by LCA queries). The minimal subtree connecting `k` marks has at most `2k−1` **branching** nodes after compressing degree-2 chains, so the DP is on `O(k)` states regardless of `n`.
</details>

## Q15
When would you use centroid decomposition instead of rerooting?

<details><summary>Answer</summary>

| | rerooting | centroid decomposition |
|---|---|---|
| build | `Θ(n)` | **`Θ(n log n)`** |
| query | `Θ(1)` per node (all answers at once) | **`Θ(log n)`–`Θ(log² n)`** per query |
| handles **dynamic** updates | no (must recompute everything) | **yes** |
| memory | `Θ(n)` | `Θ(n log n)` |

**Rerooting** when you want all answers in one pass over a static tree.
**Centroid decomposition** when values change between queries — that is what makes it the standard tool for dynamic problems like "nodes within distance `k`" under point updates.
</details>