# Visual Guide to Union-Find

## Part 1: Basic Operations

### Initial State: 6 elements (0-5)
`
  0    1    2    3    4    5
  |    |    |    |    |    |
  0    1    2    3    4    5    (parent array)
`

### After union(0, 1):
`
  0    2    3    4    5
   \   |    |    |    |
    1  2    3    4    5
`
Parent array: [0, 0, 2, 3, 4, 5]
Rank array:   [1, 0, 0, 0, 0, 0]

### After union(2, 3):
`
  0    2    4    5
   \    \   |    |
    1    3  4    5
`
Parent: [0, 0, 2, 2, 4, 5]

### After union(0, 2) with union by rank:
`
     0         4    5
   /   \       |    |
  1     2      4    5
         \
          3
`
Parent: [0, 0, 0, 2, 4, 5]
Rank:   [1, 0, 0, 0, 0, 0]

Wait — rank[0] = 1, rank[2] = 1, so after union: rank[0] becomes 2.

`
     0         4    5
   / | \       |    |
  1  2  3      4    5
`
Parent: [0, 0, 0, 0, 4, 5]
Rank:   [2, 0, 0, 0, 0, 0]

### After union(4, 5):
`
     0         4
   / | \       \
  1  2  3       5
`
Parent: [0, 0, 0, 0, 4, 4]
Rank:   [2, 0, 0, 0, 1, 0]

## Part 2: Path Compression in Action

Without path compression, find(3) would traverse: 3 → 2 → 0
With path compression, find(3) does: parent[3] = find(2) = find(0) = 0
Result: parent[3] = 0, and parent[2] = 0 (already compressed)

After find(3) with path compression:
`
         0            4
   /  |  |  \         \
  1   2  3   ...       5
`
Parent: [0, 0, 0, 0, 4, 4]

## Part 3: Kruskal's Algorithm

Graph with vertices A-F and weighted edges:

Edge weights: (A-B: 2), (C-D: 3), (A-D: 4), (B-C: 5), (B-E: 7), (D-F: 8), (E-F: 9)

1. Start: Each vertex is its own set
2. Process (A-B, 2): union(A,B) → {A,B}, {C}, {D}, {E}, {F}
3. Process (C-D, 3): union(C,D) → {A,B}, {C,D}, {E}, {F}
4. Process (A-D, 4): union(A,D) → {A,B,C,D}, {E}, {F}
5. Process (B-C, 5): already connected, skip
6. Process (B-E, 7): union(A,B,C,D with E) → {A,B,C,D,E}, {F}
7. Process (D-F, 8): union(A,B,C,D,E with F) → {A,B,C,D,E,F} — all connected
8. MST weight = 2 + 3 + 4 + 7 + 8 = 24
