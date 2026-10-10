# Lab 06 — PriorityQueue (Binary Min-Heap in `Object[]`)

`java.util.PriorityQueue<E>` is an unbounded min-heap: element 0 of the
backing `Object[] queue` is always the minimum. Parent of index `k` is
`(k - 1) >>> 1`; children are `2k+1`, `2k+2`. There are no nodes.

Core facts this lab drills:

- `offer` sifts up, `poll` moves the last slot to the root then sifts down.
  Both O(log n). `peek` is O(1) (`queue[0]`).
- Bulk `addAll` heapifies from `(n >>> 1) - 1` in O(n) (Floyd build-heap).
- Fresh queue eagerly allocates `Object[11]` (`DEFAULT_INITIAL_CAPACITY`).
  Growth is `oldCap + 2` below capacity 64, then 50% (`oldCap >> 1`).
- `offer(null)` always throws NPE. Iteration yields heap order, never sorted
  order — drain with `poll()` for sorted output.
- Unsynchronized; fail-fast iterators via `modCount` (incremented on every
  `offer`). Thread-safe sibling: `PriorityBlockingQueue`.

Files: `THEORY.md` (invariants, costs), `CODE_DEEP_DIVE.md` (5 runnable
snippets incl. reflection-measured growth 11 → 24 → 50 → 102 → 153).
The other 21 docs in this directory expand one angle each — all consistent
with those two.
## File map

- `HOW_IT_WORKS.md` — siftUp/siftDown traces on a 7-element heap.
- `INTERNALS.md` — source map of `PriorityQueue.java` (fields, `removeAt`).
- `MATH_FOUNDATION.md` — index arithmetic, heapify O(n) sum, growth series.
- `PERFORMANCE.md` — op-cost table and the `contains`-needs-a-`HashSet` rule.
- `STEP_BY_STEP.md` — hand-built heap: offers 5,3,8,1 then a poll.
- `DEBUGGING.md` — heap-invariant assert, comparator and stale-priority bugs.
- `EXERCISES.md` — reflection growth probe, top-k, Dijkstra lazy deletion.
- `QUIZ.md` / `FLASHCARDS.md` — parent(0), growth kink, `removeAt` branches.

## Running the snippets

`CODE_DEEP_DIVE.md` programs run with plain `java HeapNotSorted.java`
(single-file launch, JDK 11+). Only the growth probe needs
`--add-opens java.base/java.util=ALL-UNNAMED` for the `queue`-field read.
