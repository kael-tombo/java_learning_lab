# CODE_DEEP_DIVE — Spanning Trees

## 1. Union-Find (the foundation)

```java
package com.alglab.mst;

public final class DSU {
    private final int[] parent;
    private final byte[] rank;
    private int components;

    public DSU(int n) {
        parent = new int[n];
        rank   = new byte[n];
        components = n;
        for (int i = 0; i < n; i++) parent[i] = i;    // every vertex starts alone
    }

    public int find(int x) {                            // path halving + full compression hybrid
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];              // halve: skip one level
            x = parent[x];                             // Θ(α) amortised
        }
        return x;
    }

    public boolean union(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;                     // would create a cycle
        if (rank[ra] < rank[rb]) { int t = ra; ra = rb; rb = t; }   // attach smaller to larger
        parent[rb] = ra;
        if (rank[ra] == rank[rb]) rank[ra]++;           // rank increases only on a tie
        components--;
        return true;
    }

    public int components() { return components; }      // O(1) — Kruskal's early exit uses this
}
```

**Two comments that are load-bearing.** `union` returns `false` on a same-root call — that *is*
Kruskal's cycle test. And maintaining `components` as a field (decremented in `union`) turns the
"did we finish?" check into an `O(1)` comparison instead of counting the MST edges separately.

**`byte` for rank:** ranks never exceed `log₂ V` (`≤ 31` for `int`-indexed graphs), so a `byte`
saves 3× the memory of an `int[]` and keeps the array dense in cache. This matters at `V = 10^7`.

## 2. Kruskal

```java
public final class Kruskal {
    public record Edge(int u, int v, long w) {}

    /** Θ(E log E); returns a minimum spanning FOREST if G is disconnected. */
    public static Result run(int n, Edge[] edges) {
        // sort ascending; tie-break on (u,v) for a DETERMINISTIC tree
        Arrays.sort(edges, Comparator.comparingLong(Edge::w)
                                 .thenComparingInt(Edge::u)
                                 .thenComparingInt(Edge::v));
        DSU dsu = new DSU(n);
        List<Edge> mst = new ArrayList<>(n - 1);
        long total = 0;
        for (Edge e : edges) {
            if (e.u() == e.v()) continue;              // self-loop: cycle of length 1 — skip explicitly
            if (dsu.union(e.u(), e.v())) {
                mst.add(e);
                total += e.w();                        // long, NOT int: Σw can overflow int
                if (dsu.components() == 1) break;      // early exit — spanning tree complete
            }
        }
        return new Result(mst, total, dsu.components());   // components > 1 ⟹ forest
    }
    public record Result(List<Edge> edges, long weight, int components) {}
}
```

**Line-by-line complexity.** `Arrays.sort` on `E` objects: `Θ(E log E)` comparisons with a
comparator (a virtual call each — measurable at `E = 10^7`). The loop body is `O(α(V))`.
Early exit at `components() == 1` skips most `find` calls on dense graphs.

**Note on determinism.** `Comparator.comparingLong(...).thenComparingInt(...)` forces a canonical
answer. Plain `Comparator.comparingLong(Edge::w)` lets `Arrays.sort` (a stable TimSort/dual-pivot
quicksort) decide, which is deterministic for a given input order but not "canonical".

## 3. Prim — lazy heap (simplest correct)

```java
/** Θ(E log E). Heap may hold Θ(E) stale entries — acceptable when E is modest. */
public static Result primLazy(int n, List<List<int[]>> adj) {   // adj[u] holds {v, w}
    int[]  key = new int[n];
    int[]  parent = new int[n];
    Arrays.fill(key, Integer.MAX_VALUE);
    parent[0] = -2;
    key[0] = 0;
    PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(e -> e[1]));
    pq.add(new int[]{0, 0});
    boolean[] inTree = new boolean[n];
    List<Edge> mst = new ArrayList<>();
    long total = 0;

    while (!pq.isEmpty()) {
        int[] top = pq.poll();
        int u = top[0], w = top[1];
        if (inTree[u]) continue;                       // stale entry — skip
        if (w != key[u]) continue;                     // superseded by a cheaper edge
        inTree[u] = true;
        if (parent[u] >= 0) { mst.add(new Edge(parent[u], u, w)); total += w; }
        for (int[] e : adj.get(u)) {
            int v = e[0], wv = e[1];
            if (!inTree[v] && wv < key[v]) {
                key[v] = wv;                           // decrease-key by pushing a NEW entry
                parent[v] = u;
                pq.add(new int[]{v, wv});              // the old entry becomes stale garbage
            }
        }
    }
    return new Result(mst, total, inTree[u] ? 1 : 0);
}
```

**Why `Θ(E)` pushes:** each edge `(u,v)` can trigger at most one push when `u` is added to the
tree. Summed over all `u`, that is `Σ deg(u) = 2E`. Heap size peaks at `Θ(E)` in the worst case
(a star graph where the centre improves every leaf). The `w != key[u]` guard is what makes stale
entries harmless — without it, `inTree[u]` alone does not detect a superseded key, and you would
add a non-tree edge to the MST.

