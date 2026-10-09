# Step-by-Step: Dijkstra on a 6-Node Graph

Graph (undirected, nonnegative weights) — adjacency listing:

```
A: B(4), C(2)
B: A(4), C(1), D(5)
C: A(2), B(1), D(8), E(10)
D: B(5), C(8), E(2), F(6)
E: C(10), D(2), F(3)
F: D(6), E(3)
```

Edge list (authoritative): A–B 4, A–C 2, B–C 1, B–D 5, C–D 8, C–E 10, D–E 2, D–F 6, E–F 3. Source: **A**.

## Initialization

| node | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| dist | 0 | ∞ | ∞ | ∞ | ∞ | ∞ |
| settled | no | no | no | no | no | no |

Rule: pop the *unsettled node with minimum dist* (not alphabetically), relax its edges, skip already-settled neighbors.

## Round 1 — settle A (0)

- A→B: 0+4 = 4 → dist(B) = 4, parent(B) = A
- A→C: 0+2 = 2 → dist(C) = 2, parent(C) = A

State: A 0* | B 4 | C 2 | D ∞ | E ∞ | F ∞

## Round 2 — settle C (2) — beats B's 4

- C→B: 2+1 = 3 < 4 → dist(B) = 3, parent(B) = C  ← the direct A–B edge (4) is not optimal
- C→D: 2+8 = 10 → dist(D) = 10, parent(D) = C
- C→E: 2+10 = 12 → dist(E) = 12, parent(E) = C

State: A 0* | B 3 | C 2* | D 10 | E 12 | F ∞

## Round 3 — settle B (3)

- B→D: 3+5 = 8 < 10 → dist(D) = 8, parent(D) = B  ← route A–C–B–D = 2+1+5 = 8

State: A 0* | B 3* | C 2* | D 8 | E 12 | F ∞

## Round 4 — settle D (8)

- D→E: 8+2 = 10 < 12 → dist(E) = 10, parent(E) = D
- D→F: 8+6 = 14 → dist(F) = 14, parent(F) = D

State: A 0* | B 3* | C 2* | D 8* | E 10 | F 14

## Round 5 — settle E (10)

- E→F: 10+3 = 13 < 14 → dist(F) = 13, parent(F) = E

State: A 0* | B 3* | C 2* | D 8* | E 10* | F 13

## Round 6 — settle F (13). Done. (* = settled)

## Result

| node | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| shortest distance | 0 | 3 | 2 | 8 | 10 | 13 |

Paths via parent pointers:
- B: A→C→B = 3 (beats direct A→B = 4)
- D: A→C→B→D = 8 (beats A→B→D = 9 and A→C→D = 10)
- E: A→C→B→D→E = 10 (beats A→C→E = 12)
- F: …→E→F = 13 (beats the D→F branch = 14)

## Sanity Checks

1. Invariant: a settled distance never changes afterward — assert in code: stale pops are skipped (`if (d != dist[v]) continue;`).
2. Alternatives: A–B–D–E–F = 4+5+2+3 = 14 > 13 ✓; A–C–D–F = 2+8+6 = 16 > 13 ✓; A–C–E–F = 2+10+3 = 15 > 13 ✓.
3. Work: 6 pops, 8 edges relaxed (each undirected edge examined at most twice) — with a binary heap the bound is O((V+E) log V); 6 nodes, 9 edges, ~15 heap operations.
4. This trace is the golden test fixture for lab 04's shortest-path implementations.
