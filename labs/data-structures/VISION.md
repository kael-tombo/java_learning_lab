# Data Structures Track — Vision

## Where this track goes
From array indexing to link-cut trees: 35 labs that turn "knows the name"
into "can implement, analyze, and operate it." Each lab pairs interview
preparation (MOCK_INTERVIEW.md) with a production-flavored build
(REAL_WORLD_PROJECT.md) so concepts transfer to real systems.

## The arc
- Labs 01-08 build fluency: dynamic arrays, pointer surgery on lists,
  stack/queue discipline, tree traversals, graph search (BFS/DFS/topo),
  hash table internals, heap patterns (top-K, median), trie prefix search.
- Labs 09-20 build judgment: balanced trees and when B-trees win on disk,
  Bloom sizing by formula, DSU for connectivity, segment vs Fenwick vs
  sparse-table range queries, skip lists, LRU eviction, concurrent maps
  and queues, spatial indexes, ring buffers, persistent versions.
- Labs 21-35 build depth: open-addressing variants, Merkle proofs, undoable
  DSU for offline connectivity, locality tricks (unrolled lists, Morton codes,
  cache-oblivious layouts), cardinality/frequency/similarity sketches,
  vEB integer structures, ropes, exact-cover search, treaps, versioned
  segment trees, dynamic-forest link-cut trees.

## How success looks
A graduate sizes an LRU by hit-rate SLO, picks Fenwick over a segment tree
for prefix sums, reaches for a sketch with a stated error budget instead of
unbounded memory, and can whiteboard path copying, lazy propagation, cuckoo
displacement, or Merkle inclusion proofs with correct complexities.

## Non-goals
Not a cookbook of memorized solutions: every claim ties to an invariant you
can state, a complexity you can derive, and a snippet you can run. Not
coverage for its own sake: exotic structures earn their labs by real uses
(maps, caches, indexes, sync proofs, solvers) documented per lab.

## Maintenance
Keep snippets compiling under `javac --release 21`, outputs observed (never
guessed), prose ASCII-clean in code output, and each file within 30-80
content lines. When the JDK changes behavior relied upon, update the lab.
