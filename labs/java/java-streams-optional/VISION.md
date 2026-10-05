# Vision — Streams & Optional

## Direction
- Streams stay for batch transforms; Gatherers (custom intermediates) mature.
- Virtual threads + structured concurrency complement, not replace, streams.
- Records + patterns make collectors/pipelines more expressive.

## 5-Year Bets
1. Gatherers standard for windows/batching in ETL.
2. Primitive + value-type streams cut boxing (Valhalla).
3. `Optional` stays return-type only; no field/param creep.

## Constants
- Lazy + short-circuit first; measure before parallel.
- No shared mutation in pipelines.

## Signals
- Gatherers JEP, Valhalla primitives, SequencedCollections.
- Code reviews flagging parallel misuse.

## Career
Correct, fast pipelines (single-pass, no-box) mark senior ETL/backend work.

## Anti-Vision
Don't parallelize everything — common-pool starvation hurts.
Don't chain 20 ops — extract named functions.

## 30/60/90
- 30d: collectors + optional chaining.
- 60d: custom collector + gatherer.
- 90d: production ETL with benchmarks.
