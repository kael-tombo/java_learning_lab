# CODE_DEEP_DIVE — Max-Flow / Min-Cut

## 1. The residual edge array (the foundation — use this everywhere)

```java
package com.alglab.flow;

/**
 * Flat edge array. Forward arc u->v is index 2k; its reverse arc v->u is 2k+1 = (2k)^1.
 * `cap[i]` holds the RESIDUAL capacity; initialCapacity holds the original for cut extraction.
 */
public final class FlowNet {
    public int n;
    public int[] head = new int[0];            // head[u] = first arc out of u, or -1
    public int[] to, next;
    public long[] cap, initialCapacity;
    int arcs = 0;

    public FlowNet(int n) {
        this.n = n;
        head = new int[n];
        java.util.Arrays.fill(head, -1);
    }

    public void reserve(int m) {               // m = number of forward arcs to be added
        int size = 2 * m;
        to = new int[size]; next = new int[size];
        cap = new long[size]; initialCapacity = new long[size];
    }

    public int addArc(int u, int v, long c) {
        int e = 2 * arcs++;
        to[e] = v; cap[e] = c; initialCapacity[e] = c; next[e] = head[u]; head[u] = e;
        to[e + 1] = u; cap[e + 1] = 0; initialCapacity[e + 1] = 0;  // reverse starts empty
        next[e + 1] = head[v]; head[v] = e + 1;
        return e;
    }

    /** Push δ along arc e. Maintains res(u,v) + res(v,u) = c(u,v) + c(v,u). */
    public void push(int e, long delta) {
        cap[e]     -= delta;
        cap[e ^ 1] += delta;                    // THE line: without it Ford-Fulkerson is wrong
    }

    public long flowOn(int e) { return initialCapacity[e] - cap[e]; }
}
```

**Why `e ^ 1` instead of a `rev[]` array.** The reverse index is arithmetic, so it cannot get out
of sync. The class of bugs "I updated the reverse of the wrong arc" simply disappears. This is the
single highest-value structural choice in a flow implementation.

**`initialCapacity` is not optional.** Without it you cannot extract a min cut, and computing the
cut from residual capacities is a silent wrong answer (see pitfall 3).

## 2. Edmonds–Karp

```java
/** Θ(V·E²). Correct everywhere; slow on dense graphs. */
public static long edmondsKarp(FlowNet g, int s, int t) {
    int n = g.n;
    int[] prev = new int[n];                    // prev[v] = arc used to reach v, -1 = unreached
    long total = 0;
    while (true) {
        java.util.Arrays.fill(prev, -1);
        prev[s] = -2;                           // mark s as visited (sentinel, not a real arc)
        ArrayDeque<Integer> q = new ArrayDeque<>();
        q.add(s);
        while (!q.isEmpty() && prev[t] == -1) {
            int u = q.poll();
            for (int e = g.head[u]; e != -1; e = g.next[e]) {
                if (g.cap[e] > 0 && prev[g.to[e]] == -1) {
                    prev[g.to[e]] = e;
                    q.add(g.to[e]);
                }
            }
        }
        if (prev[t] == -1) break;               // no residual s->t path ⇒ MAXIMUM flow
        // find the bottleneck
        long delta = Long.MAX_VALUE;
        for (int v = t; v != s; ) { int e = prev[v]; delta = Math.min(delta, g.cap[e]); v = g.to[e ^ 1]; }
        for (int v = t; v != s; ) { int e = prev[v]; g.push(e, delta);              v = g.to[e ^ 1]; }
        total += delta;
    }
    return total;
}
```

`prev[s] = -2` is the visited-mark for the source. Using `-1` would collide with "unvisited", and
`prev[s]` would be overwritten — which is harmless here but confusing. `g.to[e ^ 1]` recovers the
tail of arc `e` without a `from[]` array; this is the payoff of the `e ^ 1` layout.

## 3. Dinic

