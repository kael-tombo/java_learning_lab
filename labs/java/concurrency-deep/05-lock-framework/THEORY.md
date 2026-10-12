# Lock Framework (AQS) — Theoretical Foundation

## Core Concept

`AbstractQueuedSynchronizer` (AQS) is the single engine behind
`ReentrantLock`, `Semaphore`, `CountDownLatch`, `ReentrantReadWriteLock`,
`StampedLock`'s cousins, and most of `java.util.concurrent`: an `int state`
plus a FIFO queue of waiter nodes. Subclasses define *what the state means*
(lock count, permits, latch count) via `tryAcquire`/`tryRelease`; AQS owns
*queuing, parking, and wakeup*. Learn AQS once, read every synchronizer ever.

## State + Queue: The Two Fields That Matter

```java
private volatile int state;              // subclass-defined meaning
private transient volatile Node head;    // queue head (dummy on init)
private transient volatile Node tail;    // queue tail
```

- `state` is the *only* shared mutable data (a lock count of 0/1…n, a permit
  count, a latch count). All mutation goes through CAS
  (`compareAndSetState`).
- `head`/`tail` anchor a doubly-linked CLH-variant queue of `Node`s, one per
  blocked thread. The head is always a dummy (its thread already acquired or
  is acquiring); the tail is where newcomers enqueue.

CLH lineage: the original Craig–Landin–Hagersten lock spins on a
predecessor's flag; AQS inverts it — each node parks (`LockSupport.park`)
until its *predecessor* releases and unparks it. Park-instead-of-spin is what
keeps an AQS queue cheap under contention (no cache-line spinning storm).

## The Acquire Path (exclusive, interruptible-optional)

```
tryAcquire(arg) succeeds? → done (fast path, no queue)
else → enqueue Node → loop:
         predecessor == head? → tryAcquire again (may succeed now)
         else → park (LockSupport), unless interrupted/timed-out
on wakeup → predecessor == head? tryAcquire → success: become head, unpark successor
```

Three subtleties:

1. **Barging**: a newcomer calls `tryAcquire` *before* queuing. If the lock
   just released, the newcomer can steal it from the queued head — higher
   throughput (no context switch to the waiter), unbounded unfairness
   (starvation legal). This is the documented nonfair default.
2. **Cancellation**: interrupt/timeout unlinks the node (`CANCELLED` status)
   and the queue self-heals — successors re-link to a live predecessor
   (`cleanQueue`). Cancel storms don't corrupt the queue, they just churn it.
3. **Head never holds application state**: after acquiring, the thread sets
   itself as head and its old node becomes garbage. `head` is a *position
   marker*, and `getFirstQueuedThread()`-style introspection walks from it.

## Fair vs Nonfair (ReentrantLock source-verified, JDK 23)

```java
// NonfairSync: first attempt is UNGUARDED — barges even with a queue
if (compareAndSetState(0, 1)) { setExclusiveOwnerThread(current); return true; }

// FairSync: acquires only if reentrant or queue is EMPTY
if (c == 0) {
    if (!hasQueuedThreads() && compareAndSetState(0, 1)) { ... }
}
```

- Nonfair: higher throughput, possible starvation. Default for a reason —
  the barging thread is already running (hot caches, no unpark latency).
- Fair: FIFO-ish ordering (`hasQueuedThreads` check), measurably slower in
  microbenchmarks (extra queue check + unpark latency on the handoff), still
  not *strictly* FIFO (a releaser can re-barge between `unlock` and the
  successor's wakeup — "fair" means no *overt* barging, not a hard queue
  discipline).
- Reentrancy in both: owner re-entry just `setState(c+1)` (overflow checked:
  `Maximum lock count exceeded` past 2³¹−1).

## Node Status Bits (JDK 23 — the scheme changed!)

Older JDKs used `waitStatus` with `SIGNAL = -1, CONDITION = -2, PROPAGATE =
-3, CANCELLED = 1`. JDK 23's rewritten AQS uses a `status` int with **bitwise
Unsafe ops** (`getAndBitwiseAndInt`) and new constants:

```java
static final int WAITING   = 1;            // must be 1
static final int COND      = 2;            // in a condition wait
static final int CANCELLED = 0x80000000;   // must be negative
```

(Verified in `AbstractQueuedSynchronizer.java` from the JDK 23 sources.)
Any guide quoting SIGNAL/PROPAGATE describes the pre-rewrite internals —
the *protocol* (predecessor signals successor, cancelled nodes unlink) is
unchanged; only the encoding moved. State this carefully in reviews: the
algorithm is stable, the bit layout is not API.

## ConditionObject: AQS's Wait-Set

`ConditionObject` (`lock.newCondition()`) moves a node from the sync queue
to a *condition queue* on `await()`, fully releasing `state` (reentrancy
depth saved and restored), and back on `signal()`:

- `await()` = enqueue-on-condition + release-all + park; wakeup =
  re-enqueue-on-sync + re-acquire (may BLOCK behind others — signal hands
  off *eligibility*, not the lock).
- `signal()` moves the *longest-waiting* condition node to the sync queue;
  `signalAll()` moves all. Same while-loop discipline as `Object.wait`
  (spurious wakeups allowed by spec).
- `awaitUninterruptibly`, `awaitNanos`, `awaitUntil` mirror the `Object`
  variants with nanosecond precision and deadline semantics.

One lock, many conditions = the fix for the "single wait-set" limitation of
`synchronized` (lab 02): producer/consumer pairs get separate `notFull`/
`notEmpty` queues (exactly how `ArrayBlockingQueue` is built).

## Shared Mode: Semaphores, Latches, ReadWriteLocks

Exclusive mode (`lock()`) grants one owner; shared mode (`acquireShared`)
grants while `tryAcquireShared` returns non-negative:

- `Semaphore(5)`: state = permits; acquire decrements, release increments;
  multiple holders coexist; `release()` can *increase* beyond the initial
  count (permits are not capped — a bug source when releases outnumber
  acquires).
- `CountDownLatch(n)`: state = count; `await` blocks until 0; **one-shot**
  (no reset — that's `CyclicBarrier`/`Phaser`, lab 09).
- `ReentrantReadWriteLock`: state packs *two* counters (high 16 bits reader
  count, low 16 exclusive count — 65 535 max each; overflow past that throws).
  Read-hold + write-request = deadlock by design (lock *downgrading*
  write→read is safe; *upgrading* read→write deadlocks).

## AQS vs synchronized (when to reach for the framework)

Same table shape as lab 02, one level deeper: AQS adds timeouts
(`tryLock(t)`), interruption (`lockInterruptibly`), fairness choice,
multiple conditions, and shared-mode primitives — at the cost of explicit
`unlock` in `finally` (no block structure to save you) and weaker JIT
transparency (library calls vs bytecodes; lock elision doesn't apply).

## Key Invariants

1. `state` transitions only via CAS (or under exclusive hold for reentrancy
   bumps); queue links only via CAS/volatile writes.
2. Head is always a dummy; a thread becomes head exactly when it acquires.
3. Cancelled nodes unlink without breaking the chain (successors skip to
   live predecessors).
4. `signal` transfers queue membership, never lock ownership — re-acquisition
   still races.
5. Fair mode checks queue emptiness before CAS; nonfair barges first and
   asks never.
