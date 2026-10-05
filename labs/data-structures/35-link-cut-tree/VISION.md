# VISION — Link-Cut Trees (35)

Vision: answer connectivity queries on a dynamic forest in amortized O(log n) per op.

## Mental models
- The forest is represented by preferred-path splays: the path root→node lives in one splay.
- Access(v) moves v's path into a single splay and re-roots; link/cut splice preferred paths.
- Evert(v) re-roots the tree at v using lazy reverse flags on splay nodes.
- Every op is one access plus O(1) splays; amortized O(log n).
- Lazy propagation (reverse) mirrors splay-tree reversal.

## Decision table
| Need | Use |
|---|---|
| Dynamic connectivity in a forest | Link-cut tree |
| Path aggregates on trees | HLD / LCT |
| Offline connectivity | DSU + rollback |
| Static tree path queries | HLD / sparse tables |
| Simple graph BFS connectivity | DSU |
| Heavy link-cut debugging | Euler tour tree |

## Career path
- Shows up in: competitive programming, research algorithms, some network sims.
- Interview angle: access/splay interplay; why amortized O(log n) suffices in practice.
- Ties to splay trees, HLD, and Euler-tour trees.

## Done when
- [ ] Trace access(v) on a 5-node path
- [ ] Distinguish link/cut/evert invariants
- [ ] Mini + real-world projects shipped
