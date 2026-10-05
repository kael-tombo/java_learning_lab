# FLASHCARDS — Data Structures Advanced

| # | Front | Back |
|---|---|---|
| 1 | BIT update trick? | i += i & −i |
| 2 | BIT query trick? | i -= i & −i |
| 3 | Segment tree update/query? | O(log n) |
| 4 | Segment tree space? | ~4n |
| 5 | Lazy propagation avoids? | O(k) range-add |
| 6 | Skip list expected height? | O(log n) |
| 7 | Skip level distribution? | geometric |
| 8 | JDK concurrent skip list? | ConcurrentSkipListMap |
| 9 | DSU parent path compression? | amortized α(n) |
| 10 | Union by rank prevents? | tall chains |
| 11 | Bloom FP only? | false positives only |
| 12 | Bloom k optimal? | (m/n) ln2 |
| 13 | Deletion filter variant? | counting/Cuckoo |
| 14 | Merkle internal = ? | hash(left‖right) |
| 15 | Merkle proof size? | O(log n) |
| 16 | Git uses Merkle? | yes |
| 17 | SA definition? | sorted suffix start indices |
| 18 | LCP array via Kasai? | O(n) time |
| 19 | Treap dual order? | key BST + priority heap |
| 20 | Trie ops bound? | O(L) word length |
| 21 | RB tree JDK map? | TreeMap |
| 22 | Fenwick simpler than ST? | yes for prefix sums |
| 23 | Range-add via two BIT? | difference trick |
| 24 | Bloom union = ? | bitwise OR |
| 25 | Bloom intersect = ? | bitwise AND |
| 26 | Skip list concurrent friend? | yes |
| 27 | DSU α(n) bound? | amortized per op |
| 28 | Merkle root proves? | whole-tree integrity |
| 29 | SA search O? | O(P log n) |
| 30 | Treap expected O? | O(log n) |
| 31 | ST lazy push when? | on visit to node |
| 32 | BIT memory? | O(n) |
| 33 | Skip list no rebalance? | yes |
| 34 | Bloom false positive cause? | hash collisions |
| 35 | Merkle children proof chain? | sibling hashes |
| 36 | DSU component count? | maintained |
| 37 | SA vs suffix tree memory? | SA much smaller |
| 38 | Trie prefix count? | node passthrough count |
| 39 | ST point query O? | O(log n) |
| 40 | BIT additive queries F? | prefix sum |
| 41 | Skip list level 0? | full sorted list |
| 42 | DSU rollback for? | offline connectivity |
| 43 | Bloom m bits, k hashes FPR ≈ ? | (1−e^(−kn/m))^k |
| 44 | Merkle tree arity? | typically 2 |
| 45 | SA built how? | prefix doubling O(n log² n) or O(n) algos |
| 46 | Treap split(k)? | ≤k / >k |
| 47 | ST lazy value role? | pending updates |
| 48 | BIT as binary index tree? | Fenwick tree |
| 49 | Skip list expected insert O? | O(log n) |
| 50 | DSU parent[] root stores? | size/neg rank |
| 51 | Bloom scaling? | increase m or rebuild |
| 52 | Merkle anti-tampering? | root hash signed |
| 53 | SA+LCP pattern search? | yes |
| 54 | Treap random priority? | to get O(log n) |
| 55 | ST memory vs BIT? | larger |
| 56 | ConcurrentSkipListMap ops? | O(log n) |
| 57 | DSU variants? | persistent/rollback |
| 58 | Bloom thread-safe? | no, needs sync |
| 59 | Merkle used in Bitcoin? | yes |
| 60 | When skip list vs RB? | concurrent ordered map |
