# VISION — Advanced Trees (Deep)

Vision: pick the right ordered-structure for each workload instead of reaching for TreeMap by default.

## Mental models
- RB balances with color invariants — small rotations, few on insert.
- AVL balances with strict height — faster reads, more write churn.
- Splay bets on locality — great under skew, bad worst case.
- Treap bets on randomness — simple to code, expected bounds.
- B-tree bets on block size — wins on disk.
- Trie bets on prefix locality — prefix ops become free.

## Decision table
| Workload | Pick |
|---|---|
| General ordered map | TreeMap (RB) |
| Latency-critical reads | AVL |
| Hot-key skew | Splay |
| Competitive-programming simple | Treap |
| Disk / page cache | B+ tree |
| Prefix search / autocomplete | Trie |
| Consistent snapshots | Persistent variant (lab 20/34) |

## Career path
- Shows up in: interviews, DB internals, indexing libraries, compilers (maps for symbol tables).
- Story to tell: "I know why TreeMap is red-black, when to use a trie, and how B+ helps disk scans."

## Done when
- [ ] Explain each structure in one paragraph
- [ ] Rotate an RB insert and an AVL LR case by hand
- [ ] Mini + real-world project shipped
