# VISION — Persistent Segment Trees (34)

Vision: keep every historical version of a range-query structure alive via path copying.

## Mental models
- Each update copies only the O(log n) nodes on the root-to-leaf path; new root, old root intact.
- Versions = roots; queries pin a root and walk that version only.
- "Kth smallest in range" rides on this: walk two roots built one version apart.
- Memory grows O(log n) per update; total O(q log n).
- Same trick generalizes to many BST-based structures.

## Decision table
| Need | Use |
|---|---|
| Range sum, one version | Segment/Fenwick |
| Range queries on any version | Persistent segment tree |
| Last-writer-wins timeline | Persistent structure |
| Kth smallest in subarray | Two persistent roots |
| Ordered-set per version | Persistent treap/BBST |
| Full snapshot | Copy-on-write / WAL |

## Career path
- Shows up in: competitive programming, DB MVCC analogies, immutable infra.
- Interview angle: path-copy accounting; how to answer "sum in version v"; kth-smallest-in-range.
- Ties to lab 20 (immutable persistent) and time-travel debugging.

## Done when
- [ ] Draw one update path and the shared subtrees
- [ ] Answer range sum on version v with two roots
- [ ] Mini + real-world projects shipped
