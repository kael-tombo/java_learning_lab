# Internals: Synchronized Internals

## Primary sources (read these, not blogs)
- `javap -c` (monitorenter + 2 monitorexit), HotSpot `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, JLS 17.1/17.4
- `java.lang.Thread`, `java.lang.Object` (wait/notify), `java.util.concurrent.locks.LockSupport`
- `java.util.concurrent.atomic.*`, `java.lang.invoke.VarHandle` specifications

## What the source shows
1. **Data structures:** object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit`.
2. **Entry points:** `synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout`.
3. **Memory effects** are specified in JLS 17.4 / VarHandle javadoc; the machine code is fences or `lock`-prefixed instructions selected by the JIT per platform.

## How to verify locally (JDK 17+)
```
javap -c -p YourClass.class     # look for monitorenter/monitorexit, volatile AccessFlags, Unsafe/VarHandle calls
jstack <pid>                    # Thread.State tokens + 'waiting to lock' / 'parking' lines
jcmd <pid> Thread.print         # same as jstack via diagnostic command
java -XX:+PrintFieldLayout -version  # field layout when reasoning about padding/contention
```

## Lab-specific source notes
- Biased locking disabled by default in JDK 15 (JEP 374), removed in JDK 18, flag unrecognized on JDK 23; uncontended stack-locking fast path costs on the order of ~10-20ns; wait/notify require monitor ownership (else IllegalMonitorStateException) with while-loop re-check; static (Class-object) and instance (this) monitors are disjoint; monitors are reentrant per thread; unlock->lock is a happens-before edge.

## Implementation details that are safe to rely on
1. Only the specified semantics (JLS/VarHandle/javadoc contracts), never the machine code shape.
2. Lock levels, inflation/deflation, cell growth, and fence selection are adaptive — semantics stay fixed while tactics change.
3. Thread-state tokens and stack-trace parentheticals (`on object monitor`, `parking`, `sleeping`) are the stable diagnostic surface.

## What not to do
- Do not branch application logic on `getState()` output or fuzzy sums; both are observations, not synchronization.
- Do not depend on timing, fairness, or scheduling order; none is specified.
