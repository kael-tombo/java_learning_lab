# Thread Lifecycle — Theoretical Foundation

## Core Concept

Every Java thread is always in exactly one of six `Thread.State` values —
`NEW`, `RUNNABLE`, `BLOCKED`, `WAITING`, `TIMED_WAITING`, `TERMINATED`. The
enum is the JVM's entire vocabulary for "what is this thread doing," and it
is deliberately coarse: it describes *why the JVM can't run the thread right
now*, not what the OS scheduler is doing with it.

## The Six States (from the JDK source)

```java
NEW          // created, not yet started
RUNNABLE     // executing in the JVM — OR waiting for the OS (e.g. CPU)
BLOCKED      // waiting for a monitor lock (synchronized entry/reentry)
WAITING      // Object.wait() / Thread.join() / LockSupport.park(), no timeout
TIMED_WAITING// Thread.sleep / wait(t) / join(t) / parkNanos / parkUntil
TERMINATED   // completed execution
```

Three facts most developers get wrong:

1. **RUNNABLE means "not blocked by the JVM," not "running."** The javadoc
   says the thread "may be waiting for other resources from the operating
   system such as processor." A thread descheduled by the OS, spinning in a
   tight loop, and executing productively are all RUNNABLE. There is no
   Java-visible distinction between running and ready-to-run.
2. **BLOCKED has exactly one cause: monitor locks.** Waiting for a
   `synchronized` block/method, or re-entering one after `Object.wait()`
   released it. Waiting on a `ReentrantLock` is *not* BLOCKED — it's WAITING
   (via `LockSupport.park`). This is the single most useful thread-dump
   reading skill: BLOCKED = someone holds a `synchronized` monitor you want.
3. **`getState()` is documented for monitoring, not control.** The javadoc:
   "designed for use in monitoring of the system state, not for
   synchronization control." Branching application logic on another thread's
   state is a race by construction — the state can change between your check
   and your act. Use `join()`, latches, futures.

## The Transition Map

```
NEW ──start()──▶ RUNNABLE ◀──notify/notifyAll/interrupt/timeout── WAITING
                  │  ▲                                          ▲
                  │  │               lock acquired               │
                  ▼  │                 │                         │
               BLOCKED ────────────────┘                    TIMED_WAITING
                  │                                     sleep/wait(t)/join(t)/
                  │                                     parkNanos/parkUntil
                  ▼
              TERMINATED (run() returns or throws; one-way)
```

Notes on the arrows:

- `start()` works exactly once; a second call throws
  `IllegalThreadStateException` even after termination. NEW → RUNNABLE is the
  only transition `start()` performs.
- `WAITING → RUNNABLE` needs an *event* (notify, unpark, joined thread
  dying, interrupt). `TIMED_WAITING → RUNNABLE` additionally fires on
  *timeout expiry* — the thread wakes with no signal at all.
- `BLOCKED → RUNNABLE` fires when the monitor is released *and* this thread
  wins the acquisition — there is no fairness guarantee; a thread can starve
  in BLOCKED indefinitely under contention.
- `TERMINATED` is a sink. `isAlive()` returns false for both NEW and
  TERMINATED (it reports "started but not yet died"), so `isAlive()` alone
  can't distinguish them — pair with `getState()`.

## Interrupts Interact with Every Waiting State

- `WAITING`/`TIMED_WAITING` on `wait`/`join`/`sleep`: interrupt clears the
  interrupt status and throws `InterruptedException`.
- `LockSupport.park()`: interrupt *returns silently* and *preserves* the
  status (`Thread.interrupted()` still true). Park-based code (locks,
  queues) must poll the status itself.
- `BLOCKED` and `RUNNABLE`: interrupts do nothing observable — a thread
  stuck entering `synchronized` cannot be interrupted out of it (one reason
  `ReentrantLock.lockInterruptibly()` exists).

## Daemon vs Non-Daemon: What Actually Ends the JVM

The JVM exits when all *non-daemon* threads terminate — daemon threads are
abandoned mid-execution, no finally blocks run for the kill itself (frames
are just dropped). `setDaemon(true)` must precede `start()`; the flag is
inherited from the creating thread. Practical rule: thread pools that should
not hold the JVM open use daemon threads (or `awaitTermination` + explicit
`shutdown`); anything that must finish uses non-daemon plus a shutdown hook.

## Virtual Threads and the Same Six States (Java 21+, JEP 444)

Virtual threads report the same `Thread.State` values — a parked virtual
thread shows WAITING/TIMED_WAITING just like a platform thread. The
difference is underneath: a blocked virtual thread *unmounts* its carrier,
freeing the OS thread for other virtual threads, while a blocked platform
thread pins its kernel thread. Consequences for lifecycle reasoning:

- Thread dumps of virtual-thread systems show thousands of WAITING threads
  as a *normal* steady state (one per pending task), not as a symptom.
- `synchronized` blocks *pin* the virtual thread to its carrier (JEP 444
  limitation through at least JDK 23, being lifted progressively) — so
  BLOCKED virtual threads still cost a carrier thread each.
- `Thread.sleep` on a virtual thread parks without consuming a carrier;
  `TIMED_WAITING` at million-thread scale is cheap.

## Reading a Thread Dump

`jstack <pid>` / `jcmd Thread.print` prints every thread as
`"name" #id prio=... tid=... nid=... state` plus a stack trace. The state
token maps directly to the enum:

- `java.lang.Thread.State: BLOCKED (on object monitor)` — find the
  `- waiting to lock <0x...>` line for the contested monitor, then who holds
  it (`- locked <0x...>`). Deadlock detection (`Found one Java-level
  deadlock`) is the JVM doing this graph analysis for you.
- `WAITING (parking)` — LockSupport-based (locks, queues, `CompletableFuture`
  internals); normal in pooled systems.
- `WAITING (on object monitor)` — `Object.wait()` without timeout; check for
  a matching notify path or it waits forever.
- `TIMED_WAITING (sleeping)` vs `(parking)` vs `(on object monitor)` — the
  parenthetical tells you which API put it there.
- Hundreds of threads in identical stacks at a lock = contention; identical
  stacks at a queue-take = healthy pool idling. The stack, not the state,
  is the diagnosis.

## Key Invariants

1. Exactly one state at a time; transitions only along the map above.
2. `start()` is single-use (NEW → RUNNABLE, then `IllegalThreadStateException`
   forever).
3. BLOCKED ⟺ monitor contention, nothing else. Lock-framework contention
   shows as WAITING (parking).
4. `getState()` reflects a sampling instant — never synchronize on it.
5. TERMINATED is final; daemon status decides whether the JVM waits for it.
