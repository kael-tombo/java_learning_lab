# Graph Theory — Lab 04 of Discrete Deep

The degree ledger paid exactly (14 = 2|E|), an Euler trail actually
walked by search, Cayley checked at five sizes, a 64-subgraph census
of K4, and planarity bounds with the Petersen escape. All numbers
from captured runs.

## What each file contains

- THEORY.md: handshaking and its corollaries; Euler trail/circuit
  arithmetic with the located walk 2→0→1→2→3→1→4→3; Dirac's bound and
  why Hamiltonicity stays structural; trees as the m = n−1 knife-edge
  with Cayley counts; the K4 census rows; planarity via |E| ≤ 3n−6 and
  |E| ≤ 2n−4 with Kuratowski's two minors.
- MATH_FOUNDATION.md: degrees 2,4,3,3,2 summing to 14; the trail's
  edge residues; Cayley's pairwise/create ratios (7.8, then 10.368);
  census rows 0/0/0/16/15/6/1 connected with 1/6/15 forests below
  m = 3; the planarity budget row
  (6=6, 10>9, 15>12, 21>15, 45>24).
- CODE_DEEP_DIVE.md: two executed Python programs — handshaking with
  DFS Euler trail search; Cayley brute-force, the planarity bound
  battery, and the connectivity/acyclicity census with union-find.
- EXERCISES.md: five worked problems (handshake audit, trail
  location, the 4-odd-vertex kill, Cayley at n = 5, planar budget).
- FLASHCARDS.md: twelve cards carrying run-verified figures only.

## Prerequisites within the track

Lab 02's exhaustion idea here becomes the 64-subgraph census; Lab 03's
handshake of binomial counts supplies C(4,2) = 6 and the m-by-m audit.
The degree bookkeeping transfers to Lab 06's congruence classes
(counting incidences, not values), and the census tree column is the
bridge forward into Lab 05's product-of-choices generating functions.

## Do this

Trace the found trail by hand against the printed edge list; the
moment every edge is crossed exactly once is the theorem made
concrete. Then read program 2's census and compare the m = 3 row
(16 = 16) against Cayley's 16 — the disk-number coincidence between
connected and acyclic is literally the definition of tree, seen as data.
