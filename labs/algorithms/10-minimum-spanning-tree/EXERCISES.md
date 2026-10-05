# EXERCISES — Minimum Spanning Tree
> Implement + trace + edge cases. Java templates included.

## Level 1 — Mechanics
### E1 Kruskal (25 min)
```java
static class DSU { int[] p, r;
    DSU(int n){/*TODO*/}
    int find(int x){/*TODO path compression*/ return 0;}
    boolean union(int a,int b){/*TODO by rank*/ return false;}
}
public static long kruskal(int n, int[][] edges /*{u,v,w}*/) {
    // TODO: sort by w; union if separated; sum; count==n-1 else forest sum
    return 0;
}
```
- Trace triangle `AB1 BC2 AC3`: sorted order, union steps, skipped edge.

### E2 Prim (25 min)
```java
public static long prim(int n, List<int[]>[] adj /*{to,w}*/, int s) {
    // TODO: PQ fringe; inTree[]; pop min crossing; sum
    return 0;
}
```
- Trace same triangle from `s=0`; show PQ contents per pop.

### E3 Cut-property note (10 min)
- For each taken edge write the cut it crosses (1 sentence). E.g., `{A}|{B,C}` lightest = AB.

## Level 2 — Edge Cases
### E4 Disconnected → forest
- Two components: expect MSF (both trees), document behavior vs exception.

### E5 Ties + negatives
- Square all `w=1`: any 3 edges, total 3. Negative `-5` edge must be taken (no cycle logic changes).

### E6 Large weights overflow
- Sums near `Integer.MAX`: use `long`; test `w=1e9 × 3` edges.

## Level 3 — Trace Tables
| Sorted edge | find(u)?=find(v)? | Take? | Total |
|-------------|-------------------|-------|-------|
| AB1 | N | Y | 1 |
| BC2 | N | Y | 3 |
| AC3 | Y (A~C) | N | 3 |
- Reproduce for a 5-node custom graph.

## Level 4 — Property Tests
- P1: `total` equals on Kruskal vs Prim over 30 random graphs (fixed seed).
- P2: acyclicity: taken edges `== V-comp`, no cycle via DSU replay.
- P3: brute force on `n≤7`: MST weight == min over all spanning trees (enumerate).

## Level 5 — Stretch
- S1 Borůvka round (parallel-friendly) sketch.
- S2 Second-best MST (硬度 up): max-edge-on-path query.
- S3 Real network (see MINI_PROJECT): wire mock cities, print savings vs naive star.

## Submission Checklist
- [ ] DSU + both algos + traces.
- [ ] Forest/tie/overflow tests.
- [ ] Random cross-check + brute-force small.
- [ ] `O(E log E)` / `O(E log V)` notes.
