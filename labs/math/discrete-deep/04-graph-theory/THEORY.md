# Graph Theory — Theory

## 1. Handshaking: The Degree Ledger

Σ deg(v) = 2|E| always — each edge pays its two endpoints. On the lab's
7-edge graph with degrees (0:2, 1:4, 2:3, 3:3, 4:2), the run printed
both sides as 14. Corollaries arrive free: the number of odd-degree
vertices is even (odds here: 2 and 3), and an n-vertex graph can't have
all distinct degrees (degrees live in 0..n−1, but 0 and n−1 conflict).

## 2. Euler: Trail vs Circuit, With a Search to Prove It

A connected multigraph has an Euler circuit iff every degree is even;
an Euler trail iff exactly two degrees are odd (start at one, end at
the other). The lab's graph has odd vertices {2,3}, and the DFS search
found the trail 2 → 0 → 1 → 2 → 3 → 1 → 4 → 3, all 7 edges used
exactly once (run-printed walk and the once-only certificate True).
The earlier 6-edge version of this graph had FOUR odd vertices and the
same search returned None — the condition is arithmetic, not search
luck: each interior visit consumes two incidences, so odd vertices need
to be endpoints.

## 3. Hamilton: Dirac's Bound, and Why It's Not a Classification

Euler is degree-theoretic; Hamiltonicity is structural. Dirac: n ≥ 3
vertices with deg(v) ≥ n/2 everywhere force a Hamilton cycle. Checks
by hand: K₅ has all degrees 4 ≥ 2.5 and is Hamiltonian; C₅ has degrees
2 < 2.5 yet is still Hamiltonian — the bound is sufficient, never
necessary. The decision problem is NP-complete, which is the precise
reason no clean degree certificate can exist on both sides.

## 4. Trees: Counting Connected Minimal Graphs

A tree on n vertices is exactly a connected graph with n−1 edges
(equivalently: n−1 edges and acyclic; equivalently: acyclic and every
pair joined by a unique path). Labeled counts obey Cayley n^(n−2),
verified by exhaustive union-find enumeration on the run at
n = 2, 3, 4, 5, 6: brute and n^(n−2) give 1, 3, 16, 125, 1296 with
equal True at every step. K₄ therefore admits 16 spanning trees while
carrying only C(4,2) = 6 admissible edge slots — most trees share
edges, none share all.

## 5. Connectivity Census on 4 Vertices

The run enumerated all edge subsets of K₄ by size m and audited
connected + acyclic: m = 3 is where all 16 trees live (16 connected,
16 acyclic — the two coincide exactly there); m = 4, 5, 6 give 15, 6,
1 connected graphs with ZERO acyclic (Pigeonhole: ≥ n edges force a
cycle in a 4-vertex graph); m ≤ 2 have no connected members, and all
their 1, 6, 15 members are forests — an m-edge cycle needs m ≥ 3.
Summary read off the printout: connectedness needs edges, acyclicity
needs scarcity, and trees are the exact knife-edge m = n−1.

## 6. Planarity: Bounds and the Two Forbidden Minors

Any planar graph with n ≥ 3 vertices obeys |E| ≤ 3n−6 (all faces ≥ 3
sides, Euler's V − E + F = 2 does the arithmetic). K₅ has 10 edges
against bound 9 — rejected by counting alone. K₃,3 is bipartite
(girth 4), tightening the bound to |E| ≤ 2n−4, and 9 > 8 rejects it too.
K₄ is exactly tight: 6 = 3·4−6, the maximal-planar equality; Petersen
(n = 10, |E| = 15 ≤ 24) slips under the edge bound and needs its
K₃,3-minor for rejection — the bound screens but does not resolve.
Kuratowski: precisely K₅ and K₃,3 subdivisions are the only blockers.

## 7. The Lab's Programs

Program 1 runs handshaking and a full Euler trail search, locating 7
walked edges; program 2 carries the Cayley cross-checks, the planarity
bounds including the boundary case and Petersen's dodge, and the
by-size connectivity/acyclicity census over all 64 edge subsets of K₄.
