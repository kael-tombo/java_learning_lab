# Math Foundation — Concurrency Deep & Virtual Threads (concurrency-deep)

Quantitative models behind JMM, Loom, structured concurrency, VarHandles. (LEETCODE_SOLUTIONS variant: complexity math.)

## Core formulas

- `Heap occupancy: Old = Total − (Eden + Survivor×2) − Metaspace_overhead (concurrency-deep)`

- `Little's Law: L = λ·W (threads/queue sizing)`

- `Amdahl: S = 1/((1−p)+p/n)`

- `Throughput = ops/time; latency p50/p99`

- `Hash cost ≈ O(1) avg; resize = O(n)`

- `GC pause budget: pause% = pause_time / interval`

- `Thread pool size ≈ cores × (1 + wait/compute)`

- `Memory: bytes ≈ header(12–16) + fields + padding→8`

## Worked mini-examples

1. `JMM happens-before`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
2. `virtual threads & carriers`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
3. `structured concurrency`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
4. `scoped values`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
5. `ForkJoinPool`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
6. `StampedLock/LongAdder`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
7. `VarHandle`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
8. `reactive vs virtual`: plug n=10k into relevant formula; estimate time/space; verify by measurement.

## Rules of thumb
- Measure before tuning; one variable at a time.
- p99 matters more than mean for SLAs.
- 80/20: profile hottest frame first.
- Note 0: apply to JMM happens-before; record assumption + error.
- Note 1: apply to virtual threads & carriers; record assumption + error.
- Note 2: apply to structured concurrency; record assumption + error.
- Note 3: apply to scoped values; record assumption + error.
- Note 4: apply to ForkJoinPool; record assumption + error.
- Note 5: apply to StampedLock/LongAdder; record assumption + error.
- Note 6: apply to VarHandle; record assumption + error.
- Note 7: apply to reactive vs virtual; record assumption + error.
- Note 8: apply to JMM happens-before; record assumption + error.
- Note 9: apply to virtual threads & carriers; record assumption + error.
- Note 10: apply to structured concurrency; record assumption + error.
- Note 11: apply to scoped values; record assumption + error.
- Note 12: apply to ForkJoinPool; record assumption + error.
- Note 13: apply to StampedLock/LongAdder; record assumption + error.
- Note 14: apply to VarHandle; record assumption + error.
- Note 15: apply to reactive vs virtual; record assumption + error.
- Note 16: apply to JMM happens-before; record assumption + error.
- Note 17: apply to virtual threads & carriers; record assumption + error.
- Note 18: apply to structured concurrency; record assumption + error.
- Note 19: apply to scoped values; record assumption + error.
- Note 20: apply to ForkJoinPool; record assumption + error.
- Note 21: apply to StampedLock/LongAdder; record assumption + error.
- Note 22: apply to VarHandle; record assumption + error.
- Note 23: apply to reactive vs virtual; record assumption + error.
- Note 24: apply to JMM happens-before; record assumption + error.
- Note 25: apply to virtual threads & carriers; record assumption + error.
- Note 26: apply to structured concurrency; record assumption + error.
- Note 27: apply to scoped values; record assumption + error.
- Note 28: apply to ForkJoinPool; record assumption + error.
- Note 29: apply to StampedLock/LongAdder; record assumption + error.
- Note 30: apply to VarHandle; record assumption + error.
- Note 31: apply to reactive vs virtual; record assumption + error.
- Note 32: apply to JMM happens-before; record assumption + error.
- Note 33: apply to virtual threads & carriers; record assumption + error.
- Note 34: apply to structured concurrency; record assumption + error.
- Note 35: apply to scoped values; record assumption + error.
- Note 36: apply to ForkJoinPool; record assumption + error.
- Note 37: apply to StampedLock/LongAdder; record assumption + error.
- Note 38: apply to VarHandle; record assumption + error.
- Note 39: apply to reactive vs virtual; record assumption + error.
- Note 40: apply to JMM happens-before; record assumption + error.
- Note 41: apply to virtual threads & carriers; record assumption + error.
- Note 42: apply to structured concurrency; record assumption + error.
