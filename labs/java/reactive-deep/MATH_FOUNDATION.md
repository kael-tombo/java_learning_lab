# Math Foundation — Reactive Java Deep Dive (reactive-deep)

Quantitative models behind Reactor, RxJava, Flow API, backpressure. (LEETCODE_SOLUTIONS variant: complexity math.)

## Core formulas

- `Heap occupancy: Old = Total − (Eden + Survivor×2) − Metaspace_overhead (reactive-deep)`

- `Little's Law: L = λ·W (threads/queue sizing)`

- `Amdahl: S = 1/((1−p)+p/n)`

- `Throughput = ops/time; latency p50/p99`

- `Hash cost ≈ O(1) avg; resize = O(n)`

- `GC pause budget: pause% = pause_time / interval`

- `Thread pool size ≈ cores × (1 + wait/compute)`

- `Memory: bytes ≈ header(12–16) + fields + padding→8`

## Worked mini-examples

1. `Publisher/Subscriber`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
2. `Flux/Mono`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
3. `backpressure strategies`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
4. `schedulers`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
5. `error handling`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
6. `testing with StepVerifier`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
7. `R2DBC/reactive web`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
8. `virtual threads vs reactive`: plug n=10k into relevant formula; estimate time/space; verify by measurement.

## Rules of thumb
- Measure before tuning; one variable at a time.
- p99 matters more than mean for SLAs.
- 80/20: profile hottest frame first.
- Note 0: apply to Publisher/Subscriber; record assumption + error.
- Note 1: apply to Flux/Mono; record assumption + error.
- Note 2: apply to backpressure strategies; record assumption + error.
- Note 3: apply to schedulers; record assumption + error.
- Note 4: apply to error handling; record assumption + error.
- Note 5: apply to testing with StepVerifier; record assumption + error.
- Note 6: apply to R2DBC/reactive web; record assumption + error.
- Note 7: apply to virtual threads vs reactive; record assumption + error.
- Note 8: apply to Publisher/Subscriber; record assumption + error.
- Note 9: apply to Flux/Mono; record assumption + error.
- Note 10: apply to backpressure strategies; record assumption + error.
- Note 11: apply to schedulers; record assumption + error.
- Note 12: apply to error handling; record assumption + error.
- Note 13: apply to testing with StepVerifier; record assumption + error.
- Note 14: apply to R2DBC/reactive web; record assumption + error.
- Note 15: apply to virtual threads vs reactive; record assumption + error.
- Note 16: apply to Publisher/Subscriber; record assumption + error.
- Note 17: apply to Flux/Mono; record assumption + error.
- Note 18: apply to backpressure strategies; record assumption + error.
- Note 19: apply to schedulers; record assumption + error.
- Note 20: apply to error handling; record assumption + error.
- Note 21: apply to testing with StepVerifier; record assumption + error.
- Note 22: apply to R2DBC/reactive web; record assumption + error.
- Note 23: apply to virtual threads vs reactive; record assumption + error.
- Note 24: apply to Publisher/Subscriber; record assumption + error.
- Note 25: apply to Flux/Mono; record assumption + error.
- Note 26: apply to backpressure strategies; record assumption + error.
- Note 27: apply to schedulers; record assumption + error.
- Note 28: apply to error handling; record assumption + error.
- Note 29: apply to testing with StepVerifier; record assumption + error.
- Note 30: apply to R2DBC/reactive web; record assumption + error.
- Note 31: apply to virtual threads vs reactive; record assumption + error.
- Note 32: apply to Publisher/Subscriber; record assumption + error.
- Note 33: apply to Flux/Mono; record assumption + error.
- Note 34: apply to backpressure strategies; record assumption + error.
- Note 35: apply to schedulers; record assumption + error.
- Note 36: apply to error handling; record assumption + error.
- Note 37: apply to testing with StepVerifier; record assumption + error.
- Note 38: apply to R2DBC/reactive web; record assumption + error.
- Note 39: apply to virtual threads vs reactive; record assumption + error.
- Note 40: apply to Publisher/Subscriber; record assumption + error.
- Note 41: apply to Flux/Mono; record assumption + error.
- Note 42: apply to backpressure strategies; record assumption + error.