```java
/** Θ(V²E). The default choice. */
public final class Dinic {
    private final FlowNet g;
    private final int[] level, it;

    public Dinic(FlowNet g) { this.g = g; level = new int[g.n]; it = new int[g.n]; }

    /** BFS on the residual graph; returns true if t is reachable. Sets level[] and it[]. */
    private boolean bfs(int s, int t) {
        java.util.Arrays.fill(level, -1);
        int[] q = new int[g.n];
        int qh = 0, qt = 0;
        level[s] = 0; q[qt++] = s;
        while (qh < qt) {
            int u = q[qh++];
            for (int e = g.head[u]; e != -1; e = g.next[e])
                if (g.cap[e] > 0 && level[g.to[e]] < 0) {
                    level[g.to[e]] = level[u] + 1;
                    q[qt++] = g.to[e];
                }
        }
        if (level[t] < 0) return false;
        for (int u = 0; u < g.n; u++) it[u] = g.head[u];   // reset current-arc pointers
        return true;
    }

    /** Send as much as possible along level-graph arcs. Θ(V) per call, Θ(VE) per phase. */
    private long dfs(int u, int t, long lim) {
        if (u == t) return lim;
        for (; it[u] != -1; it[u] = g.next[it[u]]) {         // advance past saturated arcs
            int e = it[u];
            int v = g.to[e];
            if (g.cap[e] == 0 || level[v] != level[u] + 1) continue;   // must be level-admissible
            long d = dfs(v, t, Math.min(lim, g.cap[e]));
            if (d > 0) { g.push(e, d); return d; }          // return EARLY: it[u] not advanced
        }
        return 0;                                            // u is blocked for this phase
    }

    public long maxFlow(int s, int t) {
        long total = 0;
        while (bfs(s, t)) {
            long f;
            while ((f = dfs(s, t, Long.MAX_VALUE / 4)) > 0) total += f;   // blocking flow
        }
        return total;
    }
}
```

**The two lines that make it work.**
1. `level[v] != level[u] + 1` filters to level-graph arcs. Without it you re-explore saturated
   arcs and may revisit non-admissible edges — losing the `O(VE)` per-phase bound.
2. `return d;` **without** `it[u]++`. `it[u]` is advanced only by the `for`-loop increment when
   `dfs` returns 0, i.e. only when arc `e` is exhausted. Advancing eagerly on success would skip
   arcs that still have residual capacity and can still carry more flow.

**`it[u] == -1` after the loop means `u` is finished for this phase** — that's the pruning that
gives `O(VE)` per phase rather than `O(V·E)` per *augmentation*.

## 4. Push–Relabel (highest-label + gap + global relabel)

```java
/** O(V³) FIFO-ish; O(V²√E) practical with all heuristics. Use on big/dense instances. */
public final class PushRelabel {
    private final long[] cap;      // residual
    private final long[] init;
    private final int[] first, next, to;
    private final int n, s, t;
    private final int[] height, count;      // count[h] = #vertices at height h
    private final long[] excess;
    private final int[] cur;
    private final List<Integer> active;
    private long work;                        // ops since the last global relabel

    public long maxFlow() {
        height[s] = n;
        for (int h = 0; h < n; h++) count[0]++;    // everyone starts at height 0 except s
        count[0] = n - 1;
        // saturate all arcs out of s
        for (int e = first[s]; e != -1; e = next[e]) {
            long d = cap[e];
            cap[e] = 0; cap[e ^ 1] += d;
            excess[g.to[e]] += d; excess[s] -= d;
            if (g.to[e] != t && g.to[e] != s) activate(g.to[e]);
        }
        while (!active.isEmpty()) {
            int u = active.remove(active.size() - 1);   // highest height: LIFO on a sorted stack
            if (excess[u] > 0 && u != s && u != t) discharge(u);
            if (work > 6L * arcs) globalRelabel();      // every ~6|E| ops
        }
        return excess[t];
    }

    private void activate(int v) {
        if (height[v] < n && excess[v] > 0) active.add(v);   // height ≥ n ⇒ dead
    }

    private void relabel(int u) {
        int best = Integer.MAX_VALUE;
        for (int e = first[u]; e != -1; e = next[e])
            if (cap[e] > 0) best = Math.min(best, height[to[e]] + 1);
        count[height[u]]--;
        height[u] = best;
        count[best]++;
        cur[u] = first[u];
        work++;
    }

    private void discharge(int u) {
        while (excess[u] > 0) {
            if (cur[u] == -1) { relabel(u); continue; }
            int e = cur[u], v = to[e];
            if (cap[e] > 0 && height[u] == height[v] + 1) {
                long d = Math.min(excess[u], cap[e]);
                cap[e] -= d; cap[e ^ 1] += d;
                excess[u] -= d; excess[v] += d;
                if (v != s && v != t && excess[v] > 0 && excess[v] == d) activate(v);
                if (excess[u] == 0) break;              // keep cur[u] pointing at e
            } else {
                cur[u] = next[e];
            }
        }
    }

    /** GAP heuristic: if a height level becomes empty, everything above it is unreachable to t. */
    private void applyGap(int oldHeight) {
        for (int v = 0; v < n; v++) {
            if (v != s && v != t && height[v] > oldHeight && height[v] < n) {
                count[height[v]]--;
                height[v] = n + 1;             // n+1 = "dead", excluded from active list
                count[height[v]]++;
            }
        }
    }

    /** GLOBAL RELABEL: one reverse BFS from t gives EXACT distances. Resets everything. */
    private void globalRelabel() {
        work = 0;
        java.util.Arrays.fill(height, n + 1);
        int[] q = new int[n]; int qh = 0, qt = 0;
        height[t] = 0; q[qt++] = t;
        while (qh < qt) {
            int v = q[qh++];
            for (int e = first[v]; e != -1; e = next[e]) {
                int u = to[e];
                if (cap[e ^ 1] > 0 && height[u] > height[v] + 1) {   // examine the REVERSE residual
                    height[u] = height[v] + 1;
                    q[qt++] = u;
                }
            }
        }
        java.util.Arrays.fill(count, 0);
        for (int v = 0; v < n; v++) { count[height[v]]++; cur[v] = first[v]; }
        active.clear();
        for (int v = 0; v < n; v++) if (v != s && v != t && excess[v] > 0 && height[v] < n) active.add(v);
    }
}
```

