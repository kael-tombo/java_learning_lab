# Visual Guide: Graph Theory

## 1. The Königsberg Bridge Graph (Euler, 1736)

Seven bridges link four landmasses: north bank (A), south bank (B), and two islands (C, D). Model each landmass as a vertex and each bridge as an edge:

```
    A ---- C ---- B
          |  \
          |   \
          D ----   (7 bridges: degrees A:3, B:3, C:3, D:3 in the classic rendition)
```

Euler's rule: a trail using every edge exactly once exists iff the graph has **0 or 2 vertices of odd degree** (0 = closed circuit, 2 = start at one odd end, finish at the other). All four vertices are odd (4 odd vertices) → no such walk. Nothing about distances, directions, or positions entered the argument — only degrees.

## 2. BFS Layers = Distance Rings

```
            level 0:   A
            level 1:   B   C        (1 edge from A)
            level 2:   D   E   F    (2 edges from A)
            level 3:   G            (3 edges from A)
```

Each level is discovered completely before the next — the queue holds at most two adjacent levels. Property to remember: an edge between levels differing by more than 1 cannot exist in an unweighted BFS tree (it would have shortened a path).

## 3. DFS Back-Edge = Cycle

```
   A → B → C → D
       ↑       |
       └───────┘        (D → B is a "back edge" to a gray node)
```

Three-color discipline: white = unvisited, gray = on current recursion stack, black = finished. Edges: tree (to white), forward (to black), cross (to black, unrelated), **back (to gray) → cycle detected**. A DAG has no back edges under any DFS.

## 4. Cut and Max-Flow = Min-Cut

Graph: s→a capacity 3, s→t capacity 1, a→t capacity 2.

```
        a
      3/ \2
     s    t
      \1 /
```

- Max flow: push 2 along s→a→t (bottleneck 2), then 1 along s→t. Total **3**; no augmenting path remains (s→a has 1 left but a→t is saturated).
- Cuts: {s} vs {a,t} costs 3 + 1 = 4; {s,a} vs {t} costs 2 + 1 = 3. Minimum = **3**.
- Max-flow min-cut: 3 = 3 ✓. The tight cut ({s,a} | {t}) is the network's bottleneck — every unit reaching t must cross it.

## 5. Spanning Tree (Kruskal on the Lab's 6-Node Graph)

Edges in ascending weight order, adding only if the endpoints are in different components:

| # | edge | weight | decision | running total |
|---|---|---|---|---|
| 1 | B–C | 1 | add | 1 |
| 2 | A–C | 2 | add | 3 |
| 3 | D–E | 2 | add | 5 |
| 4 | E–F | 3 | add | 8 |
| 5 | A–B | 4 | reject — cycle A–C–B | 8 |
| 6 | B–D | 5 | add (merges {A,B,C} with {D,E,F}) | 13 |
| 7+ | D–F, C–D, C–E | 6, 8, 10 | all rejected — cycles | 13 |

Stop at V − 1 = 5 edges. **MST weight = 13**, tree = {B–C, A–C, D–E, E–F, B–D}. Check with the cut property: partition {A,B,C} needs 2 cheapest internal edges (1 + 2 = 3), {D,E,F} needs 2 (2 + 3 = 5), and the cheapest bridge between the parts is B–D = 5 — 3 + 5 + 5 = 13, matching Kruskal exactly.

## 6. Bipartite Matching (Hall's Condition Visual)

```
   X = {x1, x2, x3}   edges: x1-y1, x1-y2, x2-y2, x3-y3
   Y = {y1, y2, y3}
   OK:  N({x1,x2}) = {y1,y2} (|N|=|S| ✓),  N({x1,x2,x3}) = {y1,y2,y3} ✓
   FAIL: give x3 only y1 while x1,x2 also reach only {y1,y2}:
         S = {x1,x2,x3}, N(S) = {y1,y2} → |N(S)| = 2 < 3 → no full matching
```

Drawn as two rows with edges between them: Hall's theorem says a perfect left-side matching exists iff **no** left subset is "squeezed" into a smaller right neighborhood — visually, no left group whose edges all land inside a smaller right group.
