# FLASHCARDS — Thread Deadlock Analysis

| # | Front | Back |
|---|---|---|
| 1 | Coffman conditions (4)? | Mutual exclusion, hold-and-wait, no preemption, circular wait |
| 2 | Which condition does lock ordering break? | Circular wait — all threads acquire locks in same global order |
| 3 | Deadlock CPU signature? | Flat/low CPU with stuck threads (vs high CPU = spin/infinite loop) |
| 4 | `jstack` deadlock banner? | `Found one Java-level deadlock:` followed by involved threads |
| 5 | Command for thread dump via jcmd? | `jcmd <pid> Thread.print` |
| 6 | Why 3 dumps 30s apart? | One dump can't separate stuck (same stack 3×) from slow (moving stack) |
| 7 | `waiting to lock <0x>` vs `parking`? | First = monitor contention; second = LockSupport / executor queue wait |
| 8 | BLOCKED vs WAITING? | BLOCKED = waiting for monitor entry; WAITING = Object.wait / park without timeout |
| 9 | Fix for transfer(a,b) vs transfer(b,a)? | Order locks by id: `first=min(a,b)` then sync in that order |
| 10 | `tryLock` deadlock defense? | `if(!lock.tryLock(2, SECONDS)) backoff+retry` — breaks hold-and-wait permanently |
| 11 | Pool-induced deadlock example? | Thread holds DB conn waiting for lock; lock holder waits for conn — separate pools/timeouts fix |
| 12 | Metric for deadlocked threads? | `jvm_threads_deadlocked` >0 pages |
| 13 | Livelock vs deadlock? | Livelock threads run/retry but make no progress; deadlock threads are parked forever |
| 14 | Starvation signal? | Some threads progress, low-priority ones stuck; check fairness / reader-writer bias |
| 15 | ReadWriteLock deadlock trap? | Upgrading read→write lock while another reader holds read = deadlock; use downgrade only |
| 16 | `jstack -l` extra info? | Ownable synchronizers + locked-on details beyond plain `jstack` |
| 17 | JFR thread events? | `jdk.JavaMonitorEnter`, `jdk.ThreadPark` show contention hotspots |
| 18 | async-profiler wall mode? | `./profiler.sh -e wall -d 60 -f wall.html` captures blocked/parked stacks |
| 19 | Immediate mitigation? | Drain/restart stuck pod, shed load; thread dump first if safe |
| 20 | Long-term prevention? | Lock ordering doc, `tryLock` timeouts, lock-splitting, deadlock detector test |
| 21 | Health-check trap? | Health thread sharing worker pool can deadlock — isolate probe threads |
| 22 | `synchronized` vs `ReentrantLock` for diagnosis? | ReentrantLock gives timed/tryLock + fair queues; synchronized dumps are simpler |
| 23 | How to prove cycle? | Chain `waiting to lock X held by thread-Y` back to start across dump |
| 24 | Load-test detection? | Concurrency soak + forced lock inversion test with timeout assertions |
| 25 | Postmortem key artifact? | Lock-order graph + dump excerpts + ordering fix + regression test |
| 26 | ForkJoinPool deadlock? | `join()` inside task with small parallelism — use `ManagedBlocker` or async |
| 27 | DB + lock ordering rule? | Never hold app lock across remote call; acquire conn late, release early |
| 28 | Alert thresholds? | Deadlocked>0 page; pool>90% 10m warn; p99 breach with flat CPU investigate |
| 29 | Tool to visualize dumps? | fastthread.io / IBM TDA — paste 3 dumps, compare stuck stacks |
| 30 | One-line interview answer? | Flat CPU + stuck stacks + cycle in jstack → order locks + tryLock timeout |