**Five things this depends on.**
1. `height[s] = n` — with `h(s) = n` and validity `h(u) ≤ h(v)+1`, the only way to have all excess
   zero is `n ≤ 0`, a contradiction, so no `s→t` residual path can exist at the end.
2. The `active` list is kept **sorted by height descending**; `remove(size-1)` then pops the
   highest. With `remove(active.size()-1)` on a list that is *not* sorted you lose the
   highest-label property (you still get FIFO-ish behaviour and correct results, just slower).
3. `activate(v)` is called only when `excess[v]` transitions from `0` to positive (`excess[v] == d`
   after the push means it was 0 before). Without that guard the active list grows unboundedly.
4. `globalRelabel` examines `cap[e ^ 1]`, not `cap[e]` — it is a **reverse** BFS from `t`, finding
   which vertices can reach `t`.
5. `height < n` guard everywhere: height `≥ n` means "provably dead", and dead vertices must
   neither be discharged nor counted as active.

## 5. Bipartite matching via Dinic

```java
/** Maximum matching, O(E√V) via Dinic. Returns matchR[v] = matched left vertex, or -1. */
public static int[] maxBipartiteMatching(int[] adjLeft, int nL, int nR) {
    int S = nL + nR, T = S + 1;
    FlowNet g = new FlowNet(nL + nR + 2);
    g.reserve(nL + nR + adjLeft.length);
    long INF = Math.min(nL, nR);                 // tight ∞ — never binding
    for (int u = 0; u < nL; u++) g.addArc(S, u, 1);
    for (int u = 0; u < nL; u++) for (int v : adjLeft[u]) g.addArc(u, nL + v, 1);
    for (int v = 0; v < nR; v++) g.addArc(nL + v, T, 1);
    new Dinic(g).maxFlow(S, T);
    int[] matchR = new int[nR];
    java.util.Arrays.fill(matchR, -1);
    for (int e = g.head[0]; e != -1; e = g.next[e]) { /* unused */ }
    for (int u = 0; u < nL; u++)
        for (int e = g.head[u]; e != -1; e = g.next[e])
            if (g.initialCapacity[e] == 1 && g.initialCapacity[e ^ 1] == 0 && g.cap[e] == 0)
                matchR[g.to[e] - nL] = u;        // unit forward arc, fully saturated ⇒ matched
    return matchR;
}
```

The matching extraction uses `initialCapacity[e] == 1 && initialCapacity[e ^ 1] == 0` to identify
original `u→v` arcs (the reverse has capacity 0 originally), then `cap[e] == 0` to check
saturation. **This is why `initialCapacity` must be kept.**

## 6. Min-cut extraction and verification

