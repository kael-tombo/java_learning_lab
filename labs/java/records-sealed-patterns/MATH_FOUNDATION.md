# Math Foundation — Records, Sealed Classes & Patterns (records-sealed-patterns)

Quantitative models behind data carriers, exhaustive switch, deconstruction. (LEETCODE_SOLUTIONS variant: complexity math.)

## Core formulas

- `Heap occupancy: Old = Total − (Eden + Survivor×2) − Metaspace_overhead (records-sealed-patterns)`

- `Little's Law: L = λ·W (threads/queue sizing)`

- `Amdahl: S = 1/((1−p)+p/n)`

- `Throughput = ops/time; latency p50/p99`

- `Hash cost ≈ O(1) avg; resize = O(n)`

- `GC pause budget: pause% = pause_time / interval`

- `Thread pool size ≈ cores × (1 + wait/compute)`

- `Memory: bytes ≈ header(12–16) + fields + padding→8`

## Worked mini-examples

1. `record canonical constructors`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
2. `compact constructors`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
3. `sealed permits`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
4. `pattern matching switch`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
5. `guarded patterns`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
6. `record patterns`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
7. `exhaustiveness`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
8. `serialization of records`: plug n=10k into relevant formula; estimate time/space; verify by measurement.

## Rules of thumb
- Measure before tuning; one variable at a time.
- p99 matters more than mean for SLAs.
- 80/20: profile hottest frame first.
- Note 0: apply to record canonical constructors; record assumption + error.
- Note 1: apply to compact constructors; record assumption + error.
- Note 2: apply to sealed permits; record assumption + error.
- Note 3: apply to pattern matching switch; record assumption + error.
- Note 4: apply to guarded patterns; record assumption + error.
- Note 5: apply to record patterns; record assumption + error.
- Note 6: apply to exhaustiveness; record assumption + error.
- Note 7: apply to serialization of records; record assumption + error.
- Note 8: apply to record canonical constructors; record assumption + error.
- Note 9: apply to compact constructors; record assumption + error.
- Note 10: apply to sealed permits; record assumption + error.
- Note 11: apply to pattern matching switch; record assumption + error.
- Note 12: apply to guarded patterns; record assumption + error.
- Note 13: apply to record patterns; record assumption + error.
- Note 14: apply to exhaustiveness; record assumption + error.
- Note 15: apply to serialization of records; record assumption + error.
- Note 16: apply to record canonical constructors; record assumption + error.
- Note 17: apply to compact constructors; record assumption + error.
- Note 18: apply to sealed permits; record assumption + error.
- Note 19: apply to pattern matching switch; record assumption + error.
- Note 20: apply to guarded patterns; record assumption + error.
- Note 21: apply to record patterns; record assumption + error.
- Note 22: apply to exhaustiveness; record assumption + error.
- Note 23: apply to serialization of records; record assumption + error.
- Note 24: apply to record canonical constructors; record assumption + error.
- Note 25: apply to compact constructors; record assumption + error.
- Note 26: apply to sealed permits; record assumption + error.
- Note 27: apply to pattern matching switch; record assumption + error.
- Note 28: apply to guarded patterns; record assumption + error.
- Note 29: apply to record patterns; record assumption + error.
- Note 30: apply to exhaustiveness; record assumption + error.
- Note 31: apply to serialization of records; record assumption + error.
- Note 32: apply to record canonical constructors; record assumption + error.
- Note 33: apply to compact constructors; record assumption + error.
- Note 34: apply to sealed permits; record assumption + error.
- Note 35: apply to pattern matching switch; record assumption + error.
- Note 36: apply to guarded patterns; record assumption + error.
- Note 37: apply to record patterns; record assumption + error.
- Note 38: apply to exhaustiveness; record assumption + error.
- Note 39: apply to serialization of records; record assumption + error.
- Note 40: apply to record canonical constructors; record assumption + error.
- Note 41: apply to compact constructors; record assumption + error.
- Note 42: apply to sealed permits; record assumption + error.
