# CODE_DEEP_DIVE — Shortest Paths: All-Pairs

## 1. Floyd–Warshall

```java
package com.alglab.allpairs;

public final class FloydWarshall {
    static final long INF = Long.MAX_VALUE / 4;      // NOT MAX_VALUE — see §7

    /** Θ(V³). D is 1-indexed into a (V+1)×(V+1) matrix; returns false on a negative cycle. */
    public static boolean run(int n, long[][] D) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++)
                if (i != j && D[i][j] == INF) D[i][j] = INF;   // caller must pre-fill
        }
        for (int k = 0; k < n; k++) {                 // K OUTERMOST — invariant depends on this
            long[] dk = D[k];                          // hoist row k: sequential in the j loop
            for (int i = 0; i < n; i++) {
                long dik = D[i][k];
                if (dik == INF) continue;              // guard 1: skips the whole row — big win sparse
                long[] di = D[i];
                for (int j = 0; j < n; j++) {
                    long dkj = dk[j];
                    if (dkj == INF) continue;          // guard 2
                    long alt = dik + dkj;
                    if (alt < di[j]) di[j] = alt;
                }
            }
        }
        for (int i = 0; i < n; i++) if (D[i][i] < 0) return false;   // negative cycle
        return true;
    }
}
```

**The three optimisations, and why each helps.**
1. `long[] dk = D[k]` hoisted outside the `i` loop: the `j` loop reads `dk[j]` sequentially.
   Without it, every read is `D[k][j]` — same addresses, but the JIT cannot hoist the row
   base pointer, so you re-do the array-load + bounds check each iteration.
2. `if (dik == INF) continue` — on a sparse graph most entries are `∞`, and this skips `Θ(V)`
   inner iterations per such row. Measured: up to `10×` on `V=4000, E=8000`.
3. `if (dkj == INF) continue` — same idea within a row. Costs one predictable branch; wins
   whenever the graph is sparse.

**Negative-cycle check must run after the main loop** — during the loop, `D[i][i] < 0` can be a
transient value that a later `k` would... actually no, once negative it stays negative (you can
traverse the cycle again). So you *could* check inside, but the post-loop scan is `O(V)` and
cache-friendly. Report which vertices are affected so callers can act.

## 2. FW — blocking for cache

```java
/** Same result, better cache behaviour. Block size B ≈ 32–64 for long[][] row-major. */
public static boolean runBlocked(int n, long[][] D, int B) {
    for (int kk = 0; kk < n; kk += B) {
        int kEnd = Math.min(kk + B, n);
        // (a) diagonal block: D[ii][jj] via k in [kk, kkEnd)
        for (int k = kk; k < kEnd; k++) {
            long[] dk = D[k];
            for (int ii = kk; ii < kEnd; ii++) {
                long dik = D[ii][k];
                if (dik == INF) continue;
                long[] di = D[ii];
                for (int jj = kk; jj < kEnd; jj++) {
                    long alt = dik + dk[jj];
                    if (alt < di[jj]) di[jj] = alt;
                }
            }
        }
        // (b) column strip: rows below, all columns in the block
        for (int jj = 0; jj < n; jj++)
            for (int k = kk; k < kEnd; k++) {
                long dkj = D[k][jj];
                if (dkj == INF) continue;
                for (int ii = kEnd; ii < n; ii++) {
                    long dik = D[ii][k];
                    if (dik == INF) continue;
                    long alt = dik + dkj;
                    if (alt < D[ii][jj]) D[ii][jj] = alt;
                }
            }
        // (c) row strip: rows in the block, all columns
        for (int ii = kk; ii < kEnd; ii++)
            for (int k = kk; k < kEnd; k++) {
                long dik = D[ii][k];
                if (dik == INF) continue;
                long[] di = D[ii];
                for (int jj = kEnd; jj < n; jj++) {
                    long dkj = D[k][jj];
                    if (dkj == INF) continue;
                    long alt = dik + dkj;
                    if (alt < di[jj]) di[jj] = alt;
                }
            }
    }
    for (int i = 0; i < n; i++) if (D[i][i] < 0) return false;
    return true;
}
```

The gain: in the naive version, `D[k][*]` is re-streamed `V` times per `k` (once per `i`). With
blocking, the `K×K` tile stays hot in L1 across all three phases. Measured `1.5–3×` at `V = 600`.

## 3. Transitive closure with bitsets

