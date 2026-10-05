# VISION — Virtual Threads

## Vision Statement
**A thread per request, finally affordable** — millions of cheap virtual threads turn blocking code into scalable code, if you unlearn pool-tuning instincts.

---
## Mental Models
### 1. Cheap vs Pooled
Platform thread ≈ 1MB stack + OS thread; virtual thread ≈ KBs on heap, mounted on carrier. Create per task (`Thread.startVirtualThread`), don't pool.
### 2. Park, Don't Block
Virtual thread parks on blocking I/O and frees its carrier. Throughput scales with concurrent I/O, not CPU count.
### 3. Pinning Is the Gotcha
`synchronized` blocks and native/JNI calls pin the carrier (no unmount). Prefer `ReentrantLock` in hot paths on Java 21.
### 4. Structured Scope > Fire-and-Forget
`StructuredTaskScope` (preview/21+) binds subtask lifetimes to a scope: failure cancels siblings, results join at scope exit. No leaked futures.

---
## Decision Framework
| Question | Rule |
|----------|------|
| I/O-bound fan-out? | Virtual thread per task |
| CPU-bound math? | Platform pool sized to cores |
| synchronized on hot path? | Replace with ReentrantLock |
| ThreadLocal-heavy? | Migrate to ScopedValue; audit memory |

---
## Career Trajectory
- **L1:** `Thread.ofVirtual().start()`, `newVirtualThreadPerTaskExecutor()` with try-with-resources.
- **L2:** Pinning diagnosis, ReentrantLock swap, ThreadLocal audit.
- **L3:** StructuredTaskScope (ShutdownOnFailure/Success), JFR virtual-thread events.
- **L4:** Platform-vs-virtual capacity planning, migration of legacy pools.

---
## 4-Week Path
```
W1: Virtual basics: 100k-thread hello, executor migration of a client.
W2: Pinning lab: synchronized vs ReentrantLock under JFR.
W3: Structured concurrency: fan-out fetch with deadline + cancel.
W4: Gateway kata: 10k-concurrent fake-I/O benchmark, platform vs virtual.
```
## Success Metrics
- [ ] Run 100k concurrent sleeps without tuning
- [ ] Detect + fix one pinning hotspot with JFR evidence
- [ ] Justify platform vs virtual per workload with numbers
