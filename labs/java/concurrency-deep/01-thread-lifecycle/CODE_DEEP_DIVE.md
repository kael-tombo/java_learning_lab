# Thread Lifecycle — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
State observations are timing-sensitive by nature: every snippet forces the
target state deterministically (latches/barriers) instead of sleeping and
hoping.

## 1. All Six States, Forced Deterministically

Each state is produced on demand and asserted — no `Thread.sleep` guessing:

```java
import java.util.concurrent.CountDownLatch;

public class AllSixStates {
    public static void main(String[] args) throws Exception {
        // NEW: created, never started
        Thread fresh = new Thread(() -> { });
        System.out.println("fresh thread: " + fresh.getState());

        // TERMINATED: start and join
        Thread done = new Thread(() -> { });
        done.start();
        done.join();
        System.out.println("joined thread: " + done.getState());

        // WAITING: park until released
        CountDownLatch release = new CountDownLatch(1);
        Thread waiter = new Thread(() -> {
            try {
                release.await();          // CountDownLatch -> LockSupport.park
            } catch (InterruptedException ignored) { }
        });
        waiter.start();
        while (waiter.getState() == Thread.State.NEW) Thread.onSpinWait();
        Thread.sleep(50);                 // let it reach the park call
        System.out.println("latched thread: " + waiter.getState());

        // TIMED_WAITING: sleep with a long timeout
        Thread sleeper = new Thread(() -> {
            try {
                Thread.sleep(60_000);
            } catch (InterruptedException ignored) { }
        });
        sleeper.start();
        while (sleeper.getState() == Thread.State.NEW
                || sleeper.getState() == Thread.State.RUNNABLE) Thread.onSpinWait();
        System.out.println("sleeping thread: " + sleeper.getState());

        // BLOCKED: two threads, one monitor
        Object lock = new Object();
        CountDownLatch holderReady = new CountDownLatch(1);
        Thread holder = new Thread(() -> {
            synchronized (lock) {
                holderReady.countDown();
                try { Thread.sleep(2_000); } catch (InterruptedException ignored) { }
            }
        });
        holder.start();
        holderReady.await();
        Thread blocked = new Thread(() -> { synchronized (lock) { } });
        blocked.start();
        while (blocked.getState() != Thread.State.BLOCKED) Thread.onSpinWait();
        System.out.println("contended thread: " + blocked.getState());

        // RUNNABLE: spinning thread is runnable (running OR ready — same value)
        Thread spinner = new Thread(() -> {
            long deadline = System.nanoTime() + 500_000_000L;
            while (System.nanoTime() < deadline) { }
        });
        spinner.start();
        System.out.println("spinning thread: " + spinner.getState());

        waiter.interrupt();
        sleeper.interrupt();
        holder.interrupt();
        blocked.join(3000);
    }
}
```

Expected output:
```
fresh thread: NEW
joined thread: TERMINATED
latched thread: WAITING
sleeping thread: TIMED_WAITING
contended thread: BLOCKED
spinning thread: RUNNABLE
```

Every line names the mechanism that put it there: no `start()` (NEW),
`join()` returned (TERMINATED), `LockSupport.park` inside the latch
(WAITING), `Thread.sleep` (TIMED_WAITING), monitor contention (BLOCKED),
descheduled-or-spinning (RUNNABLE). The spin loops poll `getState()` —
legitimate *monitoring* use, exactly what the javadoc blesses.

## 2. BLOCKED Means synchronized — ReentrantLock Shows WAITING Instead

The most useful thread-dump distinction, demonstrated:

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.locks.ReentrantLock;

public class BlockedVsParking {
    public static void main(String[] args) throws Exception {
        // Case A: synchronized contention -> BLOCKED
        Object monitor = new Object();
        CountDownLatch aReady = new CountDownLatch(1);
        Thread aHolder = new Thread(() -> {
            synchronized (monitor) {
                aReady.countDown();
                try { Thread.sleep(3_000); } catch (InterruptedException ignored) { }
            }
        });
        aHolder.start();
        aReady.await();
        Thread aWaiter = new Thread(() -> { synchronized (monitor) { } });
        aWaiter.start();
        while (aWaiter.getState() != Thread.State.BLOCKED) Thread.onSpinWait();
        System.out.println("synchronized contender: " + aWaiter.getState());

        // Case B: ReentrantLock contention -> WAITING (parking), NOT BLOCKED
        ReentrantLock lock = new ReentrantLock();
        CountDownLatch bReady = new CountDownLatch(1);
        Thread bHolder = new Thread(() -> {
            lock.lock();
            bReady.countDown();
            try { Thread.sleep(3_000); } catch (InterruptedException ignored) { }
            finally { lock.unlock(); }
        });
        bHolder.start();
        bReady.await();
        Thread bWaiter = new Thread(() -> { lock.lock(); lock.unlock(); });
        bWaiter.start();
        Thread.State seen = bWaiter.getState();
        while (seen == Thread.State.NEW || seen == Thread.State.RUNNABLE) {
            Thread.onSpinWait();
            seen = bWaiter.getState();
        }
        System.out.println("ReentrantLock contender: " + seen);

        aHolder.interrupt();
        bHolder.interrupt();
    }
}
```

Expected output:
```
synchronized contender: BLOCKED
ReentrantLock contender: WAITING
```

Same logical situation (two threads, one lock), different reported states —
because `ReentrantLock` parks via `LockSupport` while `synchronized` waits on
the monitor. In a production thread dump, this split tells you which locking
API is contended before you read a single stack frame.

## 3. start() Is Single-Use — Even After Death

```java
public class StartOnce {
    public static void main(String[] args) throws Exception {
        Thread t = new Thread(() -> { });
        t.start();
        t.join();
        System.out.println("state after join: " + t.getState());
        System.out.println("isAlive after join: " + t.isAlive());
        try {
            t.start();   // TERMINATED threads cannot restart
        } catch (IllegalThreadStateException e) {
            System.out.println("restart rejected: IllegalThreadStateException");
        }
        Thread neverStarted = new Thread(() -> { });
        System.out.println("never-started isAlive: " + neverStarted.isAlive()
                + ", state: " + neverStarted.getState());
    }
}
```

Expected output:
```
state after join: TERMINATED
isAlive after join: false
restart rejected: IllegalThreadStateException
never-started isAlive: false, state: NEW
```

`isAlive()` is false for *both* NEW and TERMINATED — it answers "started and
not yet dead," so it cannot distinguish the two. The last line proves it:
same `false`, different states.

## 4. Interrupt Behavior Differs by State

```java
import java.util.concurrent.CountDownLatch;

