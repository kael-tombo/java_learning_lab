# QUIZ — Heaps (Advanced Use) (`08-heaps`)
> 15 questions. Attempt closed-book, then check answers.

## Questions
1. What is the defining access contract of heaps (1 sentence)?
2. Name the backing representation(s) of `HeapApps` and one alternative.
3. State the invariant that every mutator must preserve.
4. Give Big-O for `heapify-O(n)` and the assumption (amortized / expected / worst).
5. Give Big-O for `push` and when it degrades.
6. What triggers resize / rebalance / rehash, and what is its cost?
7. Empty-structure behavior: return value vs exception — what do you choose and why?
8. How do duplicates/nulls behave in your implementation?
9. Compare heaps vs the closest alternative on locality and memory overhead.
10. Which Java stdlib class matches this lab, and what guarantee does its Javadoc give?
11. Sketch the worst-case input and its cost.
12. How does iteration order (or lack thereof) affect correctness of client code?
13. Name one fail-fast / concurrency pitfall and the fix.
14. What metric proves your implementation scales (benchmark design)?
15. Name one production use among: streaming analytics, pathfinding, job scheduling, median maintenance and why heaps fits.

## Answers (no peeking first — each maps to a THEORY section to re-read on a miss)
1. See THEORY §1 — contract summary for heaps; representation-independent behavior.
   Re-read §1 if you described implementation instead of contract.
2. Reference: see `HeapApps` skeleton in EXERCISES E1; alternative in THEORY §6.
   You should name both the reference backing and one alternative with its tradeoff.
3. THEORY §4 — e.g., size consistency + structural property (order/heap/hash/trie/bloom).
   Every mutator must re-establish it; tests should assert it (EXERCISES E3).
4. Expected: derive from THEORY §5 table; state amortized vs expected explicitly.
   If you said "O(1)" without qualification, re-read MATH_FOUNDATION §1–§2.
5. Same table; degradation = resize pause / collision chain / skew / heap skew / long keys.
   Name the concrete adversarial input (EXERCISES E5).
6. Load factor / capacity-full / balance-factor / heap-size / trie fan-out; cost O(n) rebuild or O(log n) rotations.
   Also state the threshold value (e.g., α≈0.75, AVL ±1) and why that constant.
7. `NoSuchElementException` for pop/peek/dequeue; `Optional`/null only if documented; never silent wrong value.
   Unchecked empty access is the #1 lab bug — guard + test it.
8. Policy must be documented + tested (EXERCISES E3); hash/BST need `equals/hashCode` or `Comparator` consistency.
   Inconsistent `compareTo` vs `equals` silently duplicates entries in trees.
9. Array=locality king; linked=splice king; hash=lookup king; tree/heap/trie=semantics king (order/priority/prefix).
   Cite one measurement (cache misses, alloc rate) that would confirm your pick.
10. Linked in THEORY §6 (ArrayList/LinkedList/ArrayDeque/HashMap/TreeMap/PriorityQueue/Trie/Guava BloomFilter).
    Quote the Javadoc guarantee, not folklore — note unbounded vs bounded, null policy, thread-safety.
11. Sorted keys (BST), collisions (hash), reverse (heap), prefix flood (trie) — see E5.
    Sketch the cost curve before/after the fix.
12. Hash/bloom have no order; tree/heap order is semantic; assuming order where none exists is a bug.
    `HashMap` iteration order may even change across resizes — never serialize it as a contract.
13. `modCount` fail-fast; `ConcurrentModificationException`; fix = copy, lock, or concurrent variant.
    Fail-fast is best-effort detection, not a concurrency solution.
14. Timing table across n=1k/10k/100k with warmup; expect constant/log/linear per table.
    Report median of ≥5 runs + one aux metric (resizes / height / chain / FPR).
15. Any of: streaming analytics, pathfinding, job scheduling, median maintenance — justify via operation mix + complexity row.
    A good answer names the dominant op, its frequency, and why alternatives lose.

## Scoring
- 13–15: proceed to CODE_DEEP_DIVE. 10–12: re-read the missed THEORY sections, retry in 2 days.
- <10: redo THEORY + FLASHCARDS before touching EXERCISES E4+.
