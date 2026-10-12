# How It Works: Thread Lifecycle

## The mechanism in one paragraph
Thread Lifecycle is the six `Thread.State` values and the transitions between them. The moving parts are `java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token, driven through `start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()`, implemented as described in `java.base/java/lang/Thread.java` (State enum, start/join/sleep), HotSpot `thread.cpp`/`osthread`, `jstack`/`jcmd Thread.print` output. BLOCKED = synchronized-monitor contention only; ReentrantLock contention shows as WAITING (parking); RUNNABLE covers running+ready; getState() is monitoring-only; start() is single-use (second call throws IllegalThreadStateException); virtual threads report the same six states but synchronized pins the carrier through JDK 23 (JEP 444).

## Step-by-step through the parts
1. **Name the operands.** Before reasoning, write down the exact objects/fields involved (which thread, which monitor, which field, which atomic). Most bugs are wrong-operand bugs.
2. **Trace one operation end to end.** Pick a single call from `start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()` and follow it: JDK entry -> HotSpot primitive -> observable result. Use INTERNALS.md source paths to confirm each hop.
3. **Add the second thread.** Re-trace with two actors interleaved. Ask at each step: which edge orders these two actions? If none, you have a race; say so explicitly.
4. **Check the exits.** Every acquisition has a release path (including exceptions/interrupts/timeouts). Verify yours, then compare with COMMON_MISTAKES.md.
5. **Confirm empirically.** Run the STEP_BY_STEP.md commands (`jstack`, `javap -c`, `jshell`) and match output against the predicted tokens/bytecodes.

## Worked trace
- Start from README.md item 4: BLOCKED = synchronized-monitor contention only; ReentrantLock contention shows as WAITING (parking); RUNNABLE covers running+ready; getState() is monitoring-only; start() is single-use (second call throws IllegalThreadStateException); virtual threads report the same six states but synchronized pins the carrier through JDK 23 (JEP 444).
- Reproduce it with the smallest program in STEP_BY_STEP.md, then explain each line of output using the vocabulary of `java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token.

## What people get wrong
- Skipping step 1 (reasoning about "the lock" or "the flag" without saying which object/field).
- Treating monitoring output as control input (thread states, fuzzy sums).
- Assuming edges that do not exist (different monitors, plain fields, element access through a volatile array reference).

## Next
- INTERNALS.md for source paths; MATH_FOUNDATION.md for the ordering rules in symbols.

## Second trace: the interrupt split by state
- Interrupt one parked thread (`LockSupport.park`) and one sleeping thread (`Thread.sleep`); record status after: park preserves (`Thread.interrupted()` still true), sleep clears while throwing `InterruptedException`.
- Now interrupt a thread BLOCKED on `synchronized` entry and re-dump: still BLOCKED with no exception possible — monitor entry ignores interrupts by specification.
- Repeat the park case through `CountDownLatch.await()`: it throws `InterruptedException` because the latch API converts the park return into the exception — same substrate, different contract.
- Conclusion to write down: interruption is a per-mechanism contract (throw-and-clear vs silent-preserve vs ignore), never a global stop signal.

## API-to-state map (fill from your runs)
- `start()` once: NEW -> RUNNABLE; second `start()`: `IllegalThreadStateException`, no transition at all.
- `sleep / wait(t) / join(t) / parkNanos / parkUntil`: RUNNABLE -> TIMED_WAITING; timeout expiry alone returns to RUNNABLE.
- `wait / join / park` (no timeout): RUNNABLE -> WAITING; only notify/unpark/target-death/interrupt returns to RUNNABLE.
- Contended `synchronized` entry or post-`wait()` reentry: RUNNABLE -> BLOCKED; release-plus-win returns to RUNNABLE with no fairness promise.
- `run()` returns or throws: any live state -> TERMINATED, one way; `isAlive()` reads false for NEW and TERMINATED alike.
- `setDaemon(true)` before `start()`: marks exit-irrelevant; after `start()`: `IllegalThreadStateException`.

## Where dumps mislead
- RUNNABLE-heavy dump on a saturated box: most of those threads are descheduled, not executing — reach for a CPU profiler (async-profiler, JFR `jdk.ExecutionSample`), not more dumps.
- Identical WAITING stacks at a pool's queue-take: idle capacity, not a hang — compare against task-arrival rate before "fixing" the pool size.
- A single BLOCKED thread with a fast-moving holder: transient contention, not a deadlock — diff two dumps before escalating.

## Self-check
- Cover the map above and reproduce all six lines from a live `jstack` before moving on; any line you cannot produce is a re-read of THEORY.md, not a memory failure.
