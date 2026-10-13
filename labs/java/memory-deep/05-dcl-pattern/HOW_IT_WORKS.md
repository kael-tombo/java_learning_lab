# How It Works: DCL Pattern

## Step 1: the fast path (check 1)

```java
Helper h = instance;   // single volatile read
if (h == null) { ... }
```

After initialization, every call does exactly this: one volatile load,
non-null, return. No monitor, no fence beyond the load. The local `h`
pins the read so the method tests and returns the same object.

## Step 2: entering the slow path

A thread observing null contends for `synchronized (VolatileDcl.class)`.
Only threads that saw null pay the monitor; everyone else already
returned. The outer check is purely an optimization — but load-bearing
as one, since without it the idiom is just locking.

## Step 3: the recheck under lock (check 2)

```java
if ((h = instance) == null)
    h = instance = new Helper();
```

Inside the monitor, the thread re-reads. The monitor edge makes the
first thread's write visible here: if T1 already initialized, T2's
recheck sees non-null and skips construction. Without this line, T2
(which read null at check 1 long ago) initializes a second instance —
`constructions == 2`, deterministically with the 50 ms window.

## Step 4: construction and volatile publication

`new Helper()` runs (field stores plus the lab-04 freeze for its
finals), then the `volatile` write publishes. The chain: constructor
stores hb freeze hb volatile write (inside the lock) hb every later
volatile read at check 1. That edge is the pre-2004 fix: reference and
constructed state travel in order.

## Step 5: all later readers

Each subsequent check-(1) volatile read is ordered after the
publication write, so `value == 42` holds for all 16 racers across all
10k gets. Single identity (`seen.size() == 1`) plus initialized state —
both asserted, both structural.

## Step 6 (the alternatives' mechanics)

Holder: first call touches `LazyHolder`, the JVM takes the class-init
lock (JLS 12.4.2), runs `INSTANCE = new Helper()` once. Enum: class init
again, plus JVM-enforced reflection and serialization identity.
Synchronized accessor: every call takes the monitor; the monitor edges
do all the ordering at ~20 ns per call.
