# Data Structures Track - Vision

## Direction
Thirty-five labs carry builders from array indexing to link-cut trees,
turning name recognition into implement, analyze, and operate. Interview
readiness (MOCK_INTERVIEW.md) pairs with a production-style build
(REAL_WORLD_PROJECT.md) in each lab so ideas survive contact with real
workloads.

## The progression
- Labs 01-08 build fluency: growable arrays, list pointer surgery,
  stack and queue discipline, traversal habits, graph search (BFS, DFS,
  topo order), hash internals, heap patterns (top-K, median), prefix
  search on tries.
- Labs 09-20 build judgment: balanced trees and the disk case for
  B-trees, Bloom sizing from its formula, connectivity via DSU, range
  options (segment vs Fenwick vs sparse table), skip lists, LRU policy,
  concurrent maps and queues, spatial indexes, ring buffers, versioned
  structures.
- Labs 21-35 build depth: open-addressing designs, Merkle proofs,
  undoable DSU for offline questions, locality craft (unrolled lists,
  Morton codes, oblivious layouts), sketch trio (cardinality, frequency,
  similarity), vEB integer search, ropes, exact-cover solving, treaps,
  versioned segment trees, dynamic forests.

## Graduate profile
A finisher sizes a cache from a hit-rate SLO, picks Fenwick for pure
prefix traffic, reaches for a sketch with a written error budget over
unbounded memory, and can derive path copying, lazy propagation, cuckoo
displacement, or Merkle inclusion cost from first principles.

## Boundaries
This track is not memorized solutions: each claim links to an invariant
stated in words, a complexity derived on paper, and behavior observed in
a run. Exotic structures justify their labs through deployed uses -
caches, indexes, sync proofs, solvers - named in each lab.

## Upkeep
Snippets compile under `javac --release 21` with observed outputs, code
output stays plain ASCII, and every doc holds 30-80 content lines. When
JDK behavior shifts under a lab, the lab gets updated.
