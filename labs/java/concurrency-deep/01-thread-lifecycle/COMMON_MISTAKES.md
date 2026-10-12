# Common Mistakes: Thread Lifecycle

## 1. Branching on getState()
```java
// WRONG: races the shutter
if (t.getState() == Thread.State.WAITING) t.interrupt();
// RIGHT: use join/latch/future to coordinate; getState only for dashboards/dumps
done.await(); // or t.join();
```

## 2. Calling start() twice (including after termination)
```java
t.start(); t.join(); t.start(); // THROWS IllegalThreadStateException — start is single-use
// RIGHT: create a new Thread (or submit to an executor) for the next run
```

## 3. Reading BLOCKED as "any lock contention"
BLOCKED means a `synchronized` monitor only. ReentrantLock queues park -> WAITING. Hunting the wrong subsystem wastes the incident. Read the parenthetical.

## 4. Interrupting a synchronized-entry wait
Interrupts do nothing to BLOCKED threads. A thread stuck entering `synchronized` ignores interrupt; `ReentrantLock.lockInterruptibly()` exists for exactly this need.

## 5. Assuming RUNNABLE means executing
A descheduled thread and a spinning thread are both RUNNABLE. CPU starvation hides inside RUNNABLE — confirm with OS CPU metrics and stack samples, not the state word.

## 6. Treating TIMED_WAITING expiry as a signal
`sleep(t)/wait(t)/join(t)` wake with no event on timeout. Code that assumes "woke => notified" mis-handles spurious/timeout wakes; always re-check the condition.

## 7. Daemon threads holding must-finish work
The JVM abandons daemon threads mid-execution at exit. Anything that must complete runs non-daemon with explicit shutdown/join, or a shutdown hook.

## Review checklist
- Operands named (which thread/monitor/field/atomic)? Edges identified (MATH_FOUNDATION.md)?
- Every acquisition paired with release on all paths (exceptions, interrupts, timeouts)?
- No monitoring signal used as a control signal?
