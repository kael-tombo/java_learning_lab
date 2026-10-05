# VISION — Threading Deep Dive

## Vision Statement
**Threads are scheduled contention, not magic parallelism** — master
lifecycles, pools, and virtual threads so throughput scales without
mystery stalls, leaks, or 3 a.m. pool-exhaustion pages.

---
## Mental Models
### 1. Thread = Stack + Scheduler Slot
`Thread` object ≠ OS thread guarantee. Platform threads cost ~1MB
stack; virtual threads are cheap continuations on carriers.
### 2. Pool = Queue + Policy + Rejection
Core/max/keepAlive/queue/rejection define behavior under load more
than thread count. Unbounded queues hide overload until OOM.
### 3. Blocking Has a Price Tag
Blocking a platform thread wastes a carrier; blocking a virtual
thread (minus pinning) is cheap. Know which you hold.
### 4. Interruption Is Cooperative
`interrupt()` is a polite flag + unblock of sleep/wait/join. Code
that swallows `InterruptedException` breaks cancellation.

---
## Decision Framework
| Question | Rule |
|----------|------|
| I/O fan-out? | Virtual threads, one-per-task executor |
| CPU-bound? | `availableProcessors()` sized pool, no blocking |
| Mixed? | Separate pools; bulkhead I/O from CPU |
| Fire-and-forget? | Never — track, timeout, and reject explicitly |

---
## Career Trajectory
- **L1:** start/join, sleep, interrupt handling, ExecutorService basics.
- **L2:** Pool sizing, futures, ThreadLocal hygiene, deadlock reading.
- **L3:** Virtual threads, pinning, carrier sizing, structured scopes.
- **L4:** Capacity models, backpressure, fleet-wide thread governance.

---
## 4-Week Path
```
W1: Lifecycle + interruption kata; thread-dump reading drills.
W2: Pool sizing lab — bounded vs unbounded under synthetic overload.
W3: Virtual threads + pinning (synchronized vs ReentrantLock) with JFR.
W4: Bulkheaded gateway service + load test + dump-driven tuning report.
```
## Success Metrics
- [ ] `Thread.print` dump readable in <5 min (pool, state, lock)
- [ ] JFR shows ~0 `VirtualThreadPinned` on hot path
- [ ] Overload test rejects fast, never OOMs
- [ ] Cancellation propagates end-to-end (deadline respected)

## What This Is Not
"More threads = faster." It is applied queueing theory.

> Mantra: **Bound everything; observe what waits.**
