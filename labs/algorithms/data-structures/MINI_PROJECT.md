# MINI_PROJECT — Data Structures Track
> One harness, eight structures: dynamic array, linked list, hash map, BST/AVL, binary heap, union-find, trie, Fenwick tree — each with an oracle test and an operation-count report.

## Inputs
- Seeded operation scripts (insert/delete/query mixes, 10k/100k ops) shared across structures where applicable.
- Adversarial scripts: sorted insertions for BST, hash-collision keys for the map, decrease-key mix for the heap.

## Build steps
1. Implement dynamic array (growth factor 2, amortized O(1)) and linked list; compare indexed-access and middle-insertion timings.
2. Implement hash map (chaining, rehash at 0.75) with probe/chain stats; verify against java.util.HashMap on 50k ops.
3. Implement BST then AVL rotations; verify sorted-insertion heights (BST degenerates, AVL stays logarithmic) with heights printed.
4. Implement binary heap with decrease-key via index map; verify against sorting on 10k extracts.
5. Implement union-find (path compression + union by rank), trie (insert/prefix-count), Fenwick (point-update/range-sum); verify each against a naive oracle.
6. Record operation counts and ms per (structure, script) with machine/JDK noted.

## Acceptance criteria
1. Every structure passes its oracle comparison (HashMap, sorting, naive array/sets) on all scripts.
2. BST-vs-AVL height table on sorted insertions shows the degeneration gap from real runs.
3. Hash stats show max chain length at load 0.75 vs 0.95 from real runs.
4. Heap extract order matches sorted order on all seeds including the decrease-key mix.
5. Union-find, trie, and Fenwick each have a dedicated oracle test file with hand-checkable small cases.
6. Write-up states each central bound (amortized array O(1), hash expected O(1), AVL O(log n), heap O(log n), union-find alpha(n), Fenwick O(log n)).

## Analysis prompts
1. Where does the linked list beat the array, and where does it lose 100x?
2. What does the AVL rotation count look like on sorted vs random insertions?
3. At what op mix does the heap index map pay for itself?

## Non-goals
- Red-black deletion internals (AVL suffices here), B-trees, lock-free structures, and persistent data structures (each named with triggers).

## Oracle baselines to reproduce
- Sorted-insertion heights: BST degenerating toward n while AVL stays near log2(n), both printed from your runs.
- Hash max-chain at 0.75 vs 0.95 load recorded; heap extracts matching sorted order on every seed.

## Stretch
- Add red-black insertion (or document precisely where AVL was chosen instead and why).
- Add a B-tree page simulation (fan-out 128) and compare range-scan cost against the BST.
