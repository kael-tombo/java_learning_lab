# THEORY — Thread Deadlock Analysis (Incident Mechanics)

## 1. Incident in One Paragraph
A deadlock freezes a subset of threads forever: thread A holds lock L1 waiting for L2 while B holds L2 waiting for L1. No CPU burn, no crash — just threads that never return. In production this surfaces as hanging requests, exhausted Tomcat/Jetty pools, and rising latency while CPU stays eerily idle.

## 2. Mechanics
### 2.1 Coffman conditions
Mutual exclusion + hold-and-wait + no preemption + circular wait. Break any one (lock ordering breaks circular wait) and deadlock is impossible.

### 2.2 Lock types in Java
`synchronized` monitors, `ReentrantLock`, `ReadWriteLock`, plus implicit locks (connection pool semaphore, `ForkJoinPool` join). Deadlocks often span layers: thread holds DB connection while waiting for a lock held by a thread waiting for a connection (pool-induced deadlock).

### 2.3 Lock-ordering bugs
Method `transfer(a,b)` synchronizing on `a` then `b` deadlocks when another thread calls `transfer(b,a)`. Fix: global order (e.g., by `System.identityHashCode`).

### 2.4 Livelock / starvation cousins
Livelock: threads keep retrying and colliding (CAS storms). Starvation: low-priority or reader-blocked threads never scheduled. Same triage, different thread-dump shape.

### 2.5 Cascading effect
10 deadlocked worker threads in a 200-thread pool looks fine — until traffic fills the rest. Then pool exhausts, queue explodes, health checks time out, orchestrator restarts healthy-but-stuck pods.

## 3. Detection Signals
| Signal | Tool | Pattern |
|---|---|---|
| `Found one Java-level deadlock` | `jstack`, `jcmd Thread.print` | explicit deadlock section |
| BLOCKED threads rising | metrics (`jvm_threads_states`), thread dumps 30s apart | same stack stuck across dumps |
| Pool active ≈ max, queue growing, CPU flat | Tomcat/Jetty/Hikari metrics | classic deadlock signature |
| Request latency p99 → timeout, throughput → 0 for subset | APM traces | threads parked on `Object.wait` / `LockSupport.park` |
| `jstack` lock chains | fastthread.io, manual `waiting to lock <0x...>` | cycle A→B→A |

## 4. Alerts
- `jvm_threads_deadlocked > 0` → page immediately.
- Pool utilization >90% for 10m + queue depth rising → warn.
- p99 > SLO with CPU flat → suspect deadlock/starvation, capture dumps.

## 5. Triage Lifecycle
1. Capture 3× `jstack` 30s apart (prove stuck vs slow).
2. `jcmd <pid> Thread.print` + `jstack -l` for lock owners.
3. Mitigate: restart / drain stuck pod; shed load.
4. Map cycle: which two (or more) locks in which order.
5. Fix: single lock order, timeout `tryLock`, shrink critical sections, separate pools.

## 6. Misdiagnoses
- Calling it "slow DB" — DB wait shows one waiter, not a cycle. Always check for the cycle.
- One thread dump is enough — it is not; need 2–3 to distinguish stuck from slow.
- Adding more threads fixes it — it widens the race and hides the cycle longer.

## 7. Interview Angle
Draw the lock-order graph, explain how `jstack` detects cycles, and propose `tryLock(timeout)` + ordering + lock splitting. Mention `ReentrantLock` fairness trade-offs.

## 8. Takeaway
Deadlock = flat CPU + stuck threads + cycle in dumps. Capture multiple dumps, break the cycle by ordering, defend with timeouts.
