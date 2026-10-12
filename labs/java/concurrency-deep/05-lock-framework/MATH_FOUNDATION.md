# Math Foundation: Locks and Queues

## 1. Barging throughput gain (model)

Let handoff latency `H` = unpark + context-switch + cache-miss cost, and hold
time `L` = critical-section length. Fair throughput ≈ `1 / (L + H)`; nonfair
barging avoids `H` on a fraction `b` of acquisitions:

```
T_nonfair ≈ 1 / (L + (1 - b) * H)
```

With `L = 200ns`, `H = 1500ns`, `b = 0.7`: fair ≈ 588K ops/s, nonfair ≈
1/(200 + 450)ns ≈ 1.54M ops/s. The gain concentrates when `H >> L` (tiny
critical sections under contention) — exactly the microbenchmark shape where
nonfair wins.

## 2. Starvation bound

Nonfair barging admits unbounded overtaking: with arrival rate λ and service
rate μ per holder, a queued thread's wait has no finite worst case while
`λ > 0` persists. Fair mode bounds overtaking to at most one re-barge window
(release→wakeup gap): expected extra wait ≤ `H`, worst case still data-
dependent but with zero *overt* barges.

## 3. Queue length sketch (Little's law)

For arrival rate λ (acquisitions/s) and mean hold `L`:

```
mean queued threads ≈ λ * L   (when λ*L > 1, lock is the bottleneck)
```

λ = 2M/s, L = 1µs → ~2 waiters on average. If the measured queue
(`getQueueLength()`) grows linearly with offered load, the critical section —
not the lock implementation — is saturated; shrink `L` before blaming AQS.

## 4. ReadWriteLock bit packing

```
state = (readerCount << 16) | (writerCount & 0xFFFF)
MAX_COUNT = 65535 per half
```

Reader 70000 → overflow: the 17th bit bleeds into the writer half, so AQS
throws instead of corrupting. Reader count 3, writer 1 → `state =
0x00030001` = 196609. Decode with `sharedCount(c) = c >>> 16`,
`exclusiveCount(c) = c & MAX_COUNT`.

## 5. Semaphore permit arithmetic

`state` = permits. `acquire(n)`: `tryAcquireShared` returns `permits - n`
(negative = queued). Over-release is uncapped: `release()` past the initial
count grows `state` without bound — e.g. `Semaphore(5)` with 3 stray releases
holds 8 permits. Audit invariant: `releases - acquires ≤ initialPermits`.

## 6. Timeout probability

`tryLock(t)` succeeds iff some release lands in `[now, now+t]`. With mean
inter-release gap `G`, `P(success) ≈ 1 - e^(-t/G)` (exponential-gap sketch).
`t = 300ms`, `G = 100ms` → ~95%. Timeouts near `G` are coin flips — size `t`
at 5–10× `G` for stable behavior.
