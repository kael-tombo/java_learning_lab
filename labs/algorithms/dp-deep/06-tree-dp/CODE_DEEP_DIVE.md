# Code Deep Dive — Tree DP

Annotated Java. All iterative to survive `n = 10⁵` chains. Java 21.

---

## 1. The infrastructure: iterative post-order

```java
/** Adjacency as arrays: CSR-style for cache friendliness at n = 10^6. */
public final class Tree {
    final int n;
    final int[] head;      // head[u] = first edge index, -1 if none
    final int[] to;        // neighbour
    final int[] next;      // next edge index in the chain
    int edgeCount = 0;

    public Tree(int n) {
        this.n = n;
        this.head = new int[n];
        Arrays.fill(head, -1);
        this.to   = new int[2 * (n - 1)];
        this.next = new int[2 * (n - 1)];
    }

    public void addEdge(int u, int v) {
        to[edgeCount] = v; next[edgeCount] = head[u]; head[u] = edgeCount++;
        to[edgeCount] = u; next[edgeCount] = head[v]; head[v] = edgeCount++;
    }
}
```

**Adjacency-list array representation.** Java's `List<List<Integer>>` costs 24 bytes per list object plus 4 bytes per boxed `Integer` (16 bytes each!). At `n = 10⁶` that is ~100 MB of pure overhead. The `head`/`to`/`next` triple is `4n + 16(n−1)` bytes = **20 MB** with zero boxing.

### Post-order without recursion

```java
/** Returns an order[] with parents BEFORE children; reverse it for post-order. */
static int[] topoOrder(Tree g, int root) {
    int[] parent = new int[g.n];
    Arrays.fill(parent, -1);
    int[] order = new int[g.n];
    int size = 1;
    order[0] = root;
    parent[root] = -2;                             // mark visited

    // BFS using order[] as a queue. PITFALL: `size` grows inside the loop.
    for (int i = 0; i < size; i++) {
        int u = order[i];
        for (int e = g.head[u]; e != -1; e = g.next[e]) {
            int v = g.to[e];
            if (parent[v] != -1) continue;          // already visited
            parent[v] = u;
            order[size++] = v;
        }
    }
    return order;                                  // reverse iteration == post-order
}
```

**Two pitfalls, both fatal:**

1. **`for (int i = 0; i < size; i++)` with `size` mutating inside** — this is a BFS queue pattern and it works, but a reader who expects `i < n` will "fix" it and break it. Comment it.
2. **Using `parent[v] != -1` as the visited test** requires initialising `parent` to `-1` and marking the root distinctly. Forgetting the root mark means the root's parent is re-set and you can loop.

**The key insight:** you do not need a true DFS post-order. You need **any topological order, reversed**. BFS gives you one for free.

---

## 2. Maximum path sum (LeetCode 124)

```java
public static int maxPathSum(int[] nodeVal, Tree g, int root) {
    int[] order = topoOrder(g, root);
    int[] down = new int[g.n];
    int best = Integer.MIN_VALUE;                   // NEGATIVE node values are legal

    for (int i = order.length - 1; i >= 0; i--) {
        int u = order[i];
        int first = 0, second = 0;                 // the TWO largest positive child downs

        for (int e = g.head[u]; e != -1; e = g.next[e]) {
            int v = g.to[e];
            if (v == parentOf(u)) continue;         // or: check parent[] array
            int d = down[v];
            if (d > first)      { second = first; first = d; }
            else if (d > second) { second = d; }
        }

        down[u] = nodeVal[u] + first;               // the 0 default handles negative children
        // A path through u uses AT MOST two child subtrees.
        best = Math.max(best, nodeVal[u] + first + second);
    }
    return best;
}
```

**Pitfall 1 — `best = Integer.MIN_VALUE`, not `0`.** With all-negative values (`nodeVal = [-1,-2,-3]` in a chain) the answer is `-1`, and `best = 0` returns `0`.

