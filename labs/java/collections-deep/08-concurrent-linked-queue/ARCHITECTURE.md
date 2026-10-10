# Architecture: ConcurrentLinkedQueue

## Components

- `Node<E>`: `volatile E item`, `volatile Node<E> next`. No `prev` —
  removal only at head, append only at tail.
- `volatile Node<E> head` — may lag behind the first live node (dummy
  dequeued nodes accumulate ahead of it).
- `volatile Node<E> tail` — may lag behind the last node (or even behind
  head, per the source comment: "it is possible for tail to lag behind
  head (why not)?").
- `VarHandle ITEM / NEXT` — CAS primitives (`compareAndSet`, `casItem`,
  weak ordered writes for publication).

## Data flow: offer(e)

1. `requireNonNull(e)`. New node with item set (relaxed write — published
   by the later CAS on `next`).
2. Start at `tail` (snapshot `t`), walk `p.next` until `q == null`.
3. `NEXT.compareAndSet(p, null, newNode)` — **the** linearization point.
   Losers (q != null) advance and retry; winners optionally `casTail`
   if `p != t` (slack-2: only hop when two behind).
4. Never blocks; contention resolves by retry, not waiting.

## Data flow: poll()

1. `restartFromHead` loop from `head`: skip null-item nodes (dead), skip
   self-linked nodes (`p == q` → restart).
2. On a live item: `p.casItem(item, null)` — **the** linearization point.
   Exactly one racing poll wins per node.
3. Optionally swing `head` forward (slack-2 again), self-link the old head
   (`next = self`) for GC unlink.

## Boundaries

- No blocking ops (`take()` doesn't exist — see `LinkedBlockingQueue`).
- `size()` walks O(n); `isEmpty()` probes to first live item. Neither is
  stable under mutation — don't branch hot paths on them.
