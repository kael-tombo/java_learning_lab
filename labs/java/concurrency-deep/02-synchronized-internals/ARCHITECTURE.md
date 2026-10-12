# Architecture: Synchronized Internals

## Components (real ones, not generic boxes)
1. **Program layer** — your code calling `synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout`.
2. **JDK layer** — object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit`.
3. **JVM/HotSpot layer** — scheduler, park/unpark primitives, monitor subsystem; sources in `javap -c` (monitorenter + 2 monitorexit), HotSpot `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, JLS 17.1/17.4.
4. **OS/hardware layer** — kernel threads, futexes/condition variables, cache coherence and fences.

## Structure
```
+------------------- program -------------------+
|  object monitors: monitorenter/monitorexit pairing, lock levels, and wait/notify protocol                      |
+--------------- JDK (Synchronized Internals) ----------------+
|  object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit`   |
+----------- HotSpot / OS / hardware -----------+
|  threads, monitors, fences, schedulers        |
+-----------------------------------------------+
```

## Data flow
1. Application invokes one of: `synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout`.
2. JDK maps the call onto object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit`.
3. HotSpot/OS executes the primitive (thread state change, monitor op, fence, or CAS).
4. Observable effect returns: state token, mutual exclusion, visibility edge, or updated value.

## Key invariant
- Biased locking disabled by default in JDK 15 (JEP 374), removed in JDK 18, flag unrecognized on JDK 23; uncontended stack-locking fast path costs on the order of ~10-20ns; wait/notify require monitor ownership (else IllegalMonitorStateException) with while-loop re-check; static (Class-object) and instance (this) monitors are disjoint; monitors are reentrant per thread; unlock->lock is a happens-before edge.

## Failure modes at this layer
1. Misidentifying which component owns the state (e.g. wrong monitor object, wrong field, wrong atomic).
2. Assuming ordering that no edge provides (see MATH_FOUNDATION.md for the exact edges).
3. Confusing a monitoring signal (thread state, fuzzy sum) with a synchronization guarantee.

## Cross-references
- Mechanism: HOW_IT_WORKS.md. Sources: INTERNALS.md. Costs: PERFORMANCE.md.
