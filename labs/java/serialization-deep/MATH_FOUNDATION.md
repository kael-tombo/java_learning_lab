# Math Foundation — Deep Serialization (serialization-deep)

Quantitative models behind Java native, Jackson, Avro, Protobuf, versioning. (LEETCODE_SOLUTIONS variant: complexity math.)

## Core formulas

- `Heap occupancy: Old = Total − (Eden + Survivor×2) − Metaspace_overhead (serialization-deep)`

- `Little's Law: L = λ·W (threads/queue sizing)`

- `Amdahl: S = 1/((1−p)+p/n)`

- `Throughput = ops/time; latency p50/p99`

- `Hash cost ≈ O(1) avg; resize = O(n)`

- `GC pause budget: pause% = pause_time / interval`

- `Thread pool size ≈ cores × (1 + wait/compute)`

- `Memory: bytes ≈ header(12–16) + fields + padding→8`

## Worked mini-examples

1. `Serializable & serialVersionUID`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
2. `Externalizable`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
3. `Jackson databind`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
4. `Avro schemas`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
5. `Protobuf`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
6. `versioning & compatibility`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
7. `security of deserialization`: plug n=10k into relevant formula; estimate time/space; verify by measurement.
8. `performance tradeoffs`: plug n=10k into relevant formula; estimate time/space; verify by measurement.

## Rules of thumb
- Measure before tuning; one variable at a time.
- p99 matters more than mean for SLAs.
- 80/20: profile hottest frame first.
- Note 0: apply to Serializable & serialVersionUID; record assumption + error.
- Note 1: apply to Externalizable; record assumption + error.
- Note 2: apply to Jackson databind; record assumption + error.
- Note 3: apply to Avro schemas; record assumption + error.
- Note 4: apply to Protobuf; record assumption + error.
- Note 5: apply to versioning & compatibility; record assumption + error.
- Note 6: apply to security of deserialization; record assumption + error.
- Note 7: apply to performance tradeoffs; record assumption + error.
- Note 8: apply to Serializable & serialVersionUID; record assumption + error.
- Note 9: apply to Externalizable; record assumption + error.
- Note 10: apply to Jackson databind; record assumption + error.
- Note 11: apply to Avro schemas; record assumption + error.
- Note 12: apply to Protobuf; record assumption + error.
- Note 13: apply to versioning & compatibility; record assumption + error.
- Note 14: apply to security of deserialization; record assumption + error.
- Note 15: apply to performance tradeoffs; record assumption + error.
- Note 16: apply to Serializable & serialVersionUID; record assumption + error.
- Note 17: apply to Externalizable; record assumption + error.
- Note 18: apply to Jackson databind; record assumption + error.
- Note 19: apply to Avro schemas; record assumption + error.
- Note 20: apply to Protobuf; record assumption + error.
- Note 21: apply to versioning & compatibility; record assumption + error.
- Note 22: apply to security of deserialization; record assumption + error.
- Note 23: apply to performance tradeoffs; record assumption + error.
- Note 24: apply to Serializable & serialVersionUID; record assumption + error.
- Note 25: apply to Externalizable; record assumption + error.
- Note 26: apply to Jackson databind; record assumption + error.
- Note 27: apply to Avro schemas; record assumption + error.
- Note 28: apply to Protobuf; record assumption + error.
- Note 29: apply to versioning & compatibility; record assumption + error.
- Note 30: apply to security of deserialization; record assumption + error.
- Note 31: apply to performance tradeoffs; record assumption + error.
- Note 32: apply to Serializable & serialVersionUID; record assumption + error.
- Note 33: apply to Externalizable; record assumption + error.
- Note 34: apply to Jackson databind; record assumption + error.
- Note 35: apply to Avro schemas; record assumption + error.
- Note 36: apply to Protobuf; record assumption + error.
- Note 37: apply to versioning & compatibility; record assumption + error.
- Note 38: apply to security of deserialization; record assumption + error.
- Note 39: apply to performance tradeoffs; record assumption + error.
- Note 40: apply to Serializable & serialVersionUID; record assumption + error.
- Note 41: apply to Externalizable; record assumption + error.
- Note 42: apply to Jackson databind; record assumption + error.
