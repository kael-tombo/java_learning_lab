# VISION — Ropes (31)

Vision: make string concat/split/insert O(log n) by storing a binary tree of small leaves.

## Mental models
- Leaves hold flat char arrays (cap ~ e.g. 64–1024 chars); internal nodes store left-subtree weight (length).
- Concat = new parent node; index walks weights down the tree.
- Split descends and stitches two halves; rebalancing like AVL/Fibonacci weights.
- Iteration is in-order leaf traversal; avoid O(n) per-char lookups → cursor/iterator with cached path.
- Use vs StringBuilder famed: Boehm ropes in GCC's ext std::rope.

## Decision table
| Need | Use |
|---|---|
| Append-mostly buffer | StringBuilder |
| Heavy concat/split/edit in middle | Rope |
| Immutable small strings | String |
| Persistent text editing buffer | Rope / piece table |
| Regex-heavy small docs | String |
| Editor buffer for large file | Rope or piece table |

## Career path
- Shows up in: editors (Xi, VS Code uses piece table — related), text engines, log viewers.
- Interview angle: concat/split bounds, balance invariant, why index can degrade without rebalance.
- Bridges to gap buffers and piece tables.

## Done when
- [ ] Concat two ropes and compute new weight by hand
- [ ] Explain why naive index is O(depth) and how cursor fixes iteration
- [ ] Mini + real-world projects shipped
