# VISION — Data Structures Track
> Direction: from using collections to choosing them — bounds, constants, and the adversarial input that separates the two.

## Where this sits
- Sequences: dynamic arrays (amortized O(1), cache-friendly) vs linked lists (O(1) splicing, pointer-chasing reads).
- Associative: hash maps (expected O(1), load-factor discipline) vs balanced trees (O(log n), ordered).
- Priority: binary heaps O(log n) with decrease-key via index maps. Connectivity: union-find at inverse-Ackermann.
- Prefix/sums: tries for strings, Fenwick/segment trees for O(log n) range queries.

## 4-week direction
- Week 1: implement dynamic array, hash map, and BST from scratch with oracle tests; record heights and chains.
- Week 2: finish MINI_PROJECT; complete the BST-vs-AVL degeneration table from real runs.
- Week 3: adversarial week — sorted insertions, collision keys, decrease-key mixes — and fix each fallout.
- Week 4: REAL_WORLD_PROJECT review; whiteboard any structure's core invariant in 5 minutes.

## Done criteria
- State each structure's central bound plus the assumption or discipline behind it.
- Predict array-vs-list and hash-vs-tree winners for a given access mix, then verify.
- Diagnose a degeneration (tall tree, long chain, slow heap) from stats alone.

## Non-coverage
- This track does not build B-trees, lock-free structures, or persistent data structures; each is named with the scale or concurrency trigger that earns it.
- Cache-oblivious layouts are referenced, not implemented.
- Language-stdlib internals (e.g. HashMap treeification) are reading material, not lab work.

## Pitfalls
- Treating expected O(1) hashing as worst-case; adversaries and load factors exist.
- Skipping the oracle tests; structure bugs are silent data corruption.
- Ignoring constants: O(log n) with pointer chasing can lose to O(n) scans at small n.

## Adjacent tracks
- Pair with sorting/searching for the algorithm consumers and databases tracks for the on-disk structures.
- Revisit when a collection "feels slow"; stats first (height, chain, probes), then judgment.

## Weekly drills
- State one invariant per structure (heap order, AVL balance, trie prefix, Fenwick LSB) cold.
- Recompute amortized array cost via the doubling-credit argument.
- Diagnose a planted degeneration from stats alone (no source peeking).

## Anti-roadmap
- Do not use a structure whose invariant you cannot state; oracles catch what memory misses.
- Do not ignore constants at small n; measure before theorizing.