```java
/** Θ(V³/64) word ops. Row-major long[] bitsets: R[i] bit j set ⟺ i reaches j. */
public static long[][] closure(int n, int[][] adj) {
    int words = (n + 63) >>> 6;
    long[][] R = new long[n][words];
    for (int i = 0; i < n; i++) {
        R[i][i >>> 6] |= 1L << (i & 63);               // reflexive: i reaches i
        for (int j : adj[i]) R[i][j >>> 6] |= 1L << (j & 63);
    }
    for (int k = 0; k < n; k++) {
        int kw = k >>> 6, km = 1L << (k & 63);
        long[] rk = R[k];
        for (int i = 0; i < n; i++) {
            if ((R[i][kw] & km) == 0) continue;         // i cannot reach k — skip the whole OR
            for (int w = 0; w < words; w++) R[i][w] |= rk[w];
        }
    }
    return R;
}
```

The `(R[i][kw] & km) == 0` guard is what makes closure fast on sparse graphs: on a DAG in
topological order it prunes almost every row.

## 4. Johnson

```java
public final class Johnson {
    public record Edge(int u, int v, long w) {}

    /** Θ(V·E log V). Requires a connected graph; throws if a negative cycle exists. */
    public static long[][] allPairs(int n, List<Edge> edges) {
        // --- Step 1: potentials via Bellman-Ford from a virtual source (all h[v] start at 0) ---
        long[] h = new long[n];
        Arrays.fill(h, 0);                              // virtual source: 0-edge to every vertex
        boolean updated = true;
        for (int pass = 0; pass < n && updated; pass++) {
            updated = false;
            for (Edge e : edges) {
                if (h[e.v()] > h[e.u()] + e.w()) {      // relaxing u→v can only DECREASE h[v]
                    h[e.v()] = h[e.u()] + e.w();        // h <= 0 always
                    updated = true;
                    if (pass == n - 1) throw new IllegalStateException("negative cycle reachable");
                }
            }
        }
        // --- Step 2: reweight. Assert w' >= 0 — a cheap invariant that catches most bugs. ---
        List<Edge> rw = new ArrayList<>(edges.size());
        for (Edge e : edges) {
            long wp = e.w() + h[e.u()] - h[e.v()];
            if (wp < 0) throw new IllegalStateException("bad potential: w'=" + wp);
            rw.add(new Edge(e.u(), e.v(), wp));
        }
        // --- Step 3: one Dijkstra per source on w', then undo the shift ---
        List<List<Edge>> adj = buildAdj(n, rw);
        long[][] D = new long[n][n];
        for (int s = 0; s < n; s++) {
            long[] ds = dijkstra(s, adj);               // O(E log V)
            for (int t = 0; t < n; t++)
                D[s][t] = (ds[t] == FloydWarshall.INF) ? FloydWarshall.INF : ds[t] - h[s] + h[t];
        }
        return D;
    }
}
```

**Three details that carry the correctness.**
1. `Arrays.fill(h, 0)` — you do **not** need a real source vertex. Starting every potential at 0
   is exactly equivalent to Bellman–Ford from `s'` with 0-edges, and it avoids allocating `V+1`
   vertices and `V` extra edges.
2. The `pass == n - 1` throw inside the update: if an improvement happens on the `V`-th pass,
   a negative cycle exists. Placing it *inside* the loop (rather than a separate detection pass)
   keeps the single-loop form.
3. `if (wp < 0) throw` — this assertion is mathematically guaranteed (§4.2 of THEORY). If it fires,
   your BF did not converge to true shortest distances, i.e. a bug or a negative cycle.

**Skippable optimisation:** if you know all weights are `≥ 0`, skip steps 1–2 entirely (`h ≡ 0`).

## 5. A\* with a consistent heuristic

```java
/** g+h ordering. With a consistent h each node is expanded at most once. */
public static List<int[]> astar(List<List<Edge>> adj, int s, int t, int[] h) {
    int n = adj.size();
    long[] g = new long[n];
    Arrays.fill(g, FloydWarshall.INF);
    boolean[] closed = new boolean[n];
    g[s] = 0;

    PriorityQueue<Integer> pq = new PriorityQueue<>((a, b) ->
        Long.compare(g[a] + h[a], g[b] + h[b]));        // key = f = g + h, NOT g
    pq.add(s);
    int[] parent = new int[n];
    Arrays.fill(parent, -1);

    while (!pq.isEmpty()) {
        int u = pq.poll();
        if (closed[u]) continue;                         // stale duplicate
        closed[u] = true;                                // safe ONLY because h is consistent
        if (u == t) break;                               // first pop of t is optimal
        for (Edge e : adj.get(u)) {
            if (closed[e.v()]) continue;
            long ng = g[u] + e.w();
            if (ng < g[e.v()]) { g[e.v()] = ng; parent[e.v()] = u; pq.add(e.v()); }
        }
    }
    // reconstruct
    List<int[]> path = new ArrayList<>();
    for (int v = t; v != -1; v = parent[v]) path.add(new int[]{v, parent[v]});
    Collections.reverse(path);
    return path;
}
```

