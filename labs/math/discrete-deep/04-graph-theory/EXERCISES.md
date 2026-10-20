# Exercises — Graph Theory

Five problems with worked solutions; every figure is quoted from the
captured runs in CODE_DEEP_DIVE.md.

## Problem 1. Handshake Audit

On edges (0,1),(0,2),(1,2),(1,3),(2,3),(3,4),(4,1), list degrees and
verify Σ deg = 2|E|.

**Solution**: Run-printed: 0:2, 1:4, 2:3, 3:3, 4:2. Sum = 14 and
2|E| = 14, equal True. Odd vertices are 2 and 3 — exactly two, the
Euler-trail signature.

## Problem 2. Locate the Euler Trail

Find an Euler trail on that graph and confirm every edge is used once.

**Solution**: The search returned edge sequence [1,0,2,4,3,6,5]
reconstructing walk 2 → 0 → 1 → 2 → 3 → 1 → 4 → 3, with
"all 7 edges once: True" printed and start at odd vertex 2. Edge
residues: 1=(0,2) consumed from 2; 0=(0,1) from 0; 2=(1,2); 4=(2,3);
3=(1,3); 6=(4,1); 5=(3,4).

## Problem 3. Four Odd Vertices Kill It

Delete edge (4,1): degrees become 0:2, 1:3, 2:3, 3:3, 4:1. Does an
Euler trail exist?

**Solution**: No — four odd vertices, and the earlier run's searcher
returned None on precisely this shape. Reason: each visit to a vertex
pair-consumes incidences; any vertex with odd degree must be a trail
endpoint, and a walk has only two ends. 0 odd ⟺ circuit;
2 odd ⟺ trail; anything else: impossible.

## Problem 4. Cayley at n = 5, Two Roads

Verify 5^(5−2) = 125 by independent enumeration, and state K₄'s
spanning-tree count the same way.

**Solution**: Brute union-find filter printed 125 for n = 5,
equal True, as well as 1, 3, 16 at n = 2, 3, 4 and 1296 at n = 6.
For K₄: 16 = 4² spanning trees, again printed twice — once as the
m = 3 census row, once as the summed tree column of the program-2
run.

## Problem 5. Planar Budget Arithmetic

(a) How do K5 and K3,3 fail planarity by counting alone? (b) Why can't
the same arithmetic reject the Petersen graph? (c) State the tight
case.

**Solution**: (a) Run rows: K5: |E| = 10 > 3n−6 = 9 (True), rejected.
K3,3: |E| = 9 > 2n−4 = 8 (True), rejected by the sharper bipartite
bound — its girth is 4, so faces have ≥ 4 edges. (b) Petersen has
|E| = 15 ≤ 3·10−6 = 24, so the bound passes and only the K3,3-minor
argument rejects it — arithmetic limits, not full classifications.
(c) K4 at |E| = 6 = 3·4−6 exactly: the maximal-planar equality where
every face is a triangle.
