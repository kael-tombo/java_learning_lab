# Performance: Volatile Semantics

## Cost model (qualitative by architecture)
- x86 (TSO): volatile reads cost about the same as plain reads (compiler-ordering only); volatile writes need a StoreLoad fence (`xchg`+`lock`) — tens of nanoseconds, comparable to an uncontended CAS.
- ARM/POWER (weak model): both reads and writes need explicit fences (`dmb ish` on ARMv8) — volatile costs more than on x86. Never port "volatile is free" numbers across architectures.
- The expensive mistake is semantic, not nanoseconds: volatile++ retries nothing and loses updates — any counter benchmark "winning" on volatile is measuring a race.

## Contention reasoning
- Volatile scales for publish/subscribe (one writer flag, many readers) — no retries, no parking.
- It does not scale for read-modify-write: N writers on volatile++ lose ~proportionally; AtomicLong/LongAdder exist for that shape (see lab 04).

## How to measure (JMH sketch)
```java
volatile int flag;
@Benchmark public int readFlag() { return flag; }
@Benchmark public void writeFlag() { flag = 1; }
```
Run on each target architecture; report read vs write separately. Then benchmark the AtomicLong/LongAdder counter you should have used for RMW.

## Tuning levers
1. Keep volatile for flags/publication; move counters to LongAdder. 2. Batch payload writes before a single volatile publish. 3. Reach for VarHandle acquire/release only with a profiler-backed reason.

## Rule
No tuning without a JMH number on the target JVM and architecture. Orders above are orientation; your workload's contention decides.

## Read/write asymmetry (x86 numbers, qualitative peers)
- Publish-heavy shapes (config reload: many payload writes, one flag write, many flag reads) amortize the single StoreLoad fence over k fields — per-field fence cost ≈ 1/k of a fence, so batching is the entire optimization.
- Flag-spin shapes (shutdown loops): volatile reads cost ≈ plain reads on x86, so spinning on a volatile flag is cheap per lap — but prefer `park`/latch notification to spinning wherever wake latency matters.
- Write-heavy flag shapes (per-event volatile writes): each write pays the fence (~10-20ns scale, uncontended-CAS-like) — at millions of events/s consider batching events behind one publish or a striped counter.

## RMW mis-tooling costs
- `volatile++` under contention: loses updates (correctness failure first) while *looking* fast — any benchmark crowning volatile for counters measures the race, not the speed; discard and re-run with `AtomicLong`/`LongAdder`.
- DCL fast path with local read: 1 volatile read per call vs 2 — halves fence cost for free (Bloch-approved shape); the saving is per-call fences, measurable at millions of calls/s.
- `AtomicIntegerArray` per-element volatile semantics: pays fence-grade cost per element access — correct for policy tables, overkill for bulk bulk-copy payloads better published by reference swap.

## Measurement protocol
- Separate read vs write benchmarks (`readFlag` vs `writeFlag` in the PERFORMANCE.md sketch): blended numbers hide the asymmetry that drives every volatile decision.
- Run the identical harness on each target architecture: x86 TSO numbers do not port to ARM (`dmb ish` both ways) — report per-arch tables, never a single "volatile cost".
- Stress publication harnesses (DCL, piggyback) with jittered thread starts across thousands of iterations; single-run passes are the absence of evidence, not evidence of safety.
- Compare against the mechanism you should have used (AtomicLong/LongAdder for RMW, holder idiom for singletons) in the same report — volatile numbers alone never justify volatile.

## Tuning levers (ordered by payoff)
1. Batch payload writes before one volatile publish — divide fence cost by batch size.
2. Move counters off volatile onto `LongAdder` (hot) or `AtomicLong` (cold) — correctness first, striping second.
3. Use the DCL local-read shape to halve fast-path volatile reads.
4. Descend to VarHandle acquire/release only with profiler evidence; opaque never for publication.
