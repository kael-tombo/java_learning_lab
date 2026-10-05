# VISION — Concurrency

## Vision Statement
**Correct first, fast second** — threads buy throughput only when shared state is disciplined; every race you prevent beats any benchmark you win.

---
## Mental Models
### 1. Happens-Before Is the Contract
`volatile`, `synchronized`, `Lock`, `final` publish — without a happens-before edge, another thread may never see your write. Reason in edges, not sleeps.
### 2. Confinement > Locking > CAS
Best: don't share (confinement, thread-locals). Next: guard with locks. Last: lock-free CAS loops for hot counters.
### 3. Pools Have Two Knobs
Threads + queue. Unbounded queue + fixed pool = OOM under spike; unbounded threads = context-switch death. Size by Little's law, bound the queue, define rejection.
### 4. Liveness Quartet
Deadlock, livelock, starvation, missed-signal. Lock ordering, timeouts (`tryLock`), and `await/signal` discipline prevent all four.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Share state? | Confine first; else `ConcurrentHashMap`/immutable snapshot |
| Counter/hot path? | `LongAdder`, not `AtomicLong` under contention |
| Blocking I/O in pool? | Isolate pool; never block ForkJoin common pool |
| Shutdown? | Always `shutdown()+awaitTermination`; reject policy explicit |

---
## Career Trajectory
- **L1:** `Thread`, `Runnable`, `join`, `synchronized`, `volatile` basics.
- **L2:** `ExecutorService`, `Future`, `ConcurrentHashMap`, `CountDownLatch/CyclicBarrier`.
- **L3:** `CompletableFuture` graphs, `ReentrantLock/ReadWriteLock`, deadlock analysis with thread dumps.
- **L4:** Sizing/backpressure design, lock-free structures, contention profiling.

---
## 4-Week Path
```
W1: Threads, join, visibility puzzle (non-volatile flag never seen).
W2: Executors, bounded queues, rejection policies, shutdown discipline.
W3: ConcurrentHashMap compute, LongAdder, CompletableFuture pipelines.
W4: Rate-limited crawler kata + deadlock drill with jstack analysis.
```
## Success Metrics
- [ ] Explain any fix with the exact happens-before edge used
- [ ] No unbounded pools/queues in reviewed code
- [ ] Diagnose deadlock from a thread dump in < 15 min
