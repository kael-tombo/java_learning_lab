# Internals: Thread Lifecycle

## Primary sources (read these, not blogs)
- `java.base/java/lang/Thread.java` (State enum, start/join/sleep), HotSpot `thread.cpp`/`osthread`, `jstack`/`jcmd Thread.print` output
- `java.lang.Thread`, `java.lang.Object` (wait/notify), `java.util.concurrent.locks.LockSupport`
- `java.util.concurrent.atomic.*`, `java.lang.invoke.VarHandle` specifications

## What the source shows
1. **Data structures:** `java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token.
2. **Entry points:** `start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()`.
3. **Memory effects** are specified in JLS 17.4 / VarHandle javadoc; the machine code is fences or `lock`-prefixed instructions selected by the JIT per platform.

## How to verify locally (JDK 17+)
```
javap -c -p YourClass.class     # look for monitorenter/monitorexit, volatile AccessFlags, Unsafe/VarHandle calls
jstack <pid>                    # Thread.State tokens + 'waiting to lock' / 'parking' lines
jcmd <pid> Thread.print         # same as jstack via diagnostic command
java -XX:+PrintFieldLayout -version  # field layout when reasoning about padding/contention
```

## Lab-specific source notes
- BLOCKED = synchronized-monitor contention only; ReentrantLock contention shows as WAITING (parking); RUNNABLE covers running+ready; getState() is monitoring-only; start() is single-use (second call throws IllegalThreadStateException); virtual threads report the same six states but synchronized pins the carrier through JDK 23 (JEP 444).

## Implementation details that are safe to rely on
1. Only the specified semantics (JLS/VarHandle/javadoc contracts), never the machine code shape.
2. Lock levels, inflation/deflation, cell growth, and fence selection are adaptive — semantics stay fixed while tactics change.
3. Thread-state tokens and stack-trace parentheticals (`on object monitor`, `parking`, `sleeping`) are the stable diagnostic surface.

## What not to do
- Do not branch application logic on `getState()` output or fuzzy sums; both are observations, not synchronization.
- Do not depend on timing, fairness, or scheduling order; none is specified.
