# Math Foundation — Java Concurrency Basics (concurrency)

Quantitative models behind threads, locks, executors, atomics. (LEETCODE_SOLUTIONS variant: complexity math.)

## Core formulas

- `Heap occupancy: Old = Total − (Eden + Survivor×2) − Metaspace_overhead (concurrency)`

- `Little's Law: L = λ·W (threads/queue sizing)`

- `Amdahl: S = 1/((1−p)+p/n)`

- `Throughput = ops/time; latency p50/p99`

- `Hash cost ≈ O(1) avg; resize = O(n)`

- `GC pause budget: pause% = pause_time / interval`

- `Thread pool size ≈ cores × (1 + wait/compute)`

- `Memory: bytes ≈ header(12–16) + fields + padding→8`

## Worked mini-examples

1. `Thread lifecycle`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
2. `synchronized & volatile`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
3. `Locks & conditions`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
4. `Executors & pools`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
5. `Futures & CompletableFuture`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
6. `atomics`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
7. `deadlock avoidance`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
8. `thread-safety patterns`: plug n=10k into relevant formula; estimate time/space; verify by measurement.

## Rules of thumb
- Measure before tuning; one variable at a time.
- p99 matters more than mean for SLAs.
- 80/20: profile hottest frame first.
- Note 0: apply to Thread lifecycle; record assumption + error.
- Note 1: apply to synchronized & volatile; record assumption + error.
- Note 2: apply to Locks & conditions; record assumption + error.
- Note 3: apply to Executors & pools; record assumption + error.
- Note 4: apply to Futures & CompletableFuture; record assumption + error.
- Note 5: apply to atomics; record assumption + error.
- Note 6: apply to deadlock avoidance; record assumption + error.
- Note 7: apply to thread-safety patterns; record assumption + error.
- Note 8: apply to Thread lifecycle; record assumption + error.
- Note 9: apply to synchronized & volatile; record assumption + error.
- Note 10: apply to Locks & conditions; record assumption + error.
- Note 11: apply to Executors & pools; record assumption + error.
- Note 12: apply to Futures & CompletableFuture; record assumption + error.
- Note 13: apply to atomics; record assumption + error.
- Note 14: apply to deadlock avoidance; record assumption + error.
- Note 15: apply to thread-safety patterns; record assumption + error.
- Note 16: apply to Thread lifecycle; record assumption + error.
- Note 17: apply to synchronized & volatile; record assumption + error.
- Note 18: apply to Locks & conditions; record assumption + error.
- Note 19: apply to Executors & pools; record assumption + error.
- Note 20: apply to Futures & CompletableFuture; record assumption + error.
- Note 21: apply to atomics; record assumption + error.
- Note 22: apply to deadlock avoidance; record assumption + error.
- Note 23: apply to thread-safety patterns; record assumption + error.
- Note 24: apply to Thread lifecycle; record assumption + error.
- Note 25: apply to synchronized & volatile; record assumption + error.
- Note 26: apply to Locks & conditions; record assumption + error.
- Note 27: apply to Executors & pools; record assumption + error.
- Note 28: apply to Futures & CompletableFuture; record assumption + error.
- Note 29: apply to atomics; record assumption + error.
- Note 30: apply to deadlock avoidance; record assumption + error.
- Note 31: apply to thread-safety patterns; record assumption + error.
- Note 32: apply to Thread lifecycle; record assumption + error.
- Note 33: apply to synchronized & volatile; record assumption + error.
- Note 34: apply to Locks & conditions; record assumption + error.
- Note 35: apply to Executors & pools; record assumption + error.
- Note 36: apply to Futures & CompletableFuture; record assumption + error.
- Note 37: apply to atomics; record assumption + error.
- Note 38: apply to deadlock avoidance; record assumption + error.
- Note 39: apply to thread-safety patterns; record assumption + error.
- Note 40: apply to Thread lifecycle; record assumption + error.
- Note 41: apply to synchronized & volatile; record assumption + error.
- Note 42: apply to Locks & conditions; record assumption + error.
