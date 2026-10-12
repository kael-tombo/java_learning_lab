# Quiz: Thread Lifecycle

1. **Name the six Thread.State values and the one-line meaning of each.**
   A: NEW (never started), RUNNABLE (JVM-unblocked; may still wait for CPU), BLOCKED (waits a synchronized monitor), WAITING (wait/join/park, event-only wake), TIMED_WAITING (sleep/wait(t)/join(t)/parkNanos + timeout wake), TERMINATED (finished, sink).

2. **Thread A waits on a ReentrantLock held by B. BLOCKED or WAITING? Why?**
   A: WAITING (parking) — BLOCKED is synchronized-monitor contention only; lock-framework contention parks via LockSupport.

3. **What does RUNNABLE guarantee about execution?**
   A: Nothing — spinning, descheduled, and productive threads are all RUNNABLE. It reports JVM posture, not OS dispatch.

4. **Why must application logic never branch on getState()?**
   A: The javadoc restricts it to monitoring; the state can change between check and act, so branching is a race by construction. Coordinate with join/latch/future.

5. **What happens on a second start(), even after termination?**
   A: IllegalThreadStateException — start() performs NEW->RUNNABLE exactly once per Thread object.

6. **How do interrupts affect sleep/wait vs park vs synchronized-entry?**
   A: sleep/wait throw InterruptedException and clear status; park returns silently preserving status; synchronized-entry (BLOCKED/RUNNABLE) shows no observable effect.

7. **When does the JVM exit relative to daemon threads?**
   A: When all non-daemon threads terminate; daemon threads are abandoned mid-execution. setDaemon(true) must precede start().

8. **A virtual-thread dump shows 5,000 WAITING threads. Alarmed? What if BLOCKED?**
   A: WAITING thousands = normal parked backlog (carriers unmounted). BLOCKED thousands = carriers pinned (synchronized pins through JDK 23) — investigate the monitor.

## Scoring
- 7-8 correct: done. 5-6: re-read THEORY.md + INTERNALS.md. Below 5: redo STEP_BY_STEP.md before retrying.

9. **Which state does `CountDownLatch.await()` report, and what does interrupt do to it?**
   A: WAITING (parking) — the latch parks via LockSupport; interrupt throws InterruptedException out of the await.

10. **A thread returns from `Object.wait()` but stays BLOCKED for seconds. Why?**
    A: Waking and re-entering are separate events: after notify it must re-acquire the monitor, and a holder that kept the lock (or a faster rival) keeps it BLOCKED.

11. **Why are post-`join()` reads safe without volatile?**
    A: JLS 17.4 gives a thread's last action happens-before `join()` returns — joining TERMINATED is a publication edge, not just a state observation.

12. **Two dumps 5s apart show identical BLOCKED stacks on one monitor. Stuck or progressing?**
    A: Stuck (or starved): same threads on the same `<0x...>` address across the interval means no acquisition completed; moved addresses would mean progress.

13. **What does `setDaemon(true)` after `start()` do?**
    A: Throws IllegalThreadStateException — like `start()` itself, the daemon flag is set-once-before-start.

## After scoring
- For every miss, reproduce the state on demand (CODE_DEEP_DIVE.md snippet 1 forces all six) before re-answering; recall without a run does not stick.
