# FLASHCARDS — Advanced Trees

| # | Front | Back |
|---|---|---|
| 1 | RB tree height bound? | ≤ 2 log(n+1) |
| 2 | AVL height bound? | ~1.44 log n |
| 3 | Splay worst case per op? | O(n) |
| 4 | Splay amortized? | O(log n) |
| 5 | Treap expected ops? | O(log n) |
| 6 | B-tree optimizes? | block transfers |
| 7 | TreeMap based on? | red-black tree |
| 8 | Trie op bound? | O(L) word length |
| 9 | RB insert rotations max? | 2 |
| 10 | AVL rotation types? | LL, RR, LR, RL |
| 11 | Splay steps? | zig, zig-zig, zig-zag |
| 12 | Treap heap key? | random priority |
| 13 | B+ data stored where? | leaves (linked) |
| 14 | Compressed trie name? | radix tree |
| 15 | RB recolor path length? | O(log n) |
| 16 | AVL stricter than RB? | yes |
| 17 | RB vs RB delete simpler? | insert |
| 18 | TreeMap comparator source? | natural or explicit |
| 19 | Trie node children? | HashMap/array |
| 20 | Prefix count trick? | node counters |
| 21 | B-tree fanout choice? | block size |
| 22 | Splay potential fn? | sum of log sizes |
| 23 | Treap split result? | two treaps |
| 24 | RB color of root? | black |
| 25 | Red node children color? | black |
| 26 | AVL balance factor set? | {-1,0,1} |
| 27 | Why treap randomized? | avoid adversarial height |
| 28 | B-tree vs B+ scan? | B+ linked leaves |
| 29 | TreeMap first/last ops? | first/lastKey O(log n) |
| 30 | Trie space worst case? | O(total chars) |
| 31 | RB height in practice? | near AVL |
| 32 | Splay good for? | skewed hot access |
| 33 | Treap erase via? | merge of children |
| 34 | B-tree insertion split? | median up |
| 35 | TreeMap subMap view? | navigable submap |
| 36 | Trie vs hash lookup? | O(L) vs O(1) avg |
| 37 | RB tree property #3? | black-height equal paths |
| 38 | AVL rotation after LL insert? | right rotate |
| 39 | Splay amortized proof tool? | potential method |
| 40 | Treap priorities duplicates? | break tie deterministically |
| 41 | B+ vs B for range queries? | B+ better |
| 42 | TreeMap tailSet view? | true navigable tailSet |
| 43 | Trie end marker? | terminal flag |
| 44 | RB insert case red parent/red uncle? | recolor, move up |
| 45 | RB insert case red parent/black uncle, triangle? | rotate parent |
| 46 | AVL delete needs? | rebalance up to root |
| 47 | Splay zig-zag case? | double rotation |
| 48 | Treap expected height? | ~2 ln n |
| 49 | B-tree min keys per node? | ceil(m/2)-1 |
| 50 | Trie supports startsWith? | yes, O(L) |
| 51 | TreeMap.values view sorted? | no, map order |
| 52 | RB delete black-height fix? | extra black bit trick |
| 53 | Why RB over AVL in JDK? | fewer rotations |
| 54 | Splay security (DoS) risk? | O(n) repeated deep |
| 55 | Treap merge precondition? | all keys(a) < all keys(b) |
| 56 | B+ internal keys role? | routing separators |
| 57 | Trie memory optimization? | compressed edge labels |
| 58 | TreeMap O(log n) ops? | put/get/remove |
| 59 | RB in Linux kernel? | rbtree for schedule |
| 60 | Which pick for disk index? | B+ tree |
