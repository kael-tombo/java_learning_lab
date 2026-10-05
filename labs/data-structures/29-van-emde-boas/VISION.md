# VISION — van Emde Boas Trees (29)

Vision: get predecessor/successor on a bounded universe u in O(log log u).

## Mental models
- Universe u split into √u clusters, each itself a vEB of size √u (recursive divide by √u).
- A cluster-of-clusters summary tells which clusters are non-empty.
- min/max cached directly; find walks at most one cluster plus the summary.
- Insert/delete recurse into one cluster + maybe the summary → O(log log u).
- Space O(u) classic; use hashing/indirection for sparse universes (y-fast).

## Decision table
| Need | Use |
|---|---|
| Predecessor on small bounded universe | vEB tree |
| Sparse universe | y-fast trie |
| Range/min queries, arbitrary keys | Segment tree / Fenwick |
| Dynamic ordered set, general | Balanced BST / skip list |
| Static sorted, cache-friendly | van Emde Boas layout (lab 30) |

## Career path
- Shows up in: network flow scheduling, CS research (MST via Fredman-Willard ideas).
- Interview angle: recursion depth log log u, √u recursion, summary role.
- Bridges to cache-oblivious layouts (lab 30) and stringology labs.

## Done when
- [ ] Draw √u recursion for u=16 and locate 7's leaf
- [ ] Derive T(u)=T(√u)+O(1)=O(log log u)
- [ ] Mini + real-world projects shipped with benchmarks
