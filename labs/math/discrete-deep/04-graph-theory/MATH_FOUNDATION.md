# Graph Theory — Math Foundation

Values below are pasted from the captured runs of CODE_DEEP_DIVE.md;
each census ran before any claim was written.

## 1. Handshaking on the 7-Edge Graph

Edges: (0,1),(0,2),(1,2),(1,3),(2,3),(3,4),(4,1). Observed degrees:
0:2, 1:4, 2:3, 3:3, 4:2; sum 14 = 2|E| = 14 (run: equal True). Odd
vertices: {2, 3} — two of them, which is the Euler-trail license.

## 2. The Trail, Located and Certified

Run output: edge sequence [1, 0, 2, 4, 3, 6, 5] reconstructs the walk
2 → 0 → 1 → 2 → 3 → 1 → 4 → 3 (verified residues below). Edge 1 is
(0,2): 2→0; edge 0 is (0,1): 0→1; edge 2 is (1,2); edge 4 is (2,3);
edge 3 is (1,3); edge 6 is (4,1); edge 5 is (3,4). All 7 edges appear
once (run: all edges once True), starting at odd vertex 2. Contrast
run: the 4-odd-vertex variant returned None — 0 or 2 odd vertices is
an if-and-only-if, and the fourth odd kills it.

## 3. Cayley, Six-Way Checked

Brute spanning-tree counts vs n^(n−2): n=2: 1 = 1; n=3: 3 = 3;
n=4: 16 = 16; n=5: 125 = 125; n=6: 1296 = 1296; each row printed equal
True. Growth accelerates: 125/16 ≈ 7.8 from n = 4 to 5, then
1296/125 = 10.368 to n = 6 — Cayley's factor grows roughly linearly.

## 4. Connectivity Census Over All 64 Subgraphs of K4

Printed rows as (m, connected, acyclic, trees):
- (0,0,1,0), (1,0,6,0), (2,0,15,0): zero connected graphs, but acyclic
  members number 1, 6, 15 — every ≤ 2-edge subset is a forest, since a
  cycle needs 3 edges on 4 vertices.
- (3,16,16,16): connected and acyclic coincide — the 16 trees = 4².
- (4,15,0,0), (5,6,0,0), (6,1,0,0): connected 15, 6, 1, acyclic 0 —
  ≥ n edges force a cycle (Pigeonhole).
Total graphs = 2^C(4,2) = 64; total trees across all m = 16 = 4^2,
the Cayley value for n = 4. One row carries the whole theory: exactly
m = n − 1 = 3 slots admit connected-acyclic graphs, and there all 16
live.

## 5. Planarity Bounds, Numeric Row

|E| ≤ 3n−6: K5 rejected, 10 > 9 (run-printed True). Bipartite form
|E| ≤ 2n−4: K3,3 rejected, 9 > 8 (run True). K4 boundary: 6 = 6,
covered by equality as a maximal planar (triangulated) graph. Petersen:
n = 10, |E| = 15 ≤ 24, run says the edge bound does not reject it —
actual rejection demands the K3,3 minor. Budget row printed:
C(5,2) = 10 vs 9; C(6,2) = 15 vs 12; C(7,2) = 21 vs 15; C(10,2) = 45
vs 24 — the complete graph crosses the planar budget from n = 5 on.

## 6. Degree-Sum Double-Check on K3,3

Six vertices each of degree 3: sum 18 = 2·9 = 2|E| (printed). The
handshake ledger licenses the bipartite count: edges cross only
between parts, so each part's degrees sum to 9, the total edge count.
