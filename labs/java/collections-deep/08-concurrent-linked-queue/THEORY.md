# ConcurrentLinkedQueue Deep Dive — Theoretical Foundation

## Core Concept

`java.util.concurrent.ConcurrentLinkedQueue<E>` is an unbounded,
**lock-free** queue built on the Michael–Scott two-list algorithm: a singly
linked chain of nodes with `head` and `tail` pointers that are *both* allowed
to lag behind reality. Every mutation is a single CAS on a volatile field —
no `synchronized`, no `ReentrantLock`, so readers and writers never block each
other.

## The Node Structure

```java
static final class Node<E> {
    volatile E item;      // set to null when dequeued
    volatile Node<E> next; // written by CAS
}
```

Two volatile fields, no `prev` — a queue only ever removes at the head and
appends at the tail, so backward links would be dead weight. Publication
protocol: a node's `item` becomes visible only after another thread CASes some
earlier node's `next` to point at it (piggy-backing on the volatile write —
the JDK uses `ITEM.set(...)` relaxed because of exactly this reasoning).

## The Two Linearization Points

These are the only two statements that define queue semantics under
concurrency:

| Operation | Linearization point | Effect |
|-----------|--------------------|--------|
| `offer(e)` | `NEXT.compareAndSet(p, null, newNode)` — appending after the current last node | element becomes queue member |
| `poll()` | `p.casItem(item, null)` — clearing the head item | element leaves the queue |

Everything else (advancing `head`/`tail`, hopping) is **optimization**, not
semantics — it may fail, lag, or be done by a different thread entirely. If you
need to reason about "was my element enqueued before X happened?", only those
two CASes matter.

## Why head/tail Are Allowed to Lag

`offer` walks to the true last node, CASes `next`, then *only sometimes* moves
`tail`:

```java
if (p != t) // hop two nodes at a time; failure is OK
    casTail(t, p);   // t's successor is now p, not p's successor
```

The rule throughout is a **slack threshold of two**: `head`/`tail` are updated
only when they appear two or more steps away from the first/last node. Fewer
CAS operations per enqueue/dequeue means less contention on the hot pointers —
and a stale `tail` is harmless because `offer` starts at `tail` and walks
forward until `p.next == null`. Correctness never depends on `head`/`tail`
being current; they are hints.

`poll` starts at `head` and may pass through a chain of already-dequeued dummy
nodes (their `item` is null and `next` still points forward) before finding a
live one. That's the cost of letting `head` lag.

## The Self-Link Reclaim Trick

When `poll` dequeues node `p` it can't unlink it from *its* predecessor
(pred's `next` may be CAS'd by others, and the dequeuer might not even hold
pred). Instead the node is made to **link to itself**:

```java
// "linking a Node that has just been dequeued to itself.
//  Such a self-link implicitly means to advance to head."
```

Detectors: `p == q` (a node whose `next` points at itself) tells any walker
"you're on garbage — restart from head." In `poll` this is the
`else if (p == q) continue restartFromHead;` branch. The self-link also breaks
the reference chain so the GC can reclaim dequeued nodes even while an old
thread still holds a reference to them — reachability here is *not* the same
as GC reachability, a point the JDK documentation makes explicitly.

## Correctness: The Michael–Scott Argument

1. **Single-consumer safety**: two threads in `poll` both CAS the *same*
   node's `item` from `item → null`; exactly one wins, so no element is ever
   returned twice, and none is skipped (null-item nodes are walked past).
2. **Single-producer safety**: `offer` CASes `p.next` from `null → newNode`;
   multiple appends racing at the old tail — exactly one wins; losers detect
   `q != null` and retry the inner loop at the new tail.
3. **No ABA problem**: nodes are never reused or unlinked-and-relinked —
   once a node's `next` leaves null it never returns to null (except via
   self-link, which points to *itself*, not null). GC allocation gives each
   CAS a unique expected value.
4. **Termination caveat**: every retry loop is bounded by progress of *some*
   thread (lock-free, not wait-free). Under extreme contention `offer`/`poll`
   can spin many times — one thread's progress guarantees system-wide
   progress, but your particular call may starve.

## Ordering Guarantees

- **FIFO** per the linearization points: an `offer` that CASes before
  another's CAS appears first in the chain; a `poll` clears the earliest
  still-live item.
- **Iterators are weakly consistent**: never throw
  `ConcurrentModificationException`, may or may not reflect concurrent
  mutations, reflect the state at some point at-or-after creation.
- **`size()` is O(n)** — walks the chain counting live items — and its value
  is stale the instant it returns (the JDK javadoc warns it is "NOT a
  constant-time operation"). `isEmpty()` is cheaper: it delegates to `first()`
  and stops at the first live item rather than counting all of them. Neither
  answer is stable under concurrent mutation; don't branch on them in hot
  paths without accepting the race.
- **No null elements**: `offer(null)` throws NPE (`Objects.requireNonNull` —
  null is the sentinel meaning "dequeued," so allowing it would corrupt the
  protocol).

## Why Not `synchronized` on a linked list?

| | CLQ (lock-free) | synchronized LinkedList queue |
|---|---|---|
| Contention | CAS retries, no thread blocked | mutex: threads queue up, context switches |
| Blocking | never (lock-free) | producer blocks while consumer holds lock and vice versa |
| Progress | system-wide (some op completes) | one holder can stall everyone (and it can die while holding) |
| Raw throughput uncontended | very high (one CAS) | also high (biased/thin locks) |
| Throughput with many cores contending | scales better | degrades — cache-line ping-pong on the lock |
| `peek`/iteration | weakly consistent | must lock or accept CME |

When you need *blocking* semantics (`take()` that waits for an element), CLQ
doesn't offer them — that's `LinkedBlockingQueue` (put/take with condition
variables) or `SynchronousQueue`/`ArrayBlockingQueue` in the same package.

## Key Invariants

1. `head != null` always (a dummy node exists even when the queue is empty).
   Both pointers only advance, never regress; but they advance independently,
   so `tail` may lag *behind* `head` (the source comments on this: "it is
   possible for tail to lag behind head (why not)?"). Invariants live on the
   chain itself — following `next` from the true last node yields null — not
   on either pointer being current.
2. Following `next` from `head` reaches every live (non-null-item) node
   exactly once, unless a node self-linked — self-linked nodes terminate the
   walk and force a restart.
3. `item == null` ⇔ node is dequeued or a dummy; a live node's item never
   returns to non-null (the state machine is one-way: `item → null`, never
   back).
4. `head`/`tail` monotonically advance (never regress) — the JDK calls this
   "merely an optimization" but it's what keeps walkers from circling.
