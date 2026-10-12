# Flashcards: Thread Lifecycle

Q: Six Thread.State values? | A: NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED.
Q: Only cause of BLOCKED? | A: Waiting on a synchronized monitor (entry or wait-reentry).
Q: ReentrantLock contention state? | A: WAITING (parking) via LockSupport, never BLOCKED.
Q: RUNNABLE guarantee? | A: None about execution — covers running and ready-to-run.
Q: getState() sanctioned use? | A: Monitoring only (javadoc); never synchronization control.
Q: Second start()? | A: IllegalThreadStateException — single-use NEW->RUNNABLE.
Q: WAITING vs TIMED_WAITING wake? | A: Event-only vs event-or-timeout-expiry.
Q: Interrupt on park vs sleep? | A: Park: silent return, status preserved. Sleep/wait: InterruptedException, status cleared.
Q: JVM exit rule? | A: Exits when all non-daemon threads end; daemons abandoned.
Q: Virtual-thread dump with 1000s WAITING? | A: Normal parked backlog; BLOCKED 1000s = carrier pinning (synchronized through JDK 23).

## Method
- Cover the A column; recall aloud; check. Cycle missed cards twice before finishing.

## More cards (same deck)
Q: `join(t)` while waiting — which state? | A: TIMED_WAITING: wakes on target death, interrupt, or expiry.
Q: `Thread.sleep` — which state and token? | A: TIMED_WAITING (sleeping); expiry wakes with no signal.
Q: `Object.wait()` no timeout — which state? | A: WAITING (on object monitor); needs notify/notifyAll or interrupt.
Q: `Object.wait(t)` — which state? | A: TIMED_WAITING (on object monitor); notify, interrupt, or timeout returns.
Q: `CountDownLatch.await()` — which state? | A: WAITING (parking); interrupt throws InterruptedException.
Q: `Thread.join()` no timeout — which state? | A: WAITING; wakes when the target thread dies or on interrupt.
Q: `LockSupport.park()` — which state? | A: WAITING (parking); unpark or interrupt returns silently, status preserved.
Q: `LockSupport.parkNanos` — which state? | A: TIMED_WAITING (parking); unpark, interrupt, or nanos expiry returns.
Q: Re-enter synchronized after `wait()` returns? | A: BLOCKED while re-acquiring the released monitor — contends like fresh entry.
Q: `setDaemon(true)` after `start()`? | A: IllegalThreadStateException — the flag must precede start().
Q: Daemon flag inheritance rule? | A: Inherited from the creating thread — factories must set it explicitly per thread.
Q: Does `Thread.onSpinWait()` change state? | A: No — hint only; the spinner stays RUNNABLE.

## Drill
- Shuffle all 22 cards; any hesitation over 5s counts as missed.
- For every WAITING/TIMED_WAITING card, name the wake events aloud before flipping.
- For every BLOCKED card, say "synchronized monitor" before flipping.
- Re-run missed cards twice; log which parenthetical (`parking`, `sleeping`, `on object monitor`) you confuse most.
- Retire a card only after three consecutive clean recalls across two sittings.
