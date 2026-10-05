# THEORY — Queue & Stack Deep

## Stack
LIFO. Legacy `java.util.Stack extends Vector` (synchronized, legacy). Modern: `ArrayDeque` works as a stack (push/pop/peek) with no node overhead.

## Queue
FIFO. ArrayDeque (no nulls), LinkedList (OK but heavier), LinkedBlockingDeque (blocking), PriorityQueue (heap).
Semantics:
- offer/poll vs add/remove vs put/take on blocking types.
- peek returns head or null (non-blocking).

## Deque
Double-ended: add/offer to either end, poll/remove from either. ArrayDeque is the default choice.

## PriorityQueue
- Binary min-heap over `Object[] queue`; Comparator or natural ordering.
- Offer: sift-up; poll: swap root with last, sift-down; O(log n).
- Not stable for equals priorities; not a sorted stream; iterator is not priority order.
- Parallel/blocking variant: PriorityBlockingQueue (unbounded) vs LinkedBlockingQueue (FIFO).

## Amortized note
ArrayDeque ring buffer is O(1) amortized; each grow doubles capacity.

## Decision
| Workload | Pick |
|---|---|
| Stack (LIFO) | ArrayDeque |
| Queue (FIFO) | ArrayDeque |
| Bounded work queue | ArrayBlockingQueue |
| Bounded stack/queue | LinkedBlockingDeque |
| Priority dispatch | PriorityQueue |
| Multiple producers/consumers | ArrayBlockingQueue/LinkedBlockingQueue |
