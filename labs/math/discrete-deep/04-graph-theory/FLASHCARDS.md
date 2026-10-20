# Graph Theory — Flashcards (Verified Numbers)

Figures here are quoted directly from the captured runs of CODE_DEEP_DIVE.md.

### Card 1
**Front**: Handshaking lemma, with the run's example?
**Back**: Σ deg(v) = 2|E|; on the 7-edge graph, degrees 2,4,3,3,2 sum
to 14 = 2·7, printed equal True. Odd-degree vertices always even in
number.

### Card 2
**Front**: Euler circuit vs trail conditions?
**Back**: Circuit iff all degrees even; trail iff exactly two odd
vertices. The run's graph had odds {2,3} and yielded the walked path;
the 4-odd variant returned None.

### Card 3
**Front**: The found trail, as a vertex walk?
**Back**: 2 → 0 → 1 → 2 → 3 → 1 → 4 → 3, edges [1,0,2,4,3,6,5], all
7 used once (run certificate True), starting at odd vertex 2 and
ending at odd vertex 3.

### Card 4
**Front**: Cayley's formula and its checked values?
**Back**: n^(n−2) labeled trees. Brute-verified: 1, 3, 16, 125, 1296
for n = 2..6, each with equal True.

### Card 5
**Front**: Spanning trees of K4?
**Back**: 16 = 4². The program-2 run exhibited it twice: the m = 3
census row (connected 16 = acyclic 16) and the summed tree count.

### Card 6
**Front**: What does the m-by-m census on K4 show?
**Back**: Tuple rows (m, connected, acyclic, trees): m ≤ 2 give
(0,0,1,0), (1,0,6,0), (2,0,15,0) — no connected graphs but 1, 6, 15
forests; m = 3: (16,16,16) connected = acyclic; m = 4,5,6: 15, 6, 1
connected, zero acyclic. 2^6 = 64 graphs total.

### Card 7
**Front**: Why is ≥ n edges always cyclic on n vertices?
**Back**: Trees maximize the edge count of an acyclic graph at n−1;
the m = 4..6 rows in the run report acyclic 0 — the forest budget is
n−1, spent or exceeded.

### Card 8
**Front**: Dirac's theorem, statement and its trap?
**Back**: n ≥ 3 and deg(v) ≥ n/2 for all v force a Hamilton cycle.
Sufficient only: C5 has degrees 2 < 2.5 yet is Hamiltonian; and the
decision problem is NP-complete, so no two-sided degree test exists.

### Card 9
**Front**: Planar edge bound(s)?
**Back**: |E| ≤ 3n−6 (n ≥ 3); bipartite tightening |E| ≤ 2n−4 when
girth ≥ 4. From Euler's V − E + F = 2 with face degrees ≥ 3 (or ≥ 4).

### Card 10
**Front**: K5 and K3,3 by the bounds?
**Back**: K5: 10 > 9 (run True). K3,3: 9 > 8 (run True) using the
bipartite bound; its degree sum reads 6·3 = 18 = 2·9.

### Card 11
**Front**: Which classic graph dodges the edge bound?
**Back**: The Petersen graph: n = 10, |E| = 15 ≤ 24 (run: bound does
not reject), yet nonplanar via the K3,3 minor — Kuratowski's two
forbidden minors, K5 and K3,3, are exhaustive.

### Card 12
**Front**: The C(n,2) vs 3n−6 budget row?
**Back**: n = 4: 6 vs 6 (tight); n = 5: 10 vs 9 (K5 crosses); n = 6:
15 vs 12; n = 7: 21 vs 15; n = 10: 45 vs 24 — complete graphs are
nonplanar from n = 5 onward, by arithmetic alone.