**Pitfall 2 — the two-largest step.** `[first, second]` must be the two largest *positive* `down` values, initialised to `0`. Initialising `second = -∞` and then adding gives `nodeVal[u] + first - ∞` = `Integer.MIN_VALUE` overflow. **`0` is the correct default** and it means "do not use a second branch".

**Pitfall 3 — detecting the parent.** With an array representation and a `parent[]` array from `topoOrder`, compare against `parent[u]`. Storing the parent in a field is awkward; recomputing it or passing the array is cleaner.

### The two-pass BFS diameter — no DP needed

```java
public static int diameterUnweighted(Tree g) {
    int a = farthest(g, 0).node();
    return farthest(g, a).dist();
}

private record Far(int node, int dist) {}

static Far farthest(Tree g, int start) {
    int[] dist = new int[g.n];
    Arrays.fill(dist, -1);
    int[] order = new int[g.n];
    int size = 1;
    order[0] = start; dist[start] = 0;
    Far best = new Far(start, 0);

    for (int i = 0; i < size; i++) {
        int u = order[i];
        for (int e = g.head[u]; e != -1; e = g.next[e]) {
            int v = g.to[e];
            if (dist[v] != -1) continue;
            dist[v] = dist[u] + 1;
            order[size++] = v;
            if (dist[v] > best.dist()) best = new Far(v, dist[v]);
        }
    }
    return best;
}
```

`Θ(n)`, and **much simpler than the DP** for unweighted trees. Use it.

---

## 3. Independent set / vertex cover

```java
/** dp0[u] = best with u EXCLUDED; dp1[u] = best with u INCLUDED. */
public static int independentSet(int[] w, Tree g, int root) {
    int n = g.n;
    int[] order = topoOrder(g, root);
    int[] parent = parentOf(g, root, order);
    int[] dp0 = new int[n], dp1 = new int[n];

    for (int i = n - 1; i >= 0; i--) {
        int u = order[i];
        long skip = 0, take = w[u];
        for (int e = g.head[u]; e != -1; e = g.next[e]) {
            int v = g.to[e];
            if (v == parent[u]) continue;
            skip += Math.max(dp0[v], dp1[v]);
            take += dp0[v];                       // if u is in, NO child may be in
        }
        dp0[u] = (int) skip;
        dp1[u] = (int) take;
    }
    return Math.max(dp0[root], dp1[root]);
}

/** Vertex cover: the recurrence is the MIRROR IMAGE. */
public static int vertexCover(Tree g, int root) {
    int n = g.n;
    int[] order = topoOrder(g, root);
    int[] parent = parentOf(g, root, order);
    int[] dp0 = new int[n], dp1 = new int[n];

    for (int i = n - 1; i >= 0; i--) {
        int u = order[i];
        int skip = 0, take = 1;
        for (int e = g.head[u]; e != -1; e = g.next[e]) {
            int v = g.to[e];
            if (v == parent[u]) continue;
            skip += dp1[v];                        // if u is NOT in the cover, every child MUST be
            take += Math.min(dp0[v], dp1[v]);
        }
        dp0[u] = skip;
        dp1[u] = take;
    }
    return Math.min(dp0[root], dp1[root]);
}
```

**The mirror-image trap.** Independent set: `skip += max(dp0,dp1)`, `take += dp0`, answer `max`. Vertex cover: `skip += dp1`, `take += min(dp0,dp1)`, answer `min`. **Writing one while remembering the other is the #1 tree-DP bug.** Write a comment naming the constraint each branch encodes.

---

## 4. Rerooting with prefix/suffix sums

