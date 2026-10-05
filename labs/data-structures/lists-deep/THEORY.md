# THEORY — Lists Deep

## ArrayList
Backed by `Object[] elementData` with capacity and size. Get O(1), add amortized O(1) with doubling, remove/insert O(n) due to memmove. Resize copies n/2-ish overflow each doubling. Fail-fast iterators check `modCount`.

## LinkedList
Doubly-linked nodes with a `first`/`last` pointer. Get O(n), addFirst/addLast O(1), remove by iterator O(1) once positioned. Memory overhead: each node ~24–32 bytes extra. Iterators are fail-fast too.

## Vector
Legacy: all public methods `synchronized`, grows by 2x (or capacityIncrement). Obsolete for new code; prefer ArrayList (+ explicit sync) or CopyOnWriteArrayList.

## CopyOnWriteArrayList
Every mutation copies the backing array; readers never block. Good for few-writes/many-reads.

## Advanced linked-list algorithms
- Floyd's loop detection (tortoise/hare), cycle entry.
- Reversal (iterative prev/curr/next or recursive).
- Merge two sorted lists; merge k sorted lists.
- LRU via doubly-linked list + HashMap (lab 15 concept).
- Skip list as an alternative ordered structure.

## Decision
- Most cases: ArrayList.
- Queue/deque front operations: ArrayDeque beats LinkedList.
- Many-iteration small lists: ArrayList/ArrayDeque.
- Mutations in middle under iteration: LinkedList sometimes wins but rarely enough.
