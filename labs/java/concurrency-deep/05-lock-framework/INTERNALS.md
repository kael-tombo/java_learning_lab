# AQS Internals

## Node layout (JDK 23)

Each queue node holds: a `status` int, predecessor/successor links, the
waiting `Thread`, and (for shared mode) a next-waiter marker. The queue is a
doubly-linked CLH variant: newcomers CAS-append at `tail`; the `head` is a
dummy whose thread has already acquired.

## Status bits (JDK 23, source-verified)

```java
static final int WAITING   = 1;            // successor must be unparked
static final int COND      = 2;            // node sits in a condition queue
static final int CANCELLED = 0x80000000;   // node dead, must be unlinked
```

Mutations use bitwise Unsafe ops (`getAndBitwiseAndInt`,
`getAndBitwiseOrInt`), not plain volatile writes. Older guides quote
`SIGNAL = -1, CONDITION = -2, PROPAGATE = -3`: that describes the pre-rewrite
encoding. The protocol (predecessor unparks successor; cancelled nodes are
skipped) is unchanged — only the bit layout moved.

## Enqueue (`addWaiter` shape)

1. Read `tail`; set `node.prev = tail`.
2. CAS `tail` to `node`; on failure retry (another thread appended first).
3. Link old tail's `next` to `node`. A failed `next`-link is repaired by
   successors scanning backward from `tail` — `prev` links are authoritative.

## Cancellation (`cleanQueue` shape)

Interrupt or timeout marks the node `CANCELLED` and unparks its successor.
Successors whose predecessor is cancelled scan backward to the nearest live
node and re-link. Cancel storms churn the queue but never corrupt it — each
repair is a bounded backward walk.

## Acquisition loop (`acquireQueued` shape)

```text
node = addWaiter(EXCLUSIVE)
interrupted = false
loop:
  p = node.predecessor()
  if p == head and tryAcquire(arg): setHead(node); p.next = null; return interrupted
  if shouldParkAfterAcquire(p, node) and parkAndCheckInterrupt(): interrupted = true
```

`shouldPark` sets the predecessor's `WAITING` bit so release knows whom to
unpark; the double-check (`p == head` retry before parking) closes the
lost-wakeup race.

## Release (`release` shape)

`tryRelease` (state decrement, owner clear at 0) then: if head's status has
`WAITING`, unpark the successor. No ownership transfer — the successor must
still win its `tryAcquire` retry against bargers.

## Condition internals

`await()`: `addConditionWaiter` appends to the condition queue, `release`
drops `state` fully (saving depth), park. `signal()`: `transferForSignal`
moves the first condition node to the sync tail (CAS-ing `COND` off, `WAITING`
handling on). Spurious wakeups survive by spec — hence the `while` loop.