```java
/**
 * For every node v, the maximum-weight independent set of the whole tree
 * WITH v FORCED OUT.  Theta(n) via rerooting + prefix/suffix sibling sums.
 */
public static int[] bestExcludingEachNode(int[] w, Tree g, int root) {
    int n = g.n;
    int[] order = topoOrder(g, root);
    int[] parent = parentOf(g, root, order);

    int[] dp0 = new int[n], dp1 = new int[n];
    // ---- PASS 1: bottom-up, subtree only ----
    for (int i = n - 1; i >= 0; i--) {
        int u = order[i];
        long skip = 0, take = w[u];
        for (int e = g.head[u]; e != -1; e = g.next[e]) {
            int v = g.to[e];
            if (v == parent[u]) continue;
            skip += Math.max(dp0[v], dp1[v]);
            take += dp0[v];
        }
        dp0[u] = (int) skip;
        dp1[u] = (int) take;
    }

    // ---- PASS 2: top-down, adding the parent side ----
    // up0[u] = contribution u's subtree gets from ABOVE, with u excluded
    // up1[u] = ... with u included
    int[] up0 = new int[n], up1 = new int[n];
    // The root has no parent side.
    Arrays.fill(up0, 0);
    Arrays.fill(up1, 0);
    // For the ROOT we must seed with the root's own value:
    up0[root] = 0; up1[root] = 0;

    int[] answer = new int[n];

    for (int idx = 0; idx < n; idx++) {
        int u = order[idx];

        // Collect children in order.
        int deg = 0;
        for (int e = g.head[u]; e != -1; e = g.next[e]) if (g.to[e] != parent[u]) deg++;

        int[] prefix = new int[deg + 1];
        int[] suffix = new int[deg + 1];
        int[] childIdx = new int[deg];

        int c = 0;
        for (int e = g.head[u]; e != -1; e = g.next[e]) {
            int v = g.to[e];
            if (v == parent[u]) continue;
            childIdx[c] = v;
            prefix[c + 1] = prefix[c] + Math.max(dp0[v], dp1[v]);
            c++;
        }
        for (int i = deg - 1; i >= 0; i--) {
            int v = childIdx[i];
            suffix[i] = suffix[i + 1] + Math.max(dp0[v], dp1[v]);
        }

        for (int i = 0; i < deg; i++) {
            int v = childIdx[i];
            int siblings = prefix[i] + suffix[i + 1];   // O(1) -- the whole point

            // What u contributes to v, given v is excluded:
            //   u may or may not be in; take the best, plus every OTHER child's best.
            up0[v] = Math.max(up0[u], up1[u]) + siblings;
            // ... given v is included, u must be excluded:
            up1[v] = up0[u] + siblings + 0;
        }

        // The answer for u = best with u excluded over the WHOLE tree.
        int siblingsTotal = prefix[deg];
        answer[u] = Math.max(up0[u], up1[u]) + siblingsTotal;
    }
    return answer;
}
```

### What is easy to get wrong here

1. **The semantics of `up0`/`up1`.** They are "the value contributed by `u`'s side (parent side of `u` *including* `u` and its ancestors) to `u`'s subtree". Getting the recursion `up0[v] = max(up0[u], up1[u]) + siblings` wrong is silent.
2. **The root seeding.** `up0[root] = up1[root] = 0` is correct (nothing above the root), but a "0 for all" initialisation plus an explicit root assignment is the same thing — just make it obvious.
3. **`prefix`/`suffix` allocation inside the loop.** `new int[deg+1]` per node is `Θ(n)` allocations. Hoist to a single reusable buffer of size `maxDeg`.
4. **Verify with brute force.** For small trees, "independent set of `T` minus node `v`, by definition" must equal `answer[v]`. **This is the only test that validates the whole rerooting machinery.**

### A shortcut for this specific problem

For **unweighted** independent set on a tree, "best excluding `v` over the whole tree" equals `Σ_{u} dp0[u] + Σ_{edges (u,v)} max(dp0[v] − max(dp0[u],dp1[u]), 0)` + … — the rerooting is recoverable from the subtree values with a single pass. But that identity is problem-specific; **the prefix/suffix rerooting is the general technique**, and it is what you should remember.

---

## 5. Tree knapsack — the size cap is everything

