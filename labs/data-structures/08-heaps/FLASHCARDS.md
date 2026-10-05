# FLASHCARDS — Heaps (Advanced Use) (`08-heaps)
> ~60 recall rows. Cover left column, recite, flip.

| Prompt | Answer | Cue / use-case | Pitfall |
|---|---|---|---|
| Array get(i) | O(1) | random access by index | off-by-one; bounds check |
| Array push-back amortized | amortized O(1) | doubling; total copy ≤2n | forget to copy; leak ref |
| Array insert middle | O(n) | shift right | System.arraycopy range bug |
| Linked prepend | O(1) | head splice | lose head ref |
| Linked append with tail | O(1) | tail splice | stale tail on empty |
| Linked reverse | O(n) | 3-pointer | cycle or lost next |
| Cycle detection (Floyd) | O(n) time O(1) space | tortoise+hare | null deref |
| Stack push/pop | O(1) | top pointer | underflow check |
| Queue enqueue/dequeue (ring) | O(1) amortized | head/tail mod cap | full vs empty disambiguation |
| Deque ops | O(1) | ArrayDeque ring | iterator order confusion |
| Hash put/get expected | expected O(1) | good hash + α<0.75 | bad hashCode; flooding |
| Hash resize/rehash | O(n) amortized | double + rehash all | rehash with old mask |
| BST search | O(h) | order invariant | degenerate O(n) if sorted |
| BST delete | O(h) | 3 cases: leaf/1/2 children | successor splice bug |
| Heap peek | O(1) | root of array heap | empty check |
| Heap push/pop | O(log n) | sift up/down, h=floor(log2 n) | pick wrong child |
| Heapify | O(n) | bottom-up sift | naive O(n log n) push loop |
| Trie insert/search | O(L) | one edge per char | missing terminal flag |
| Trie prefix count | O(P+subtree) | DFS from prefix node | blowup on wildcard |
| Bloom add/check | O(k) | k hashes set/test bits | deletion unsupported (classic) |
| Bloom FPR | (1-e^(-kn/m))^k | size m,k from target p | undersize m |
| Load factor α | n/m | resize when α>threshold | integer-division bug |
| Amortized doubling | Σ 2^i < 2n | geometric series | linear-growth trap O(n²) |
| Tree height balanced | h=O(log n) | branching halves n | assert balance factor |
| Tree height skewed | h=O(n) | sorted insert | needs rotation |
| BFS | O(V+E) | queue frontier | visited-set omission |
| DFS | O(V+E) | stack/recursion | stack overflow; revisit |
| Dijkstra | O((V+E) log V) | heap + decrease-key | negative weights invalid |
| Topo sort | O(V+E) | Kahn/DFS | cycle detection first |
| When to use ArrayList | read-heavy, index access |  | iteration invalidation |
| When to use LinkedList | splice-heavy with handles |  | cache-miss heavy |
| When to use HashMap | point lookup, dedup |  | needs good hashCode/equals |
| When to use TreeMap | ordered/range queries |  | O(log n) not O(1) |
| When to use PriorityQueue | top-K, scheduling |  | no efficient contains/decrease-key |
| When to use Trie | prefix/autocomplete |  | memory fan-out |
| When to use Bloom | pre-check, huge n, FPR ok |  | never for authoritative answer |
| Fail-fast iterator | throw on concurrent mod | modCount check | forget modCount++ |
| equals/hashCode contract | equal ⇒ same hash | final fields | mutable keys |
| Comparator consistency | compare==0 ⇔ equals (for Tree) | document policy | ClassCastException |
| Resize copy | Arrays.copyOf / arraycopy | double cap | off-by-one; stale slots |
| Open addressing tombstone | mark deleted, skip on search | probe continues | table fills with tombstones |
| BST successor | min of right subtree | splice carefully | parent pointer fix |
| AVL balance factor | -1..1 | rotations restore | forgot height update |
| Heap parent/child idx | parent=(i-1)/2; kids 2i+1,2i+2 | 0-based array | 1-based formula bug |
| Trie compress (radix) | merge single-child chains | saves nodes | complex delete |
| Counting bloom | counter per cell to allow delete | +space | counter overflow |
| JMH vs nanoTime | JMH for rigor; nanoTime+warmup ok here |  | no warmup; GC noise |
| Space: array vs linked | array: slack; linked: ptrs+alloc |  | GC pressure |
| Locality | contiguous ⇒ prefetch wins |  | pointer-chase stalls |
| Hash flooding fix | randomized hashing (Murmur/Hashing) | seed per table | deterministic weak hash |
| Interview one-liner: arrays | O(1) index, O(n) middle insert | use when asked tradeoffs |  |
| Interview one-liner: hash | expected O(1), resize O(n) amortized | needs good hashCode/equals |  |
| Interview one-liner: BST | O(h); balanced O(log n) | sorted insert degrades |  |
| Interview one-liner: heap | peek O(1), push/pop O(log n) | scheduling, top-K |  |
| Interview one-liner: trie | O(L) per word, shared prefixes | autocomplete, routing |  |
| Interview one-liner: bloom | O(k), FPR tunable, no deletes | pre-check only, never source of truth |  |
| Invariant recall: size | size == reachable count | assert after every mutator | drift ⇒ resize/iterator bugs |
| Invariant recall: heap shape | complete tree + order | array embedding, h=floor(log2 n) | shape holds but order broken |
| Sizing rule: hash | keep α≤0.75, double + rehash | growth plan in design doc | linear growth O(n²) total |
| Sizing rule: bloom | m=−n ln p/(ln2)², k=(m/n)ln2 | compute before allocating bits | undersized m ⇒ FPR blowup |

## How to use
- Daily: 15 cards, shuffle. Retire only after 3 clean recalls.
- Link each miss back to THEORY § / CODE_DEEP_DIVE §.
- Add 5 personal cards from bugs you actually hit in EXERCISES.
