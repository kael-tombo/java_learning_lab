# Performance: Lock Framework

## Where time goes

1. Uncontended `lock()`: one CAS (~10–25ns) + owner write. Matches or beats
   `synchronized` biased/thin paths on modern JDKs for simple shapes.
2. Contended nonfair: barging avoids unpark latency on the fast fraction;
   measured wins concentrate when hold time < 1µs.
3. Contended fair: every handoff pays `unpark` + context switch (~1–3µs) plus
   the `hasQueuedThreads` check per acquire.
4. `tryLock(timeout)`: adds timed-park bookkeeping; cancellations churn the
   queue (bounded backward cleanups).

## Benchmark it (JMH sketch)

```java
@State(Scope.Benchmark)
public class LockBench {
    ReentrantLock nonfair = new ReentrantLock(false);
    ReentrantLock fair = new ReentrantLock(true);
    int x;
    @Benchmark public int nonfairInc() {
        nonfair.lock(); try { return ++x; } finally { nonfair.unlock(); }
    }
    @Benchmark public int fairInc() {
        fair.lock(); try { return ++x; } finally { fair.unlock(); }
    }
}
```

Run with several threads (`-t 8`) and a tiny body: nonfair leads. Grow the
body past ~5µs: the gap narrows because hold time dominates handoff cost.

## ReadWriteLock numbers

Reads scale while uncontended (shared CAS on the high half); a single active
writer serializes everything; writer request blocks new readers (write
preference avoids writer starvation). Read-heavy + rare-write is the only
shape where RWLock beats a plain `ReentrantLock` — measure, because the
packed-state CAS can contend harder than two separate counters would.

## Semaphore/CountDownLatch costs

Permit acquire/release = one shared-state CAS each when uncontended. Latch
`await` parks once; `countDown` is a plain CAS; the trip to zero triggers one
propagating wakeup chain — O(waiters) unparks, no thundering-herd retry.

## Tuning rules

- Default nonfair; switch to fair only with starvation evidence (p99 wait
  outliers under sustained contention), and re-measure throughput after.
- Shrink the critical section before switching lock types — queue length grows
  with `λ * hold time`, and no fairness flag fixes an oversized section.
- Prefer `tryLock(timeout)` with backoff over unbounded `lock()` in
  lock-ordering-risky code (deadlock becomes a logged retry).
- Split locks (per-shard, per-key) beat any single-lock tuning once the queue
  depth stays > 0 at target load.

## What NOT to do

- Fair lock "just in case" — pays handoff latency on every acquire.
- `tryLock()` polling loops without backoff — CAS storms burn the very cycles
  the holder needs to release.
- RWLock for write-heavy maps — writer serialization plus reader CAS churn
  loses to `ConcurrentHashMap` or a plain lock.
