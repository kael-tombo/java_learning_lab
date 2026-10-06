# Exercises — Tree DP

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.treedp`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Trace path DP

Tree (root 0):
```
      1
     / \
    2   3
   / \
  4   5
```
Values `[10, 20, 30, -10, -20]`. Trace `maxPathSum` bottom-up:

| `u` | children | child `down[]` | first | second | `down[u]` | `through[u]` |
|-----|----------|---------------|-------|--------|-----------|--------------|
| 4 | — | — | 0 | 0 | | |
| 5 | — | — | 0 | 0 | | |
| 2 | 4, 5 | | | | | |
| 3 | — | — | 0 | 0 | | |
| 1 | 2, 3 | | | | | |
| 0 | 1 | | | | | |

**Answer should be `10 + 20 + 30 = 60`.**

**Then** the negatives matter: redo with values `[-10, 20, 30, -10, -20]`. Verify that `first`/`second` correctly ignore negative `down[]` values — and explain why initialising `second = Integer.MIN_VALUE` instead of `0` produces a wrong (or overflowed) answer.

---

## Exercise 2 — Independent set vs vertex cover

Trace both for the same tree with `w = [10, 20, 30, 40, 50]`:

**Independent set:**

| `u` | `dp0[u]` | `dp1[u]` | reasoning |
|-----|----------|----------|-----------|
| 4 | | | |
| 5 | | | |
| 2 | | | |
| 3 | | | |
| 1 | | | |
| 0 | | | |

**Vertex cover:** same table.

**Answer:** independent set = `?`, vertex cover = `?`. **Then verify the two recurrences are mirror images** — write them side by side and explain what each branch's constraint is.

**Then answer in writing:** for the tree above, why is `vertexCover = n − independentSet` only sometimes true? (Only when every node has weight 1 AND... compute both for this tree and check.)

---

## Exercise 3 — Rerooting, step by step

Same tree, `w = [10, 20, 30, 40, 50]`. Compute `bestExcludingEachNode` by hand:

**Pass 1** gives `dp0`, `dp1` (from Exercise 2).

**Pass 2** — at `u = 0` with child `1`:
- `siblings` of `1` at `0` = `prefix[0] + suffix[1] = 0`
- `up0[1] = max(up0[0], up1[0]) + 0 = 0`
- `up1[1] = up0[0] + 0 = 0`

At `u = 1` with children `2, 3`:
- `prefix = [0, max(dp0[2],dp1[2]), max(dp0[2],dp1[2]) + max(dp0[3],dp1[3])]`
- for child `2`: `siblings = prefix[0] + suffix[1] = 0 + max(dp0[3],dp1[3])`

Fill in the whole table and verify each `answer[v]` against brute force.

**Then:** implement the **naive** rerooting (recompute sibling sums per child, `Θ(k²)` per node) and time it on a star with `n = 10⁵`. Verify `Θ(n²)` vs the prefix/suffix `Θ(n)` — and report the ratio.

---

## Exercise 4 — Iterative vs recursive

1. Implement `maxPathSum` recursively. Find the largest `n` for a **chain** tree before `StackOverflowError` (expect `~10⁴`).
2. Implement it iteratively. Verify it completes at `n = 10⁶`.
3. **Benchmark both** at `n = 10⁵` (well below the overflow). Which is faster, and by how much? (Expected: the iterative version, because there are no frames and `order[]` is cache-friendly — expect 1.3–2×.)
4. Now build a **star** with `n = 10⁶`. Recursion depth is 2, so recursion is safe. Which is faster now? (Expected: closer to a tie, because `order[]` is a wide BFS that thrashes cache whereas recursion is depth-first.)

**Answer in writing:** what property of the tree determines which implementation wins, and which property determines which one *works*?

---

## Exercise 5 — Tree knapsack: the size cap

1. Implement the **uncapped** version (`Θ(nK²)`). Time it at `n = 500`, `K = 500`.
2. Implement the **size-capped** version (`Θ(nK)`). Time it at the same point.
3. Time both at `n = 2000`, `K = 2000`. **The uncapped one should be infeasible** — measure how long it takes at `n = 1000, K = 1000` and extrapolate.
4. **Instrument the merge count:** for the size-capped version, count the total `i × j` inner iterations and compare with `n·K`. Verify the `Θ(nK)` bound empirically.

**The trap test:** deliberately track `subtreeSize` from `knap[u].length − 1` (the capped length) and find the smallest tree where the answer becomes wrong. Verify with brute force.

---

## Exercise 6 — Small-to-large merging

Implement `coloursAtLeastTwice` and verify against a brute force for random trees with `n ≤ 12` and colours `{0,1,2}`.

Then benchmark for `n = 10⁵` with colours `{0..10⁴}`:
- small-to-large: `Θ(n log n)`
- naive (build a fresh map per node from all descendants): `Θ(n log n)` per node ⇒ `Θ(n² log n)` — measure at `n = 10⁴` and extrapolate.

**Then:** implement the **wrong** version that merges into the *first* child rather than the largest, and measure the degradation. For a **balanced** tree it should be fine (all children similar size); find the tree shape that breaks it (a **caterpillar**: each node has one leaf and one big child — then merging into the leaf every time is `Θ(n)` per node ⇒ `Θ(n²)`).

---

## Exercise 7 — Virtual trees (CHALLENGE)

Build a tree with `n = 10⁵` and mark `k = 20` random nodes.

1. Implement LCA by binary lifting (`Θ(n log n)` build, `Θ(log n)` query).
2. Implement the virtual-tree construction: sort marks by DFS order, add adjacent LCAs, sort, build by stack.
3. Run "maximum independent set of the minimal subtree connecting the marks, forced to include the root of the virtual tree" on the virtual tree.
4. Verify against the full-tree DP with those nodes forced in/out.
5. Time it: `Θ(k log n)` vs `Θ(n)`. Report the crossover in `k`.

**Then:** implement an `O(1)` LCA (Euler tour + sparse table) and re-measure. Does `Θ(k)` beat `Θ(k log n)` in practice? (Expected: only for large `n`, because of the cache pressure of the sparse table.)

---

## Exercise 8 — Centroid decomposition (CHALLENGE)

Implement centroid decomposition and answer:

1. "How many nodes are within distance `k` of `u`?" for all `u`.
2. "What is the diameter after deleting node `u`?" for all `u`.
3. "Find a node `u` such that every component of `T \ {u}` has size `≤ n/2`" (the centroid itself).

Verify (2) against brute force for `n ≤ 10`. Time the build for `n = 10⁵`: `Θ(n log n)`.

**Answer in writing:** when would you use centroid decomposition instead of rerooting, and when the reverse?

---

## Exercise 9 — Debugging drills

1. `topoOrder` with `parent[root] = -1` (not `-2`) — what happens?
2. `topoOrder` with `if (parent[v] != -1) continue;` replaced by `if (v != parent[u])` — infinite loop on which tree?
3. `maxPathSum` with `best = 0` — find the failing input.
4. `maxPathSum` with `second = Integer.MIN_VALUE` — what does `nodeVal[u] + first + second` give?
5. Vertex cover with the independent-set recurrence — find the smallest failing tree.
6. `maxPathSum` with `for (int i = 0; i < n; i++)` over `order[]` instead of reverse — what does it compute?
7. Rerooting with `up0[v] = Math.max(up0[u], up1[u]) + siblings` and `up1[v] = Math.max(up0[u], up1[u]) + siblings` (same formula for both) — find the smallest failing tree.
8. Tree knapsack with `Arrays.fill(merged, NEG)` removed — what happens?
9. Tree knapsack with `int[] merged = new int[newLen + 1]` where `newLen` is not capped — measure the slowdown at `n = 1000, K = 1000`.
10. Small-to-large merging into `bags[v]` (the *first* child) instead of the largest — find the caterpillar that exposes it.

---

## Exercise 10 — Deliverable

`MINI_PROJECT/TreeViz.java`: render a tree, and for each node show `dp0`, `dp1`, `down`, `through`, `up0`, `up1` as it computes them — updating the display after each node in post-order so you watch the values propagate.

Then `BENCHMARK/TreeRace.java` producing a markdown table: diameter (2-pass vs DP), max path sum, independent set, vertex cover, dominating set, rerooting (naive vs prefix/suffix), tree knapsack (capped vs uncapped), small-to-large — across tree shapes `{chain, star, balanced, caterpillar, random}` at `n ∈ {10³, 10⁴, 10⁵, 10⁶}`.

**Answer in writing:** state which tree shape is worst for each algorithm, and explain why in terms of degree and depth.