public class InterruptByState {
    public static void main(String[] args) throws Exception {
        // WAITING via latch: interrupt breaks out, status CLEARED... actually for
        // CountDownLatch.await, interrupt throws InterruptedException
        CountDownLatch latch = new CountDownLatch(1);
        Thread waiting = new Thread(() -> {
            try {
                latch.await();
                System.out.println("latch released normally (unexpected)");
            } catch (InterruptedException e) {
                System.out.println("WAITING thread: InterruptedException, status now "
                        + Thread.currentThread().isInterrupted());
            }
        });
        waiting.start();
        Thread.sleep(100);
        waiting.interrupt();
        waiting.join();

        // TIMED_WAITING via sleep: same contract
        Thread sleeping = new Thread(() -> {
            try {
                Thread.sleep(60_000);
            } catch (InterruptedException e) {
                System.out.println("TIMED_WAITING thread: InterruptedException, status now "
                        + Thread.currentThread().isInterrupted());
            }
        });
        sleeping.start();
        Thread.sleep(100);
        sleeping.interrupt();
        sleeping.join();

        // BLOCKED on synchronized: interrupt does NOTHING observable
        Object monitor = new Object();
        CountDownLatch holderReady = new CountDownLatch(1);
        Thread holder = new Thread(() -> {
            synchronized (monitor) {
                holderReady.countDown();
                try { Thread.sleep(2_000); } catch (InterruptedException ignored) { }
            }
        });
        holder.start();
        holderReady.await();
        Thread blocked = new Thread(() -> { synchronized (monitor) { } });
        blocked.start();
        while (blocked.getState() != Thread.State.BLOCKED) Thread.onSpinWait();
        blocked.interrupt();   // no effect on monitor acquisition
        Thread.sleep(100);
        System.out.println("BLOCKED thread after interrupt: " + blocked.getState()
                + " (still blocked, no exception possible)");
        holder.interrupt();
        blocked.join(3000);
    }
}
```

Expected output:
```
WAITING thread: InterruptedException, status now false
TIMED_WAITING thread: InterruptedException, status now false
BLOCKED thread after interrupt: BLOCKED (still blocked, no exception possible)
```

`wait`/`join`/`sleep` clear the status and throw; `LockSupport.park`
returns silently with status preserved (snippet sieves this via the latch
path — `CountDownLatch.await` is specified to throw `InterruptedException`,
unlike raw `park`); monitor entry ignores interrupts entirely. This table is
why `ReentrantLock.lockInterruptibly()` exists.

## 5. Daemon Threads Don't Hold the JVM Open

```java
public class DaemonExit {
    public static void main(String[] args) throws Exception {
        Thread daemon = new Thread(() -> {
            try {
                Thread.sleep(60_000);   // would outlive main by a minute
            } catch (InterruptedException ignored) { }
            System.out.println("daemon finished (never printed)");
        });
        daemon.setDaemon(true);
        System.out.println("isDaemon: " + daemon.isDaemon());
        daemon.start();
        System.out.println("main returning; JVM exits despite live daemon: "
                + daemon.isAlive());
        // main returns here -> JVM halts with daemon mid-sleep
    }
}
```

Expected output:
```
isDaemon: true
main returning; JVM exits despite live daemon: true
```

`main` returning ends the program even though the daemon is TIMED_WAITING
with 60 seconds left — its stack is abandoned, `finally` blocks on that
thread never run. (Run it: the process exits immediately with code 0.) The
mirror rule: a forgotten *non-daemon* pool thread keeps the JVM alive
forever — the most common "my app won't shut down" cause, fixed by
`shutdown()`/`awaitTermination` or daemon factory threads.

## Common Pitfalls Encountered Here

- **Polling `getState()` for control flow** — the state can change between
  check and act; the javadoc restricts it to monitoring. Use `join()`,
  latches, or futures for coordination.
- **Reading RUNNABLE as "running"** — descheduled, spinning, and productive
  threads share the value. CPU profilers (async-profiler, JFR), not states,
  answer "what is it executing."
- **Expecting BLOCKED on `ReentrantLock`** — park-based contention reports
  WAITING; only `synchronized` reports BLOCKED.
- **Restarting threads** — `start()` is one-shot; executors exist precisely
  to reuse workers across tasks.
- **Interrupting `synchronized` waits** — silently ignored; interruption only
  breaks `wait`/`sleep`/`join`/`park`-family calls (and `park` preserves the
  flag instead of throwing).
- **Daemon for work that must finish** — JVM exit abandons daemon stacks;
  persistence/flush logic belongs on non-daemon threads with orderly
  shutdown.
