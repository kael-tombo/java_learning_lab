# Common Mistakes: JMM Foundations

## 1. Spinning on a plain flag

```java
// BROKEN: no happens-before edge at all
static boolean ready; static int data;
...
while (!ready) Thread.onSpinWait(); // may never observe the write
use(data);
```

The writer's `data = 42; ready = true` has no edge to the reader, so
the JIT may hoist `data` above the spin and the CPU may serve stale
`ready` indefinitely. Fix with `volatile`, a lock, or a latch — any one
edge orders the whole publication.

## 2. Publishing an object through a plain reference

```java
// BROKEN: reader may see a half-constructed object
config = new Config(url, timeout, ports); // plain static field
```

Object construction writes (program-ordered before the publish) reach
the reader only through an edge on the publish itself. A volatile
reference, a final-field freeze plus safe publication, a lock, or a
`countDown/await` handoff all work; a plain store guarantees nothing.

## 3. Assuming `volatile++` is atomic

```java
static volatile long count;
// 8 threads x 250000 increments -> nearly always short of 2000000
```

Volatile gives visibility and ordering, not atomicity: read-modify-write
is still three steps with a race between them. `LockEdge` gets exactly
2000000 because the monitor adds mutual exclusion *plus* the edge. For
counters use `AtomicLong` or a lock, never a volatile increment loop.

## 4. Confusing race-freedom with determinism

DRF guarantees *some* sequentially consistent interleaving explains the
output — not a *particular* one. Two correct runs of `LockEdge` both
print 2000000, but the interleaving differs every time. Asserting exact
thread order (which worker incremented when) is testing the scheduler,
not the program. Assert final state, never schedules.

## 5. Treating causality as ordering

`CausalityFloor` promises values in `[0, 100000]` and zero invented
values — while the *order* is arbitrary (stale, repeated, skipped).
Seeing only real values does not mean the code is correct; any consumer
that needs order still needs an edge. Causality is a floor, not a fix.

## 6. Hand-rolling flag protocols instead of library edges

A `CountDownLatch`, `Future.get`, queue `take`, or executor task edge is
specified, tested, and cheap. A hand-rolled `ready` flag plus `sleep`
retries is unspecified, flaky, and usually slower (spurious wakeups,
missed signals, no hb). `LatchEdge` exists to make the canonical
replacement concrete: write the graph, `countDown`, `await`, read.

## 7. Locking for visibility but mutating outside the lock

```java
synchronized (LOCK) { count++; }
// elsewhere, without the lock:
count = 0; // re-opens the race: this write has no edge to anyone
```

The monitor edge orders what happens *inside* critical sections on the
same monitor. Any access outside reintroduces an unordered conflicting
access — a data race by definition. Guard *every* access or none of the
edges apply.
