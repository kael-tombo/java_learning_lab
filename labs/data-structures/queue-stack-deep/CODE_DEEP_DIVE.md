# CODE_DEEP_DIVE — Queue & Stack Deep

## ArrayDeque internals
- `Object[] elements` with `head`, `tail` indices.
- `addLast`: `elements[tail] = e; tail = (tail + 1) & (elements.length - 1);`
- Grow when head == tail? It doubles before that (when `size == elements.length`).
- No nulls: `Objects.requireNonNull`.

## Stack vs ArrayDeque
- `java.util.Stack extends Vector` with `synchronized` — every call locks; use `ArrayDeque` for free-running LIFO.

## PriorityQueue internals
- `Object[] queue`; size; `comparator`.
- siftUp/siftDown with implicit indexing.
- `poll` swaps last to root, nulls last, then siftDown.
- `remove(o)` is O(n) linear scan.

## BlockingQueue
- `ArrayBlockingQueue`: fixed capacity, one ReentrantLock + two Conditions.
- `LinkedBlockingQueue`: optional capacity, separate put/take locks.
- `put` on full → awaits `notFull`; `take` on empty → awaits `notEmpty`.

## Weakly consistent iterators
Blocking queues provide weakly consistent iterators; ArrayDeque/PriorityQueue/LinkedList throw CME.

## Custom comparator tips
- Always tiebreak with a sequence number for stable FIFO within priorities.
- Beware `compare(a,b) == 0` for both (a,b) and (b,a) — Comparator contract.

## Iterators over a PriorityQueue
Use `poll` in a loop if you need priority order; the iterator gives no such guarantee.
