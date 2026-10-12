# Exercises: Thread Lifecycle

## 1. Print every state (15 min)
Write `States.java`: create a thread, print NEW; start it, print RUNNABLE; `join(50)` a sleeping thread, print TIMED_WAITING; block two threads on one `synchronized` guard, print BLOCKED from the loser; `wait()` one thread, print WAITING; join to end, print TERMINATED. APIs: `getState/start/sleep/synchronized/Object.wait/join`.

## 2. Prove BLOCKED != parked (20 min)
Park thread A on `ReentrantLock.lock()` held by B, and thread C on `synchronized` held by D. Dump with `jstack`: A must show `WAITING (parking)`, C must show `BLOCKED (on object monitor)`. Explain the subsystem split in two sentences.

## 3. Interrupt matrix (20 min)
Interrupt one thread in each of: `sleep`, `Object.wait`, `LockSupport.park`, `synchronized`-entry. Record: InterruptedException + cleared status (first two), silent return + preserved status (park), no effect (BLOCKED). Restore status where required.

## 4. start() single-use proof (10 min)
Start, join, then start again; catch and print `IllegalThreadStateException`. Replace with an executor resubmission achieving the "run twice" goal legally.

## 5. Virtual-thread dump reading (21+, 20 min)
Launch 1,000 virtual threads parked on a latch; `jcmd Thread.print` and count WAITING lines. Repeat with 1,000 platform threads to feel the footprint difference; note where `synchronized` would pin carriers.

## Submission checklist
- [ ] Each task ran on your JVM with output pasted. [ ] Predictions written before runs. [ ] One deliberate break-and-fix per lab recorded.

## 6. Daemon vs non-daemon exit (15 min)
Task: start one daemon thread sleeping 60s and one non-daemon thread awaiting a 3s latch; record wall-clock process exit.
Check: first run exits near 3s with the daemon line never printing; then make both daemon and watch the process exit immediately.
APIs: `setDaemon/isDaemon/isAlive`; success = you can state which thread held the JVM open and why.

## 7. Dump-diff drill (20 min)
Task: block 4 threads on one `synchronized` guard while 2 threads park on a held `ReentrantLock`; capture two `jstack` dumps 5s apart.
Check: label every thread `BLOCKED (on object monitor)` vs `WAITING (parking)`, name the monitor holder by `<0x...>` address, and mark each thread stuck vs progressing.
APIs: `jstack`, `synchronized`, `ReentrantLock.lock`; success = holder address traced identically in both dumps.

## 8. isAlive blind spot (10 min)
Task: print `isAlive()` plus `getState()` for a never-started thread and for a started-then-joined thread.
Check: both report `isAlive() == false` while states read NEW vs TERMINATED; write the two-line guard (`getState() == NEW` vs `== TERMINATED`) that distinguishes them.
APIs: `isAlive/getState/join`; success = the guard stated without hedging, plus the restart attempt rejected with `IllegalThreadStateException`.

## Submission additions
- [ ] Dump excerpts pasted with BLOCKED vs parking tokens labeled per thread.
- [ ] Interrupt-status values recorded after every wake (cleared vs preserved).
- [ ] Virtual-thread counts (21+) reported separately from platform-thread counts.
- [ ] The single-use `start()` rejection captured verbatim (`IllegalThreadStateException`).
- [ ] Predictions-vs-runs table filled for at least the dump-diff and interrupt tasks.