```java
/**
 * Choose a set of nodes with total weight <= K, maximising total value,
 * with the constraint that selecting a node forces selecting all its ancestors.
 * Root must be selected.  Theta(n*K) with the size cap.
 */
public static long treeKnapsack(int[] value, int[] cost, Tree g, int root, int K) {
    int n = g.n;
    int[] order = topoOrder(g, root);
    int[] parent = parentOf(g, root, order);

    // knap[u] has length 1 + min(K, subtreeSize(u)).
    int[][] knap = new int[n][];

    for (int idx = n - 1; idx >= 0; idx--) {
        int u = order[idx];

        int cur = Math.min(cost[u], K);
        int[] acc = new int[cur + 1];
        Arrays.fill(acc, NEG);
        if (cost[u] <= K) acc[cost[u]] = value[u];

        int usedLen = acc.length - 1;
        int subtreeSize = 1;

        for (int e = g.head[u]; e != -1; e = g.next[e]) {
            int v = g.to[e];
            if (v == parent[u]) continue;
            int child = knap[v];
            int childLen = child.length - 1;
            subtreeSize += (int) knap[v].length - 1;   // careful: this is capped length
            // PITFALL: subtreeSize should be the TRUE size. Track it separately.

            int newLen = Math.min(K, usedLen + childLen);
            int[] merged = new int[newLen + 1];
            Arrays.fill(merged, NEG);
            for (int i = 0; i <= usedLen; i++) {
                if (acc[i] == NEG) continue;
                for (int j = 0; j <= childLen && i + j <= newLen; j++) {
                    if (child[j] == NEG) continue;
                    int t = i + j;
                    merged[t] = Math.max(merged[t], (long) acc[i] + child[j]);
                }
            }
            acc = merged;
            usedLen = newLen;
        }
        knap[u] = acc;
    }

    long best = NEG;
    for (int k = 0; k < knap[root].length; k++) best = Math.max(best, knap[root][k]);
    return best;
}
```

**The `NEG` sentinel must be checked before adding.** `NEG + child[j]` overflows or produces a garbage `long`. And `NEG` should be `Long.MIN_VALUE / 4` if the value type is `long`.

**The two bugs that destroy performance:**

1. **Not capping the array length.** Without `Math.min(K, ...)`, the arrays are full length `K+1` and every merge is `Θ(K²)` ⇒ `Θ(nK²)`.
2. **Tracking the capped length as the subtree size.** If `subtreeSize` is derived from `knap[u].length - 1`, it saturates at `K` and the cap becomes wrong. **Track the true subtree size separately** (a `size[]` array, `Θ(n)`), and cap only the array length.

### The size array

```java
int[] size = new int[n];
// during the bottom-up pass:
size[u] = 1;
for each child v: size[u] += size[v];
int cur = Math.min(cost[u], K);
int newLen = Math.min(K, cur + size[u] - 1);
```

**This is the difference between `Θ(nK)` and `Θ(nK²)`** — a factor of `K`, which at `K = 5000` is the difference between 1 second and 2 hours.

---

## 6. Small-to-large merging

```java
/** For each node u, the set of colours appearing AT LEAST TWICE in u's subtree. */
public static int[] coloursAtLeastTwice(int[] colour, Tree g, int root) {
    int n = g.n;
    int[] order = topoOrder(g, root);
    int[] parent = parentOf(g, root, order);
    @SuppressWarnings("unchecked")
    HashMap<Integer, Integer>[] bags = new HashMap[n];

    for (int idx = n - 1; idx >= 0; idx--) {
        int u = order[idx];
        HashMap<Integer, Integer> mine = new HashMap<>();
        // Seed with my own colour.
        mine.merge(colour[u], 1, Integer::sum);

        int biggest = -1;
        for (int e = g.head[u]; e != -1; e = g.next[e]) {
            int v = g.to[e];
            if (v == parent[u]) continue;
            HashMap<Integer, Integer> b = bags[v];
            if (biggest == -1 || b.size() > bags[biggest].size()) biggest = v;
        }

        if (biggest == -1) { bags[u] = mine; continue; }

        HashMap<Integer, Integer> big = bags[biggest];   // STEAL the largest
        // Move my own colour into big FIRST, then the smaller bags.
        for (var e : mine.entrySet()) big.merge(e.getKey(), e.getValue(), Integer::sum);
        mine = null;

        for (int e = g.head[u]; e != -1; e = g.next[e]) {
            int v = g.to[e];
            if (v == parent[u] || v == biggest) continue;
            for (var entry : bags[v].entrySet()) big.merge(entry.getKey(), entry.getValue(), Integer::sum);
            bags[v] = null;                              // allow GC
        }
        bags[u] = big;
    }
    return countGe2(bags[root]);
}
```

