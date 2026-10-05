# THEORY — Data Structures Advanced

## Range structures
Fenwick (BIT): arr[i] holds a block sum; update/query O(log n) via i += i&−i trick; memory O(n); simpler than segment trees for additive prefix queries.
Segment tree: each node covers a range; add lazy propagation to support range-add/range-query in O(log n); memory 4n.

## Skip list
Levels of sorted linked lists; expected O(log n) search/insert/delete. Random level assignment (geometric). No rebalancing, concurrent-friendly (Doug Lea's ConcurrentSkipListMap).

## Union-find (DSU)
Parent pointers + union by rank + path compression → near-constant amortized α(n). Variants: rollback DSU (no path compression), persistent DSU.

## Bloom filter
Bit array of m bits, k hashes; insert sets bits; query ANDs bits. False positives possible, false negatives none. Optimal k = (m/n) ln 2. Can't delete; use counting/Cuckoo filters for deletion.

## Merkle tree
Binary tree of hashes; internal = hash(left||right). O(log n) proof of membership; used in Git, Bitcoin, IPFS.

## Red-black / Treap / Trie
(See advanced-trees-deep.) Ordered-map backends; treap randomized; trie for prefixes.

## Suffix array
Sorted list of all suffix start indices; with LCP array yields pattern search in O(P log n); memory-light vs suffix trees.

## Decision
| Need | Pick |
|---|---|
| Prefix sums | Fenwick |
| Range add + range sum | Segment tree w/ lazy |
| Ordered concurrent map | Skip list |
| Components | DSU |
| Fast membership w/ FP | Bloom |
| Integrity/proof | Merkle |
| Pattern search | Suffix array |