## 4. Prim — eager indexed heap (`O(E log V)`)

```java
/** Minimal indexed binary heap with decrease-key. Heap holds at most V entries. */
static final class IndexedHeap {
    private final int[] heap;      // heap[i] = vertex
    private final int[] pos;       // pos[v] = index in heap, or -1 if absent
    private final long[] key;
    private int size;

    IndexedHeap(int n, long[] key) {
        heap = new int[n]; pos = new int[n]; this.key = key;
        Arrays.fill(pos, -1);
        for (int i = 0; i < n; i++) pos[i] = i;        // start with ALL vertices present
    }

    boolean less(int a, int b) { return key[a] < key[b]; }

    void siftUp(int i) {
        while (i > 0) {
            int p = (i - 1) >>> 1;
            if (!less(heap[i], heap[p])) break;
            swap(i, p); i = p;
        }
    }

    void siftDown(int i) {
        while (true) {
            int l = 2 * i + 1, r = l + 1, m = i;
            if (l < size && less(heap[l], heap[m])) m = l;
            if (r < size && less(heap[r], heap[m])) m = r;
            if (m == i) break;
            swap(i, m); i = m;
        }
    }

    void decreaseKey(int v, long newKey) {              // O(log V)
        key[v] = newKey;                                 // in place — no duplicate entry
        siftUp(pos[v]);
    }

    int extractMin() {                                  // O(log V)
        int top = heap[0];
        pos[top] = -1;
        heap[0] = heap[--size];
        siftDown(0);
        return top;
    }

    private void swap(int i, int j) {
        int a = heap[i], b = heap[j];
        heap[i] = b; heap[j] = a;
        pos[a] = j; pos[b] = i;                          // pos[] maintenance is the whole trick
    }
}
```

`pos[]` is what makes decrease-key `O(log V)` instead of `O(log E)`: the vertex's location is
known, so we move it rather than searching for it. **This is ~10–40× faster than the lazy version
on graphs with `E ≫ V`** because the heap never exceeds `V` entries and never accumulates garbage.

## 5. Prim — array scan (`O(V²)`, best for dense)

```java
/** Θ(V²). Use when E = Θ(V²); beats a heap by the log V factor. */
public static Result primArray(int[][] w) {              // w[u][v] = weight, MAX_VALUE = no edge
    int n = w.length;
    long[] key = new long[n];
    int[] parent = new int[n];
    boolean[] inTree = new boolean[n];
    Arrays.fill(key, Long.MAX_VALUE);
    key[0] = 0; parent[0] = -1;

    List<Edge> mst = new ArrayList<>();
    long total = 0;
    int visited = 0;
    for (int iter = 0; iter < n; iter++) {
        int u = -1;
        for (int v = 0; v < n; v++)                    // Θ(V) linear scan for the min
            if (!inTree[v] && (u == -1 || key[v] < key[u])) u = v;
        if (u == -1 || key[u] == Long.MAX_VALUE) break; // disconnected: key stays ∞
        inTree[u] = true; visited++;
        if (parent[u] >= 0) { mst.add(new Edge(parent[u], u, key[u])); total += key[u]; }
        for (int v = 0; v < n; v++)                    // Θ(V) relax, contiguous — very cache-friendly
            if (!inTree[v] && w[u][v] < key[v]) { key[v] = w[u][v]; parent[v] = u; }
    }
    return new Result(mst, total, visited);
}
```

The `int[][]` row-major layout makes the relax loop a sequential scan over `w[u][*]` — one cache
line per 16 entries on a 64-byte line with 4-byte ints. This is why the `O(V²)` version can beat
the asymptotically better heap version in practice.

## 6. Borůvka

```java
/** Θ(E log V). One sequential edge pass per phase — cache- and stream-friendly. */
public static Result boruvka(int n, Edge[] edges) {
    DSU dsu = new DSU(n);
    long[] bestW = new long[n];
    int[] bestU = new int[n], bestV = new int[n];

    while (dsu.components() > 1) {
        Arrays.fill(bestW, Long.MAX_VALUE);
        for (Edge e : edges) {                          // ONE sequential pass
            if (e.u() == e.v()) continue;
            int ru = dsu.find(e.u()), rv = dsu.find(e.v());
            if (ru == rv) continue;                    // same component — internal edge
            if (e.w() < bestW[ru]) { bestW[ru] = e.w(); bestU[ru] = e.u(); bestV[ru] = e.v(); }
            if (e.w() < bestW[rv]) { bestW[rv] = e.w(); bestU[rv] = e.u(); bestV[rv] = e.v(); }
        }
        for (int c = 0; c < n; c++) {
            if (bestW[c] == Long.MAX_VALUE) continue;   // isolated component
            // merge unconditionally-if-safe: union() returns false if already merged this phase
            dsu.union(c, bestU[c]);
        }
    }
    // Reconstruct the tree in a second pass so the output is a clean edge list
    DSU verify = new DSU(n);
    List<Edge> mst = new ArrayList<>();
    long total = 0;
    for (Edge e : edges) if (verify.union(e.u(), e.v())) { mst.add(e); total += e.w(); }
    return new Result(mst, total, 1);
}
```

