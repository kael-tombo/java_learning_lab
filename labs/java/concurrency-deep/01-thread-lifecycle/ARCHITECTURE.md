# Architecture: Thread Lifecycle

## Components (real ones, not generic boxes)
1. **Program layer** — your code calling `start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()`.
2. **JDK layer** — `java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token.
3. **JVM/HotSpot layer** — scheduler, park/unpark primitives, monitor subsystem; sources in `java.base/java/lang/Thread.java` (State enum, start/join/sleep), HotSpot `thread.cpp`/`osthread`, `jstack`/`jcmd Thread.print` output.
4. **OS/hardware layer** — kernel threads, futexes/condition variables, cache coherence and fences.

## Structure
```
+------------------- program -------------------+
|  the six `Thread.State` values and the transitions between them                      |
+--------------- JDK (Thread Lifecycle) ----------------+
|  `java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token   |
+----------- HotSpot / OS / hardware -----------+
|  threads, monitors, fences, schedulers        |
+-----------------------------------------------+
```

## Data flow
1. Application invokes one of: `start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()`.
2. JDK maps the call onto `java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token.
3. HotSpot/OS executes the primitive (thread state change, monitor op, fence, or CAS).
4. Observable effect returns: state token, mutual exclusion, visibility edge, or updated value.

## Key invariant
- BLOCKED = synchronized-monitor contention only; ReentrantLock contention shows as WAITING (parking); RUNNABLE covers running+ready; getState() is monitoring-only; start() is single-use (second call throws IllegalThreadStateException); virtual threads report the same six states but synchronized pins the carrier through JDK 23 (JEP 444).

## Failure modes at this layer
1. Misidentifying which component owns the state (e.g. wrong monitor object, wrong field, wrong atomic).
2. Assuming ordering that no edge provides (see MATH_FOUNDATION.md for the exact edges).
3. Confusing a monitoring signal (thread state, fuzzy sum) with a synchronization guarantee.

## Cross-references
- Mechanism: HOW_IT_WORKS.md. Sources: INTERNALS.md. Costs: PERFORMANCE.md.
