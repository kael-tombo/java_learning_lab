# THEORY — Queues (FIFO) & Deques (`04-queues`)
> Operations · invariants · representation · complexity. Java-focused.

## 1. Mental model (5 min)
Think of queues as a contract: **state + invariants + operations**.
Representation options: array-backed (cache-friendly, resize cost),
node/pointer-based (O(1) splice, pointer overhead), hash-indexed (expected O(1),
hash quality matters), tree-structured (logarithmic balance if invariant holds).
This lab's reference type is `ArrayQueue`.

## 2. Vocabulary
- **Capacity vs size:** allocated slots vs logical elements.
- **Load factor α = n/m** (hash tables): drives resize + probe length.
- **Height h:** longest root→leaf path; balanced ⇒ h = O(log n).
- **Amortized cost:** average over a sequence (e.g., doubling array push).
- **Stable / ordered:** whether iteration order is defined (BST, LinkedHashMap).

## 3. Core operations (what you must implement)
| Operation | Contract / postcondition | Typical approach in `ArrayQueue` |
| `enqueue` | _see table_ | _see notes_ |
| `dequeue` | _see table_ | _see notes_ |
| `peek` | _see table_ | _see notes_ |
| `circular-enqueue` | _see table_ | _see notes_ |
| `resize-ring` | _see table_ | _see notes_ |
| `deque-push-front/back` | _see table_ | _see notes_ |
| `sliding-window-max` | _see table_ | _see notes_ |
| `level-order` | _see table_ | _see notes_ |

Detailed semantics:
1. **Create / clear** — establish empty invariant (size=0, structure-specific null/zero state).
2. **Insert / add** — preserve invariant; trigger rebalance / resize / rehash if threshold crossed.
3. **Lookup / contains** — follow index / links / hash / BST property / heap order / trie edges.
4. **Delete** — splice or mark (tombstone for open addressing; BST 3-case delete; trie prune).
5. **Traverse / iterate** — fail-fast iterator; document order guarantees (or lack thereof).
6. **Resize / rebalance** — double capacity or rotate; rehash all keys; re-heapify.

## 4. Invariants (assert these in code)
- Size field equals reachable element count; `0 <= size <= capacity`.
- Structural invariant holds after every mutator:
  - arrays: `elements[0..size)` non-null logical window; rest ignored.
  - linked: no cycle (unless circular by design); head/tail consistent.
  - hash: `bucket(hash(k))` contains k if present; `α < threshold`.
  - BST: left < node < right (per comparator); height balance factor bounded (AVL ±1).
  - heap: parent ≤ children (min-heap); complete-tree shape (array `2i+1/2i+2`).
  - trie: every word corresponds to root→terminal path; shared prefixes share nodes.
  - bloom: bits only set (never cleared in classic variant); FPR formula governs sizing.
- Iterator `modCount` matches; concurrent mutation throws `ConcurrentModificationException`.

## 5. Complexity table (memorize + derive)
| Operation | Array-backed | Linked | Hash | Tree / Heap / Trie* |
|---|---|---|---|---|
| access / search | O(1) index / O(n) search | O(n) | expected O(1), worst O(n) | O(log n) balanced; O(h) degenerate; trie O(L) |
| insert (end / anywhere) | amortized O(1) end; O(n) middle | O(1) with handle; O(n) search | expected O(1) amortized w/ resize | O(log n); heap O(log n); trie O(L) |
| delete | O(n) shift (unordered: O(1) swap) | O(1) with handle | expected O(1) | O(log n); trie O(L) |
| min / max / peek | O(n) unsorted | O(n) | O(n) | heap O(1) peek; BST O(log n); trie prefix O(P+L) |
| space | O(n) + slack | O(n) + 2 ptrs/elem | O(n+m) buckets | O(n); trie O(alphabet × nodes) worst |
| traverse | O(n) contiguous (fast) | O(n) pointer-chase | O(n+m) | O(n) |

\* Pick the column matching `queues`; other columns are for choosing alternatives.

## 6. Representation tradeoffs
- **Array:** best locality, random access, SIMD-friendly; pays shift + copy on insert/resize.
- **Linked nodes:** O(1) splice, stable iterators/handles; poor cache, extra allocation/GC.
- **Hash:** fastest point lookup; no order (unless tree/linked variant), hash-DoS risk, resize pauses.
- **Tree/heap/trie:** order / priority / prefix semantics; balance or sizing math required.
- Java mapping: `ArrayList` vs `LinkedList`, `ArrayDeque`, `HashMap`, `TreeMap`, `PriorityQueue`, custom `Trie`, Guava `BloomFilter`.

## 7. Correctness sketches
- Array doubling: geometric growth ⇒ total copy cost ≤ 2n ⇒ amortized O(1) per append (see MATH_FOUNDATION.md).
- BST search: each step discards a subtree by order invariant ⇒ O(h) comparisons.
- Heap sift: complete tree height ⌊log₂n⌋ ⇒ at most h swaps ⇒ O(log n).
- Trie lookup: one edge per character ⇒ O(L) independent of n.

## 8. When NOT to use queues
- Need ordering but picked hash; need O(1) point lookup but picked tree.
- Tiny n where simplicity beats asymptotics; huge n where memory/IO dominates (B-trees, SSTables).
- Adversarial keys (hash flooding) without randomized hashing.

## 9. Checklist before exercises
- [ ] Can draw memory layout for 0/1/many elements.
- [ ] Can state invariant in one sentence.
- [ ] Can fill the complexity row for `ArrayQueue` from memory.
- [ ] Know Java stdlib counterpart and its documented guarantees.