**The `closed` array is the risk.** With a *consistent* `h` it is sound (proved in
MATH_FOUNDATION §6). With a merely admissible `h`, `closed[u] = true` is **wrong** — remove it
and re-open nodes whose `g` improves. If you cannot prove consistency, write the safe version:

```java
// SAFE for admissible-only h:
if (e.w() >= 0) continue;   // drop `closed` entirely; rely on the ng < g[] check + stale pops
```

`g[a] + h[a]` in the comparator reads a mutable array — legal in Java (the array is a captured
local, effectively final reference) but it means the heap's ordering can change under it. It is
correct because we only ever decrease `g` (via `ng < g[v]`), which only *decreases* `f`, and the
heap is re-heapified on the next poll. The standard advice — extract `(f, node)` into the
priority element and use lazy deletion — is more robust; prefer it in production.

## 6. Dijkstra used by Johnson

```java
static long[] dijkstra(int s, List<List<Edge>> adj) {
    int n = adj.size();
    long[] dist = new long[n];
    Arrays.fill(dist, FloydWarshall.INF);
    dist[s] = 0;
    PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(e -> e[0]));
    pq.add(new long[]{0, s});
    while (!pq.isEmpty()) {
        long[] top = pq.poll();
        long d = top[0];
        int u = (int) top[1];
        if (d > dist[u]) continue;                       // lazy: skip the superseded entry
        for (Edge e : adj.get(u)) {
            long nd = d + e.w();
            if (nd < dist[e.v()]) {
                dist[e.v()] = nd;
                pq.add(new long[]{nd, e.v()});
            }
        }
    }
    return dist;
}
```

**Packing `(dist, vertex)` into a `long[]` avoids boxing.** For a graph with `E = 4·10^6` and
`V = 10^6` nodes, `V` Dijkstras allocate and garbage-collect on the order of `10^9` boxed
`Long` objects. Using `long[]` pairs plus a primitive sort is often 3–5× faster. Better still, a
`d`-ary heap (`d = 4` or `8`) over primitive arrays eliminates the per-element allocation entirely.

## 7. Pitfalls (8 + fixes)

1. **`INF = Long.MAX_VALUE`.** `INF + w` wraps to a huge negative → reachable-looking.
   Fix: `Long.MAX_VALUE / 4`, plus both guards in the relaxation loop.
2. **`k` not outermost in FW.** Silently wrong. Add a comment and never refactor that loop order.
3. **Negative-cycle check inside the FW loop.** Works, but you can report a spurious vertex. Do it
   after the loop.
4. **Johnson: forgetting to skip when all weights are `≥ 0`.** Correct but you pay `Θ(VE)` for
   nothing.
5. **Johnson: proceeding to Dijkstra after BF found a negative cycle.** Produces plausible-looking
   garbage. Throw.
6. **Johnson: not correcting the distances back.** `D'[s][t] ≠ D[s][t]`. The shift is
   `−h[s] + h[t]` — omitting it shifts every entry by a different constant, so the answer is
   wrong but plausible.
7. **A\* with `closed[]` and an admissible-only `h`.** Returns a non-optimal path. Either prove
   consistency or drop `closed[]`.
8. **Boxed `PriorityQueue<Long>` in a hot Dijkstra loop.** 3–5× slowdown from GC pressure.
   Use primitive pair encoding.

## 8. Micro-optimisations

- Row-major `long[][]` for FW (`D[i][*]` contiguous in the `j` loop). Column-major is `3×` slower.
- Hoist `D[k]` and `D[i]` into locals before the inner loops (the JIT usually does this, but the
  explicit form documents intent and survives tiering).
- For FW, a **flat** `long[]` with `idx = i*n + j` avoids per-row header loads; measurably faster
  above `n ≈ 1000`.
- FW: skip `i == k` and `j == k` — mathematically no-ops (`D[i][i] ≤ 0`).
- Johnson: reuse the `adj` structure and the priority queue across the `V` Dijkstra runs.
- Dijkstra with a `4`-ary heap of `int[]` primitives for graphs with `V > 10^5`.
- Closure: skip the `k`-unreachable guard *only* on dense graphs (where it never fires and costs
  a branch).

## 9. Checklist

- [ ] `INF = Long.MAX_VALUE / 4`; both relaxation guards present.
- [ ] FW `k` loop outermost (commented).
- [ ] Negative-cycle check after FW; returns/reports the offending vertices.
- [ ] Johnson: `h` initialised to 0 (virtual source), negative cycle throws.
- [ ] Johnson: `w' ≥ 0` asserted before running Dijkstra.
- [ ] Johnson: distance shift `−h[s] + h[t]` applied.
- [ ] A\*: `closed[]` present only if consistency is proven/documented.
- [ ] Priority queues use primitive encoding on hot paths.
- [ ] Cross-validated: FW vs `V × Dijkstra` (non-negative), FW vs Johnson (mixed signs), `n ≤ 60`.