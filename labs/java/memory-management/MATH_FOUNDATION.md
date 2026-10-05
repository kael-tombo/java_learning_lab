# Math Foundation — Java Memory Management (memory-management)

Quantitative models behind allocation, GC tuning, leak detection, heap dumps. (LEETCODE_SOLUTIONS variant: complexity math.)

## Core formulas

- `Heap occupancy: Old = Total − (Eden + Survivor×2) − Metaspace_overhead (memory-management)`

- `Little's Law: L = λ·W (threads/queue sizing)`

- `Amdahl: S = 1/((1−p)+p/n)`

- `Throughput = ops/time; latency p50/p99`

- `Hash cost ≈ O(1) avg; resize = O(n)`

- `GC pause budget: pause% = pause_time / interval`

- `Thread pool size ≈ cores × (1 + wait/compute)`

- `Memory: bytes ≈ header(12–16) + fields + padding→8`

## Worked mini-examples

1. `allocation paths (TLAB)`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
2. `young/old GC`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
3. `G1/ZGC/Shenandoah`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
4. `tuning flags`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
5. `leak detection`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
6. `heap dump analysis`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
7. `OOM causes`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
8. `direct memory`: plug n=10k into relevant formula; estimate time/space; verify by measurement.

## Rules of thumb
- Measure before tuning; one variable at a time.
- p99 matters more than mean for SLAs.
- 80/20: profile hottest frame first.
- Note 0: apply to allocation paths (TLAB); record assumption + error.
- Note 1: apply to young/old GC; record assumption + error.
- Note 2: apply to G1/ZGC/Shenandoah; record assumption + error.
- Note 3: apply to tuning flags; record assumption + error.
- Note 4: apply to leak detection; record assumption + error.
- Note 5: apply to heap dump analysis; record assumption + error.
- Note 6: apply to OOM causes; record assumption + error.
- Note 7: apply to direct memory; record assumption + error.
- Note 8: apply to allocation paths (TLAB); record assumption + error.
- Note 9: apply to young/old GC; record assumption + error.
- Note 10: apply to G1/ZGC/Shenandoah; record assumption + error.
- Note 11: apply to tuning flags; record assumption + error.
- Note 12: apply to leak detection; record assumption + error.
- Note 13: apply to heap dump analysis; record assumption + error.
- Note 14: apply to OOM causes; record assumption + error.
- Note 15: apply to direct memory; record assumption + error.
- Note 16: apply to allocation paths (TLAB); record assumption + error.
- Note 17: apply to young/old GC; record assumption + error.
- Note 18: apply to G1/ZGC/Shenandoah; record assumption + error.
- Note 19: apply to tuning flags; record assumption + error.
- Note 20: apply to leak detection; record assumption + error.
- Note 21: apply to heap dump analysis; record assumption + error.
- Note 22: apply to OOM causes; record assumption + error.
- Note 23: apply to direct memory; record assumption + error.
- Note 24: apply to allocation paths (TLAB); record assumption + error.
- Note 25: apply to young/old GC; record assumption + error.
- Note 26: apply to G1/ZGC/Shenandoah; record assumption + error.
- Note 27: apply to tuning flags; record assumption + error.
- Note 28: apply to leak detection; record assumption + error.
- Note 29: apply to heap dump analysis; record assumption + error.
- Note 30: apply to OOM causes; record assumption + error.
- Note 31: apply to direct memory; record assumption + error.
- Note 32: apply to allocation paths (TLAB); record assumption + error.
- Note 33: apply to young/old GC; record assumption + error.
- Note 34: apply to G1/ZGC/Shenandoah; record assumption + error.
- Note 35: apply to tuning flags; record assumption + error.
- Note 36: apply to leak detection; record assumption + error.
- Note 37: apply to heap dump analysis; record assumption + error.
- Note 38: apply to OOM causes; record assumption + error.
- Note 39: apply to direct memory; record assumption + error.
- Note 40: apply to allocation paths (TLAB); record assumption + error.
- Note 41: apply to young/old GC; record assumption + error.
- Note 42: apply to G1/ZGC/Shenandoah; record assumption + error.