**The subtle part:** within one phase, several components may pick edges forming a cycle (e.g.
`A–B`, `B–C`, `C–A`). Merging them all "simultaneously" would create a cycle. `union`'s `false`
return is what prevents it — the union-find *is* the simultaneous-merging simulation. Do **not**
try to pre-check for cycles with a second data structure; union-find already is one.

## 7. Reverse-Delete (reference / teaching)

```java
/** Θ(E(V+E)) naive. Correct, obvious, and unusable for E > 10^5. */
public static Result reverseDelete(int n, Edge[] edges) {
    List<Edge> sorted = new ArrayList<>(Arrays.asList(edges));
    sorted.sort(Comparator.comparingLong(Edge::w).reversed());   // DESCENDING — load-bearing
    List<Edge> keep = new ArrayList<>(sorted);
    long total = 0;

    for (Edge e : sorted) {                             // heaviest first
        int degBefore = degreeSum(keep, e);              // degrees of e.u(), e.v() in keep
        // removing e disconnects iff it is a BRIDGE. Test by: is u reachable from v without e?
        if (reachableWithout(keep, e.u(), e.v(), e)) continue;   // a cycle exists — delete it
        // otherwise keep it (it was a bridge)
    }
    return buildResult(keep);
}

private static boolean reachableWithout(List<Edge> es, int s, int t, Edge skip) {
    // BFS from s, never traversing `skip`
    boolean[] seen = new boolean[maxVertex(es) + 1];
    ArrayDeque<Integer> q = new ArrayDeque<>();
    seen[s] = true; q.add(s);
    while (!q.isEmpty()) {
        int u = q.poll();
        if (u == t) return true;
        for (Edge e : es) {
            if (e == skip) continue;
            int v = (e.u() == u) ? e.v() : (e.v() == u ? e.u() : -1);
            if (v >= 0 && !seen[v]) { seen[v] = true; q.add(v); }
        }
    }
    return false;
}
```

**Note:** `e.u() == e.v()` breaks the `reachabilityWithout` neighbour test — a self-loop yields
`v = -1` from the second branch and is correctly ignored. Also, identity comparison `e == skip`
is only valid because `sorted` and `keep` share element references; copying the list by value
would silently break it.

## 8. Pitfalls (9 + fixes)

1. **`int` accumulator for the total weight.** `Σ w` over `10^5` edges of weight `10^5` is `10^10`
   — overflows `int`. Use `long`.
2. **Prim lazy heap without the `w != key[u]` check.** Adds non-tree edges to the MST. The
   `inTree[u]` guard alone is insufficient.
3. **Kruskal with a non-deterministic comparator.** Fine for correctness, but untestable — two runs
   give different trees. Add `.thenComparing(u, v)`.
4. **Reverse-delete sorted ascending.** Silently returns a maximum spanning tree. The descending
   order is what makes the cycle property apply.
5. **Forgetting the self-loop skip in Prim.** A self-loop is examined during relaxation and
   *cannot* improve `key[u]` (`w ≥ key[u]` by the check `!inTree[u]`), so it is harmless — but an
   explicit skip documents intent.
6. **Using Dijkstra's non-negativity assumption.** MST works with negative weights. If you "fixed"
   a negative-weight bug in Kruskal by rejecting negatives, you lost generality.
7. **Dense graph + heap-based Prim.** Correct but `Θ(V² log V)`; use array-Prim.
8. **`byte` rank overflow.** Safe for `int`-indexed graphs (`≤ 31`), but a bug if you ever use
   `long` indices or a modified union that increments rank without a tie. Prefer `int` if unsure.
9. **Assuming a spanning tree exists.** Always check `components()`; return the forest.

## 9. Micro-optimisations

- Pack edges into a single `long[]` (`(w << 40) | (u << 20) | v`) and sort with a primitive sort —
  removes comparator dispatch entirely. Requires `V < 2^20`.
- Kruskal: allocate `parent`/`rank` once and reuse across runs in a benchmark harness.
- Array-Prim: hoist `w[u]` into a local `int[] row = w[u]` to help the JIT hoist the bounds check.
- Array-Prim: track the min in a `priority` scan that starts from the last extracted index
  (approximation) — only valid for approximate MSTs.
- Borůvka: store `bestU/bestV/bestW` in parallel primitive arrays for cache locality.
- For single-linkage clustering, you only need the MST's *sorted edge list*, not the tree — skip
  edge-list construction.

## 10. Checklist

- [ ] Union-find uses **both** rank and path compression.
- [ ] `total` is `long`.
- [ ] Cycle test is `union(...) == true`, not a separate check.
- [ ] Early exit on `components() == 1` (Kruskal) — and the forest case is *returned*, not hidden.
- [ ] Comparator includes a deterministic tie-break.
- [ ] Reverse-delete sorts **descending**.
- [ ] Dense graph → array-Prim; sparse → heap-Prim or Kruskal.
- [ ] Validated against a brute-force (enumerate subsets for `V ≤ 8`) on random instances.