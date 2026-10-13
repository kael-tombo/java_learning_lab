# Performance: JMM Foundations

## The pricing principle: edges cost, plain code is free

Unordered code pays nothing and guarantees nothing. Each hb edge buys a
verdict (visibility, ordering, exclusion) for a fence and coordination
price. The lab's demos are chosen to show the cheapest edge per shape —
start/join (already paid: thread creation dwarfs the fence), monitor
(one atomic plus fences per critical section), latch (one-shot volatile
chain). Never pay for a stronger edge than the shape needs.

## What each demo's edge costs (structural, x86)

- **Start/join**: the dominant cost is thread creation and scheduling
  (microseconds); the hb fences ride along for a few nanoseconds. If
  you already start and join a thread, its edge is the cheapest
  publication in the system — use it before adding volatiles.
- **Monitor (LockEdge)**: 2M guarded increments complete in well under
  contention collapse on 8 threads because uncontended lock/unlock is
  tens of nanoseconds of CAS plus fences. Throughput scales until the
  lock word itself becomes the bottleneck — then shard the counter or
  switch to striped/AtomicLong accumulation.
- **Latch**: one AQS volatile chain per handoff — single-digit
  nanoseconds of fence cost plus a park/unpark if the waiter blocks.
  Cheaper than a lock for one-shot publication; wrong tool for repeated
  mutual exclusion.
- **Volatile reference publication** (exercise 6 variant): one release
  store per publish — on x86 the write fence dominates (lab 03 measures
  ~10 ns vs ~1 ns plain). Publish rarely, read freely: reads are nearly
  free on TSO.

## The cost hierarchy to internalize

```
thread-lifecycle edge (amortized over thread lifetime): cheapest per byte
plain access: ~1 ns, no guarantee
acquire read / release store: ~1-2 ns on x86 (compiler barrier + cheap op)
volatile store (SC fence): ~10 ns on x86 (lab 03 ladder)
monitor enter/exit: tens of ns uncontended, contended = scheduling
park/unpark + context switch: microseconds
```

Choose the lowest row whose guarantee covers the shape: lifecycle >
latch/volatile-reference > release/acquire chain > lock > blocking
primitives. Escalate only when the verdict demands it.

## Measurement discipline (from lab 03, applied here)

- Compare within one JVM: warm both paths, then measure (frequency
  scaling dwarfs fence effects on cold runs).
- Defeat elimination with indexed traffic (distinct slots per
  iteration), as the lab-03 harnesses do — a loop over one location
  measures register allocation, not memory ordering.
- Quote ratios and verdicts across machines, never absolutes:
  nanoseconds are platform-relative, fence counts are structural.

## Anti-patterns that cost real money

- Volatile per-element stores in a bulk publish (fence per element):
  publish the array reference once instead — one fence, same guarantee.
- Lock per increment at high contention (the 2M demo shape at 64
  threads): switch to LongAdder-style striping; the hb story is
  unchanged, the lock word stops melting.
- Busy-spin `await` replacements (plain flag + onSpinWait): burns a
  core at full power to avoid a one-shot park that costs microseconds
  once. Spin only for nanosecond-scale rendezvous (lab 02's litmus),
  never for task handoff.
