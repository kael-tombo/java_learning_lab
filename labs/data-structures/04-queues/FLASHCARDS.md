# Flashcards — Queue Data Structure (Circular Queue)

- Q: Circular queue operations & time? → A: enQueue/deQueue/Front/Rear/isEmpty/isFull all O(1)
- Q: Circular vs linear queue? → A: Circular wraps around, no shifting; linear wastes space or shifts
- Q: Empty vs full ambiguity? → A: Both have head == tail
- Q: Two solutions for empty/full? → A: 1) Waste one slot 2) Track size variable
- Q: Head/tail/size meaning? → A: head=front index, tail=next insert slot, size=element count
- Q: ArrayDeque vs LinkedList for queue? → A: ArrayDeque: circular array, cache-friendly, no node allocation
- Q: ArrayDeque amortized time? → A: O(1) — resize doubles capacity, <2n total copies
- Q: Linked list circular queue? → A: Head/tail node pointers, no capacity limit, more memory per element
- Q: Circular queue vs Deque? → A: Circular queue: fixed capacity, FIFO only. Deque: both ends, dynamic
- Q: Why modulo for wrap? → A: (index + 1) % capacity implements circular behavior without branches
- Q: Queue FIFO principle? → A: First In, First Out — first enqueued, first dequeued
- Q: Queue use cases? → A: BFS, task scheduling, buffering, rate limiting, print spooler
- Q: Circular queue Rear() formula? → A: (tail - 1 + capacity) % capacity
- Q: When to use circular queue over ArrayDeque? → A: Fixed capacity required, memory-constrained, embedded systems
- Q: ArrayDeque internal structure? → A: Circular array with head/tail pointers, doubles on resize