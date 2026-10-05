# FLASHCARDS — Trie (Prefix Tree)

~60 cards. Format: `Term | One-line answer`. Core: A trie stores strings by sharing common prefixes: each edge is a character and each node marks end-of-word plus subtree counts.

| # | Front | Back |
|---|---|---|
| 1 | Core idea | A trie stores strings by sharing common prefixes: each edge is a character and each node marks end-of-word plus subtree counts. |
| 2 | op `insert(word)` | add a word, creating nodes as needed — O(L) |
| 3 | op `search(word)` | exact match incl. end-of-word flag — O(L) |
| 4 | op `startsWith(prefix)` | prefix existence check — O(P) |
| 5 | op `countWordsWithPrefix(p)` | subtree word count — O(P) |
| 6 | op `delete(word)` | unmark + prune dead nodes — O(L) |
| 7 | op `autocomplete(p,k)` | DFS top-k under prefix node — O(P + k*Sigma) |
| 8 | Invariant 1 | Every root-to-node path spells a prefix of some inserted key |
| 9 | Invariant 2 | endOfWord flag distinguishes 'car' from prefix of 'cart' |
| 10 | Invariant 3 | passCount/subtree counts stay consistent after insert/delete |
| 11 | Invariant 4 | alphabet mapping (array vs HashMap) is fixed per implementation |
| 12 | Hot path | insert(word) at O(L) |
| 13 | Baseline beaten | linear scan / rebuild / coarse lock |
| 14 | Java home | src/ + JUnit 5 tests |
| 15 | Debug tool | invariant checker + ASCII dump |
| 16 | Adversarial case | sorted keys / collisions / degenerate split |
| 17 | Fix | randomize / rehash / rebalance / resize |
| 18 | Memory | O(n) + auxiliary (see THEORY) |
| 19 | Use it for | search-engine autocomplete + IP longest-prefix match |
| 20 | Also used for | contact-list prefix search in a mobile app |
| 21 | Interview pitch | Prefix search, autocomplete, IP routing |
| 22 | Worst bug | stale bookkeeping |
| 23 | Prove it | hand trace n=7 |
| 24 | Complexity qualifier | best/avg/worst + amortized/expected where apt |
| 25 | Hazard | off-by-one indexing |
| 26 | Hazard 2 | overflow in aggregates |
| 27 | Hazard 3 | duplicates handling |
| 28 | Test 1 | empty |
| 29 | Test 2 | singleton |
| 30 | Test 3 | boundary |
| 31 | Test 4 | adversarial order |
| 32 | Test 5 | fuzz invariants |
| 33 | Visualize | draw nodes/intervals/registers |
| 34 | Benchmark | ns/op at 1k/10k/100k |
| 35 | Trade-off | memory vs speed |
| 36 | Trade-off 2 | static vs dynamic |
| 37 | Trade-off 3 | exact vs approximate |
| 38 | API sketch | insert(word) |
| 39 | API sketch 2 | search(word) |
| 40 | API sketch 3 | startsWith(prefix) |
| 41 | Cost placeholder | see per-op cost rows |
| 42 | Cost insert(word) | O(L) |
| 43 | Cost search(word) | O(L) |
| 44 | Cost startsWith(prefix) | O(P) |
| 45 | Cost countWordsWithPrefix(p) | O(P) |
| 46 | Cost delete(word) | O(L) |
| 47 | Cost autocomplete(p,k) | O(P + k*Sigma) |
| 48 | Review: Trie (Prefix Tree) invariant 1 | Every root-to-node path spells a prefix of some inserted key |
| 49 | Review: Trie (Prefix Tree) invariant 2 | endOfWord flag distinguishes 'car' from prefix of 'cart' |
| 50 | Review: Trie (Prefix Tree) invariant 3 | passCount/subtree counts stay consistent after insert/delete |
| 51 | Review: Trie (Prefix Tree) invariant 4 | alphabet mapping (array vs HashMap) is fixed per implementation |
| 52 | Review: Trie (Prefix Tree) invariant 5 | Every root-to-node path spells a prefix of some inserted key |
| 53 | Review: Trie (Prefix Tree) invariant 6 | endOfWord flag distinguishes 'car' from prefix of 'cart' |
| 54 | Review: Trie (Prefix Tree) invariant 7 | passCount/subtree counts stay consistent after insert/delete |
| 55 | Review: Trie (Prefix Tree) invariant 8 | alphabet mapping (array vs HashMap) is fixed per implementation |
| 56 | Review: Trie (Prefix Tree) invariant 9 | Every root-to-node path spells a prefix of some inserted key |
| 57 | Review: Trie (Prefix Tree) invariant 10 | endOfWord flag distinguishes 'car' from prefix of 'cart' |
| 58 | Review: Trie (Prefix Tree) invariant 11 | passCount/subtree counts stay consistent after insert/delete |
| 59 | Review: Trie (Prefix Tree) invariant 12 | alphabet mapping (array vs HashMap) is fixed per implementation |
| 60 | Review: Trie (Prefix Tree) invariant 13 | Every root-to-node path spells a prefix of some inserted key |

