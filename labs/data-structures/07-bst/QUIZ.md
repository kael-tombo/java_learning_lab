# QUIZ — Binary Search Trees (`07-bst`)
> 15 questions. Attempt closed-book, then check answers.

## Questions
1. What is the defining access contract of BST (1 sentence)?
2. Name the backing representation(s) of `BST` and one alternative.
3. State the invariant that every mutator must preserve.
4. Give Big-O for `insert` and the assumption (amortized / expected / worst).
5. Give Big-O for `search` and when it degrades.
6. What triggers resize / rebalance / rehash, and what is its cost?
7. Empty-structure behavior: return value vs exception — what do you choose and why?
8. How do duplicates/nulls behave in your implementation?
9. Compare BST vs the closest alternative on locality and memory overhead.
10. Which Java stdlib class matches this lab, and what guarantee does its Javadoc give?
11. Sketch the worst-case input and its cost.
12. How does iteration order (or lack thereof) affect correctness of client code?
13. Name one fail-fast / concurrency pitfall and the fix.
14. What metric proves your implementation scales (benchmark design)?
15. Name one production use among: ordered maps, ranges, leaderboards, in-memory indexes and why BST fits.

## Answers (no peeking first)
1. See THEORY §1 — contract summary for BST; representation-independent behavior.
2. Reference: see `BST` skeleton in EXERCISES E1; alternative in THEORY §6.
3. THEORY §4 — e.g., size consistency + structural property (order/heap/hash/trie/bloom).
4. Expected: derive from THEORY §5 table; state amortized vs expected explicitly.
5. Same table; degradation = resize pause / collision chain / skew / heap skew / long keys.
6. Load factor / capacity-full / balance-factor / heap-size / trie fan-out; cost O(n) rebuild or O(log n) rotations.
7. `NoSuchElementException` for pop/peek/dequeue; `Optional`/null only if documented; never silent wrong value.
8. Policy must be documented + tested (EXERCISES E3); hash/BST need `equals/hashCode` or `Comparator` consistency.
9. Array=locality king; linked=splice king; hash=lookup king; tree/heap/trie=semantics king (order/priority/prefix).
10. Linked in THEORY §6 (ArrayList/LinkedList/ArrayDeque/HashMap/TreeMap/PriorityQueue/Trie/Guava BloomFilter).
11. Sorted keys (BST), collisions (hash), reverse (heap), prefix flood (trie) — see E5.
12. Hash/bloom have no order; tree/heap order is semantic; assuming order where none exists is a bug.
13. `modCount` fail-fast; `ConcurrentModificationException`; fix = copy, lock, or concurrent variant.
14. Timing table across n=1k/10k/100k with warmup; expect constant/log/linear per table.
15. Any of: ordered maps, ranges, leaderboards, in-memory indexes — justify via operation mix + complexity row.
