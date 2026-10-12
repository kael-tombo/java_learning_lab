# Debugging: Thread Lifecycle

## Capture
```
jstack <pid> > dump.txt
jcmd <pid> Thread.print > dump2.txt
```
For live systems add `jcmd <pid> Thread.print -l` (lock owners) and JFR `jdk.JavaMonitorEnter` events.

## Decode tokens
- `BLOCKED (on object monitor)` + `- waiting to lock <0xA>` -> find `- locked <0xA>` holder; that holder's stack is the fix location.
- `WAITING (parking)` -> LockSupport path (locks, queues, futures); normal for pooled threads, suspicious when workers should be computing.
- `WAITING (on object monitor)` -> `Object.wait()` with no timeout; demand the notify path or convert to timed wait.
- `TIMED_WAITING (sleeping|parking|on object monitor)` -> parenthetical names the API; expiry wakes with no signal.

## Triage recipe
1. Count identical stacks: hundreds BLOCKED at one frame = contention; hundreds parked at queue-take = healthy idle.
2. Check `Found one Java-level deadlock` footer first — the JVM already did the graph analysis.
3. Correlate with CPU: high CPU + RUNNABLE loops = spin; low CPU + BLOCKED/WAITING = stuck or idle.
4. For virtual threads (21+): thousands of WAITING is the normal backlog shape; BLOCKED thousands still cost carriers (pinning through JDK 23).

## Five-minute checklist
- [ ] Deadlock footer present? [ ] Which monitor/address repeats? [ ] Who holds it and what are they waiting for? [ ] Parking or monitor? [ ] Timeout/expiry assumed as signal anywhere?

## Sources
- `java.base/java/lang/Thread.java` (State enum, start/join/sleep), HotSpot `thread.cpp`/`osthread`, `jstack`/`jcmd Thread.print` output. Keep THEORY.md open; every diagnosis ends by naming the violated invariant.

## Interrupt triage
- `sleep`/`wait`/`join` hang, log shows `InterruptedException`, status cleared -> normal wake path; find who interrupted (shutdown hook vs stray cancel) before touching the catch block.
- Parked thread keeps interrupt status set yet stays parked after `interrupt()` -> park returned but the code re-parked without polling `Thread.interrupted()`; add the poll or switch to an interruptible API.
- BLOCKED thread stays BLOCKED minutes after `interrupt()` -> expected behavior, not a missed signal: monitor entry is uninterruptible, so no interrupt volume frees it; replace entry with `ReentrantLock.lockInterruptibly()` on that path.
- `WAITING (parking)` worker never wakes and no unpark appears in code search -> the permit was consumed before the park call or never sent; trace `unpark` ordering, not thread priority.

## Daemon-shutdown diagnosis
- Process lingers after `main` returns -> survivors in `jcmd <pid> Thread.print` are non-daemon by definition; daemonize them in the thread factory or add `shutdown()` plus `awaitTermination` with a timeout.
- Daemon output lines vanish at exit with no `finally` trace -> frames are dropped at JVM halt, not skipped by logic; move must-finish writes (buffer flush, audit log) to non-daemon threads joined from a shutdown hook.
- Exit-time flakiness across runs -> daemon-status inheritance: threads created by a daemon worker are daemon themselves; audit the factory chain, not just the leaf thread.

## Dump-diff technique
- Capture two dumps 5s apart (`jstack <pid>` twice into separate files): identical stacks on the same `<0x...>` monitor in both = stuck; identical stacks on moved addresses = progressing contention.
- Pair with CPU (`top -H -p <pid>` or OS equivalent): high CPU plus RUNNABLE spin frames = CPU burn; low CPU plus BLOCKED/WAITING = waiting, not working.
- For virtual threads (21+): diff carrier-thread sections against virtual-thread sections; a BLOCKED virtual thread that never moves across diffs pins its carrier for the whole interval.