**The `biggest` selection must happen before any merge**, and the largest bag must be the one you steal. Merging small-into-small is the bug that turns `Θ(n log n)` into `Θ(n)`.

**Memory pitfall:** `bags[v] = null` after merging. Without it you retain every node's map ⇒ `Θ(n log n)` memory instead of `O(n)`.

**Cost:** `Θ(n log n)` — each element moves at most `log₂ n` times because its container at least doubles each move.

---

## 7. Cross-validation harness

```java
static void fuzz() {
    Random rnd = new Random(999);
    for (int trial = 0; trial < 5_000; trial++) {
        int n = 1 + rnd.nextInt(9);
        int[] parent = new int[n];      // parent[0] = -1; random tree
        for (int i = 1; i < n; i++) parent[i] = rnd.nextInt(i);
        Tree g = fromParents(parent);
        int root = 0;

        int[] w = new int[n];
        for (int i = 0; i < n; i++) w[i] = rnd.nextInt(9) - 4;   // NEGATIVE values included

        // --- Independent set ---
        assert TreeDP.independentSet(w.clone(), g, root) == bruteIndSet(g, w.clone(), root);
        // --- Vertex cover ---
        assert TreeDP.vertexCover(g, root) == bruteVertexCover(g, root);
        // --- Path sum ---
        assert TreeDP.maxPathSum(w.clone(), g, root) == brutePathSum(g, w.clone(), root);
        // --- Rerooting: the ONLY test that validates the machinery ---
        int[] r = TreeDP.bestExcludingEachNode(w.clone(), g, root);
        for (int v = 0; v < n; v++)
            assert r[v] == bruteIndSet(g, w.clone(), root, v) : "reroot at " + v;
    }
}

/** Brute force: independent set with node v forced out. O(2^n). */
static int bruteIndSet(Tree g, int[] w, int root, int forcedOut) {
    int n = g.n;
    int best = Integer.MIN_VALUE;
    for (int mask = 0; mask < (1 << n); mask++) {
        if ((mask & (1 << forcedOut)) != 0) continue;
        boolean ok = true;
        for (int e = g.head[0]; e != -1; e = g.next[e]) { /* all edges */ }
        // check no edge has both ends selected
        ...
        if (ok) { int s = 0; for (int i = 0; i < n; i++) if ((mask & (1<<i)) != 0) s += w[i]; best = Math.max(best, s); }
    }
    return best;
}
```

**The rerooting test is the highest-value test in this lab.** It validates the prefix/suffix sums, the `up` recursion, and the answer assembly in one shot, and there is no other way to catch an error in the message-passing algebra.

**Include negative weights** — that is where `best = 0` and the `0` defaults in the two-largest step fail.

---

## 8. What to use in production

```java
// Diameter of an unweighted tree: two BFS passes. Simpler than any DP.
int d = diameterUnweighted(tree);

// Path/weighted problems: the iterative bottom-up DP. Never recurse.

// "For every node, the answer over the whole tree": rerooting with prefix/suffix.
// This is THE technique. Theta(n).

// Tree knapsack: the size cap. Without it you are Theta(n*K^2).

// n = 10^6 nodes: use the CSR-style head/to/next arrays, never List<List<Integer>>.
// Boxed Integer edges cost 100 MB vs 20 MB for the arrays -- 5x.

// Deep chains (n = 10^5): the iterative topoOrder. Recursion dies at ~10^4.
```

**The transferable lesson:** the only hard part of tree DP is **rerooting**, and its only hard sub-part is the **prefix/suffix sibling-sum trick**. Everything else is a two-state recurrence you can write from the constraint.