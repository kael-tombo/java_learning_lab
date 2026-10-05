# Math Foundation — Java Performance Engineering (performance-deep)

Quantitative models behind JMH, JIT, profiling, GC latency. (LEETCODE_SOLUTIONS variant: complexity math.)

## Core formulas

- `Heap occupancy: Old = Total − (Eden + Survivor×2) − Metaspace_overhead (performance-deep)`

- `Little's Law: L = λ·W (threads/queue sizing)`

- `Amdahl: S = 1/((1−p)+p/n)`

- `Throughput = ops/time; latency p50/p99`

- `Hash cost ≈ O(1) avg; resize = O(n)`

- `GC pause budget: pause% = pause_time / interval`

- `Thread pool size ≈ cores × (1 + wait/compute)`

- `Memory: bytes ≈ header(12–16) + fields + padding→8`

## Worked mini-examples

1. `JMH benchmarks`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
2. `JIT C1/C2 & inlining`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
3. `escape analysis`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
4. `allocation profiling`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
5. `async-profiler/JFR`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
6. `GC pause tuning`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
7. `lock contention`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
8. `vector API`: plug n=10k into relevant formula; estimate time/space; verify by measurement.

## Rules of thumb
- Measure before tuning; one variable at a time.
- p99 matters more than mean for SLAs.
- 80/20: profile hottest frame first.
- Note 0: apply to JMH benchmarks; record assumption + error.
- Note 1: apply to JIT C1/C2 & inlining; record assumption + error.
- Note 2: apply to escape analysis; record assumption + error.
- Note 3: apply to allocation profiling; record assumption + error.
- Note 4: apply to async-profiler/JFR; record assumption + error.
- Note 5: apply to GC pause tuning; record assumption + error.
- Note 6: apply to lock contention; record assumption + error.
- Note 7: apply to vector API; record assumption + error.
- Note 8: apply to JMH benchmarks; record assumption + error.
- Note 9: apply to JIT C1/C2 & inlining; record assumption + error.
- Note 10: apply to escape analysis; record assumption + error.
- Note 11: apply to allocation profiling; record assumption + error.
- Note 12: apply to async-profiler/JFR; record assumption + error.
- Note 13: apply to GC pause tuning; record assumption + error.
- Note 14: apply to lock contention; record assumption + error.
- Note 15: apply to vector API; record assumption + error.
- Note 16: apply to JMH benchmarks; record assumption + error.
- Note 17: apply to JIT C1/C2 & inlining; record assumption + error.
- Note 18: apply to escape analysis; record assumption + error.
- Note 19: apply to allocation profiling; record assumption + error.
- Note 20: apply to async-profiler/JFR; record assumption + error.
- Note 21: apply to GC pause tuning; record assumption + error.
- Note 22: apply to lock contention; record assumption + error.
- Note 23: apply to vector API; record assumption + error.
- Note 24: apply to JMH benchmarks; record assumption + error.
- Note 25: apply to JIT C1/C2 & inlining; record assumption + error.
- Note 26: apply to escape analysis; record assumption + error.
- Note 27: apply to allocation profiling; record assumption + error.
- Note 28: apply to async-profiler/JFR; record assumption + error.
- Note 29: apply to GC pause tuning; record assumption + error.
- Note 30: apply to lock contention; record assumption + error.
- Note 31: apply to vector API; record assumption + error.
- Note 32: apply to JMH benchmarks; record assumption + error.
- Note 33: apply to JIT C1/C2 & inlining; record assumption + error.
- Note 34: apply to escape analysis; record assumption + error.
- Note 35: apply to allocation profiling; record assumption + error.
- Note 36: apply to async-profiler/JFR; record assumption + error.
- Note 37: apply to GC pause tuning; record assumption + error.
- Note 38: apply to lock contention; record assumption + error.
- Note 39: apply to vector API; record assumption + error.
- Note 40: apply to JMH benchmarks; record assumption + error.
- Note 41: apply to JIT C1/C2 & inlining; record assumption + error.
- Note 42: apply to escape analysis; record assumption + error.
