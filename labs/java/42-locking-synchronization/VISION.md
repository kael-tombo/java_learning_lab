# VISION — Locking & Synchronization Internals

## Vision Statement
**Correctness first, contention second** — understand monitors, AQS,
and lock-free atomics deeply enough to choose the cheapest primitive
that is still provably correct under the JMM.

---
## Mental Models
### 1. Monitor = Mutual Exclusion + Signalling
`synchronized` gives atomicity + visibility + wait/notify. Thin →
fat lock inflation is observable in JFR (`JavaMonitorEnter`).
### 2. AQS Is a Parking Queue
`ReentrantLock/Semaphore/CountDownLatch` share one FIFO + CAS core.
Fairness is a throughput-vs-starvation dial, not a default.
### 3. CAS Is Optimistic Consensus
`Atomic*`/VarHandles retry on contention. Great at low collision,
spinning waste at high collision — then use LongAdder/striping.
### 4. Deadlock Needs All Four Coffman Conditions
Mutual exclusion + hold-and-wait + no preemption + circular wait.
Break any one (ordering, timeout, tryLock) and deadlock dies.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Simple critical section? | synchronized (biased/inflated by JVM) |
| Need timeout/interrupt/fair? | ReentrantLock + tryLock(timeout) |
| Counter under contention? | LongAdder, not AtomicLong |
| Read-heavy map? | ConcurrentHashMap / StampedLock (careful) |

---
## Career Trajectory
- **L1:** synchronized, volatile, wait/notify, ConcurrentHashMap.
- **L2:** Locks, latches, barriers, atomics, deadlock diagnosis.
- **L3:** AQS internals, lock splitting/striping, JFR contention tuning.
- **L4:** Custom synchronizers, JMM proofs, contention budgets.

---
## 4-Week Path
```
W1: Monitor kata + deadlock repro + Thread.print diagnosis.
W2: AQS lab — fair vs unfair, tryLock timeouts, condition queues.
W3: Lock-free lab — CAS, ABA, LongAdder, VarHandle fences.
W4: Contended-ledger tuning — JFR contention profile + striped fix.
```
## Success Metrics
- [ ] Diagnose a deadlock from a dump in <10 min
- [ ] JFR monitor-enter p99 attributed to exact lock
- [ ] Contended counter 10x faster via striping (measured)
- [ ] Zero lock-ordering violations (ordered acquisition enforced)

## What This Is Not
Lock-free everything. Most wins come from smaller sections.

> Mantra: **Hold no lock while doing I/O; order every acquisition.**
