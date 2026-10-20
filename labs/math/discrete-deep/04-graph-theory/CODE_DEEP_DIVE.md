# Code Deep Dive — Graph Theorems, Searched and Counted

Two runnable Python programs (stdlib only); observed-output blocks are verbatim runs.

## 1. Handshaking Plus an Actual Euler Trail Search

```python
edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (4, 1)]
deg = {v: sum((u == v) + (w == v) for u, w in edges) for v in range(5)}
print("degrees:", sorted(deg.items()))
print("sum(degrees) = %d, 2|E| = %d, equal: %s" % (sum(deg.values()), 2 * len(edges), sum(deg.values()) == 2 * len(edges)))
odd = [v for v, d in deg.items() if d % 2]
print("odd-degree vertices:", [v for v, d in deg.items() if d % 2], "count:", len(odd))

def euler_trail(edges):
    n = 1 + max(max(u, v) for u, v in edges)
    adj = {i: [] for i in range(n)}
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i)); adj[v].append((u, i))
    def dfs(v, used):
        if len(trail) == len(edges): return v
        for w, i in adj[v]:
            if not used[i]:
                used[i] = True
                trail.append(i)
                r = dfs(w, used)
                if r is not None: return r
                used[i] = False; trail.pop()
        return None
    for s in adj:
        trail = []
        if dfs(s, [False] * len(edges)) is not None: return trail

t = euler_trail(edges)
print("edge indices of a found Euler trail:", t)
walk, at = [odd[0]], odd[0]
for i in t:
    at = edges[i][1] if edges[i][0] == at else edges[i][0]; walk.append(at)
print("vertex walk:", walk)
print("starts at odd vertex %d: %s; all %d edges once: %s" % (odd[0], walk[0] == odd[0], len(edges), len(set(t)) == len(edges)))
```

Observed output:

```text
degrees: [(0, 2), (1, 4), (2, 3), (3, 3), (4, 2)]
sum(degrees) = 14, 2|E| = 14, equal: True
odd-degree vertices: [2, 3] count: 2
edge indices of a found Euler trail: [1, 0, 2, 4, 3, 6, 5]
vertex walk: [2, 0, 1, 2, 3, 1, 4, 3]
starts at odd vertex 2: True; all 7 edges once: True
```

## 2. Cayley Cross-Checks, Planarity Bounds, and the K4 Census

```python
import itertools

def audit(n, edges):
    parent, merges = list(range(n)), 0
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv; merges += 1
    return merges == n - 1, merges == len(edges), (merges == n - 1 and merges == len(edges))

n = 4
all_e = list(itertools.combinations(range(n), 2))
vals = [(m,) + tuple(sum(x[i] for x in [audit(n, c) for c in itertools.combinations(all_e, m)])
        for i in range(3)) for m in range(len(all_e) + 1)]
print("census (m, connected, acyclic, trees):", [(m, c, a, t) for m, c, a, t in vals])
print("total graphs 2^6 = %d; summed trees = %d = 4^2" % (2 ** 6, sum(t for *_r, t in vals)))

def brute_trees(nn):
    return sum(audit(nn, c)[1] for c in itertools.combinations(itertools.combinations(range(nn), 2), nn - 1))
print("Cayley n^(n-2) vs brute:", [(nn, brute_trees(nn), nn ** (nn - 2),
      brute_trees(nn) == nn ** (nn - 2)) for nn in (2, 3, 4, 5, 6)])
print("planarity: K5 |E|=10 vs 3n-6=9:", 10 > 9, "| K3,3 |E|=9 vs 2n-4=8:", 9 > 8, "| Petersen |E|=15 vs 3n-6=24: under bound, needs K3,3-minor")
print("C(n,2) = c vs 3n-6 = b:", [(nn, nn * (nn - 1) // 2, 3 * nn - 6) for nn in (4, 5, 6, 7, 10)])
```

Observed output:

```text
census (m, connected, acyclic, trees): [(0, 0, 1, 0), (1, 0, 6, 0), (2, 0, 15, 0), (3, 16, 16, 16), (4, 15, 0, 0), (5, 6, 0, 0), (6, 1, 0, 0)]
total graphs 2^6 = 64; summed trees = 16 = 4^2
Cayley n^(n-2) vs brute: [(2, 1, 1, True), (3, 3, 3, True), (4, 16, 16, True), (5, 125, 125, True), (6, 1296, 1296, True)]
planarity: K5 |E|=10 vs 3n-6=9: True | K3,3 |E|=9 vs 2n-4=8: True | Petersen |E|=15 vs 3n-6=24: under bound, needs K3,3-minor
C(n,2) = c vs 3n-6 = b: [(4, 6, 6), (5, 10, 9), (6, 15, 12), (7, 21, 15), (10, 45, 24)]
```

Census rows (m, connected, acyclic, trees): the 1, 6, 15 at m ≤ 2 are disconnected forests; trees live only at m = 3, reading 16 two ways.
