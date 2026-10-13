# Refactoring: JMM Foundations

## Pattern 1: plain flag spin -> latch (or volatile)

Before (racy, possibly never terminates):

```java
static boolean ready; static int data;
// writer: data = 42; ready = true;
// reader: while (!ready) Thread.onSpinWait(); use(data);
```

After (guaranteed):

```java
static final CountDownLatch READY = new CountDownLatch(1);
static int data;
// writer: data = 42; READY.countDown();
// reader: READY.await(); use(data);
```

Why: the latch edge (`countDown` hb `await` return) carries the whole
graph. A volatile flag also works for one-shot publication; the latch
additionally parks instead of burning a core.

## Pattern 2: scattered publishes -> single edge point

Before: three separate plain flags for `url`, `timeout`, `ports`, each
spun on independently — three races, three wakeups, no composition.

After: one latch (or one volatile `ready` guarding all three plain
fields — safe publication through a single release). One edge, one
rendezvous, whole graph delivered. The `LatchEdge` demo is this refactor
already applied; keep new code in the after shape from the start.

## Pattern 3: volatile counter -> locked or atomic counter

Before: `static volatile long count` incremented from N threads —
ordering without atomicity, millions lost at 2M scale.

After (exactness required): the `LockEdge` shape — every increment
inside `synchronized (LOCK)`. After (throughput required): `LongAdder`
or `AtomicLong`. Rule of thumb: volatile for flags and references,
atomics/locks for read-modify-write, never the reverse.

## Pattern 4: sleep-based "visibility" -> join/future

Before: spawn worker, `Thread.sleep(100)`, read results — timing as a
correctness mechanism, broken under load or on fast machines alike.

After: `worker.join()` then read (sum 41541750 guaranteed), or submit
to an executor and `future.get()`. The lifecycle/library edge replaces
the guess with a chain; the sleep's 100 ms becomes zero added latency
in the common case (join returns the moment work completes).

## Pattern 5: lock-everything -> narrowest sufficient edge

Before: every shared read under `synchronized` — correct, contended,
slow; the lock word melts at high thread counts.

After: immutable snapshot published once through a volatile reference
or latch; readers go lock-free thereafter. Keep the monitor for
read-modify-write (the 2M chain), downgrade pure publication to a
one-shot edge. Match the edge to the shape: lifecycle for task results,
latch for startup graphs, volatile reference for re-publishable
snapshots, lock for exclusion.

## Refactoring checklist

- Name the two conflicting accesses and the edge that now orders them.
- Confirm the three links (write -> release -> acquire -> read) exist
  in program order on both sides.
- Assert exact oracles (1499500 / 41541750 / 2000000 / latch true) in
  tests, looped, not single-shot.
- Delete the sleep, the second lock instance, and the unlocked fast
  path — then re-run the checklist.