```java
public record Cut(boolean[] inS, long capacity, long flow) {}

/** Extract a minimum cut. VERIFY: the returned capacity always equals the flow value. */
public Cut minCut(FlowNet g, int s, int t, long flowValue) {
    boolean[] inS = new boolean[g.n];
    int[] q = new int[g.n]; int qh = 0, qt = 0;
    inS[s] = true; q[qt++] = s;
    while (qh < qt) {
        int u = q[qh++];
        for (int e = g.head[u]; e != -1; e = g.next[e])
            if (g.cap[e] > 0 && !inS[g.to[e]]) { inS[g.to[e]] = true; q[qt++] = g.to[e]; }
    }
    long cap = 0;
    for (int u = 0; u < g.n; u++) if (inS[u])
        for (int e = g.head[u]; e != -1; e = g.next[e]) if (!inS[g.to[e]]) cap += g.initialCapacity[e];
    if (cap != flowValue) throw new IllegalStateException("BUG: cut " + cap + " != flow " + flowValue);
    return new Cut(inS, cap, flowValue);
}
```

**The `throw` is the point.** Cut-extraction equality is a *theorem*, so any violation is a
guaranteed bug — and it is the cheapest possible end-to-end test of the whole flow routine.

## 7. Pitfalls (8 + fixes)

1. **Forgetting `cap[e ^ 1] += delta`.** The single most consequential bug: forward-only search,
   which silently returns non-maximal flows (see QUIZ Q4 for a concrete instance).
2. **Dinic `dfs` advancing `it[u]` on success.** Skips arcs that still have residual capacity.
   Only advance when the arc is exhausted (`dfs` returned 0).
3. **Computing the cut from `cap[e]` instead of `initialCapacity[e]`.** Yields a number unrelated
   to the cut. Silent.
4. **Dinic's `if (cap[e] == 0 ...)` without `level[v] == level[u]+1`.** Loses the level graph ⇒
   loses both correctness of the blocking-flow termination argument and the `O(VE)` bound.
5. **Push–relabel `applyGap` not called** after a relabel that empties a level. You lose the
   single biggest heuristic; results stay correct.
6. **Push–relabel activating an already-active vertex** (`excess[v] > 0` check only, without the
   `excess[v] == d` transition test). The active list grows exponentially.
7. **`int` flow values.** Flow can reach `Σc`; use `long`.
8. **`Integer.MAX_VALUE` as `INF`.** Two such arcs overflow when summed. Use
   `(long) V * maxFiniteCap + 1`, or `min(|U|,|V|)` for matching.
9. **Recursion depth in `dfs`.** Path length `≤ V`; for `V > 10⁴` you can blow the Java stack.
   Convert to an iterative blocking-flow routine.

## 8. Micro-optimisations

- Flat `int[]`/`long[]` edge arrays instead of an object graph: 4–8× on large instances.
- `head[]`-based adjacency (as above) beats `List<List<Edge>>` — no per-vertex allocation, no
  pointer chasing.
- BFS with an `int[]` queue instead of `ArrayDeque<Integer>` — removes boxing entirely.
- Reset `it[]` inside `bfs` (one pass) rather than in a separate loop.
- Push–relabel: bucket the active list by height (`count[]` + per-height lists) instead of
  re-sorting; this is the standard "highest-label with buckets" and is significantly faster.
- Global-relabel frequency: 4·|E| is a good default; tune by measuring.
- For bipartite matching, use Hopcroft–Karp directly instead of a general Dinic — ~2× on large
  sparse instances because the specialised implementation avoids the general machinery.

## 9. Checklist

- [ ] Edge array with `e ^ 1` reverse indexing; `cap[e ^ 1]` updated on every push.
- [ ] `initialCapacity` kept (required for cut extraction and matching extraction).
- [ ] Dinic: `level[v] == level[u]+1` filter present; `it[]` advanced only on exhaustion.
- [ ] Push–relabel: `height[s] = V`; gap heuristic wired in; global relabel periodic.
- [ ] Push–relabel: activation guard `excess[v] == delta` (0 → positive transition).
- [ ] `long` for capacities, flows, and `INF`.
- [ ] `cutCapacity == flowValue` asserted after every run.
- [ ] Cross-validated: Edmonds–Karp vs Dinic vs push–relabel on random graphs, `V ≤ 40`.