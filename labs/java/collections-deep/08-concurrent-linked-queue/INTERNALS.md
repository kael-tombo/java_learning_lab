# Internals: ConcurrentLinkedQueue Source Map

File: `src/java.base/share/classes/java/util/concurrent/ConcurrentLinkedQueue.java`
(OpenJDK; design credited to Doug Lea, Michael–Scott algorithm).

## Fields and handles

- `transient volatile Node<E> head, tail` — lagging hints, never authority.
- `Node`: `volatile E item; volatile Node<E> next;` CAS via
  `MethodHandles`/`VarHandle` (`ITEM`, `NEXT`).
- Invariant: `head != null` always (dummy node even when empty).

## Key methods

- `offer(E e)`: `requireNonNull`; outer `t`-snapshot loop, inner
  `p`/`q` walk; linearization `NEXT.compareAndSet(p, null, n)`; then
  `if (p != t) casTail(t, n)`.
- `poll()`: `restartFromHead` labeled loop; branches: `item != null` →
  `casItem` attempt; `p == q` → `continue restartFromHead`; else advance
  `p = q`. Head update `updateHead(head, p)` only when `p != h` (slack).
- `peek()`/`first()`: same walk, no CAS — returns first live item or null.
- `size()`: full walk counting live items — O(n), documented NOT
  constant-time. `isEmpty()`: `first() == null` — stops early.
- `iterator()`: weakly consistent; `next()` skips null-item and
  self-linked nodes; never throws CME.
- `remove(Object)` / `bulkRemove`: CAS item to null like poll (unlinking
  via self-link/head-swing happens lazily on later polls).

## The `p != t` / `p != h` pattern

Both offer and poll compare the walked-to node against the snapshot and
CAS the pointer only on mismatch-by-two. Single-step staleness is
deliberately tolerated — that tolerance is the throughput optimization.
