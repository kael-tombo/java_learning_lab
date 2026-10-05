# VISION — Cache-Oblivious Structures (30)

Vision: algorithms that are optimal for every memory level without knowing B (block) or M (cache size).

## Mental models
- Ideal-cache model: cost = number of block transfers; B, M unknown to the algorithm.
- Recursion that "shrinks" hits optimal tile size at some level automatically (van Emde Boas layout).
- k-way merging streams (funnelsort) instead of sorting in tiles.
- Blocked/tiling intuition still helps: cache-oblivious recursion subsumes tiling.
- Static layouts (vEB layout of a binary tree) approximate optimal at all depths.

## Decision table
| Need | Use |
|---|---|
| Scan-heavy static search | Arrays + binary search |
| Search with unknown B,M | vEB static layout |
| Sorting without tuning | Funnelsort |
| DB index | B-tree (cache-aware) |
| Matrix multiply | recursive blocked layout |
| Unknown hardware hierarchy | cache-oblivious |

## Career path
- Shows up in: high-performance computing, DB internals, layout research (e.g. fractal indexes).
- Interview angle: why blocking helps; amortized block-transfer analysis.
- Connects to lab 29 (vEB recursion) and T Iles: memory hierarchy reasoning.

## Done when
- [ ] Explain recursive layout drawing for depth d tree
- [ ] Compare transfers vs cache-aware in one table
- [ ] Mini + real-world projects shipped
