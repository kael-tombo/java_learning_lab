# VISION — Treaps (33)

Vision: BST ordered by key, heap-ordered by random priority; expected O(log n) everything.

## Mental models
- Each node carries a random priority; the tree must be a BST on keys AND a max-heap on priorities.
- This "two orders" view makes rotations deterministic: whatever keeps both orders is correct.
- Split(t, k) into (≤k, >k) and Merge(a,b) let you build all other ops (insert/erase/join) in a few lines.
- Randomization replaces explicit balancing; expected height ~ 2 ln n.
- Deterministic expected bounds that survive adversarial key orders.

## Decision table
| Need | Use |
|---|---|
| Simple randomized BST | Treap |
| Guaranteed height bounds | AVL/Red-black |
| Persistent/functional ops | Treap with path copying |
| Ordered map with range ops | Treap with split/merge |
| Cache-friendliness | B-tree |
| Simplicity for interviews | Treap |

## Career path
- Shows up in: randomized structures, competitive programming, some editor maps.
- Interview angle: split/merge formulation; expected-height argument.
- Gateway to implicit treaps (rope alternative) and persistent variants.

## Done when
- [ ] Insert/erase via split/merge by hand
- [ ] Derive expected height from random priorities
- [ ] Mini + real-world projects shipped
