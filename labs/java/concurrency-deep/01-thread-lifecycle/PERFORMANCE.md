# Performance: Thread Lifecycle

## Cost model (qualitative — measure per workload)
- State transitions themselves are cheap; what costs is what the state implies: BLOCKED parks in the OS (context switches), parking/unparking crosses scheduler queues, spinning in RUNNABLE burns CPU for zero progress.
- Virtual threads make parked WAITING/TIMED_WAITING cheap (no carrier consumed) except where `synchronized` pins the carrier (through JDK 23) — pinning turns a cheap park into a held OS thread.
- Thread-per-task at platform scale exhausts stacks (~1MB default each) and scheduler capacity; pools or virtual threads bound the damage.

## Contention reasoning
- Identical BLOCKED stacks across many threads = serialized throughput: useful work per second caps at the critical-section rate regardless of thread count.
- Identical parked-take stacks = healthy: idle workers cost little until tasks arrive.
- No formula predicts your speedup; count runnable demand vs available cores and measure (next section).

## How to measure (JMH sketch)
```java
@Benchmark @Threads(8)
public void contended(Blackhole bh) { /* your guarded section */ bh.consume(work()); }
```
Compare 1 vs N threads, platform vs virtual (21+), synchronized vs ReentrantLock. Report ops/s + context-switch rate, not single-run timings.

## Tuning levers
1. Shrink critical sections and contested-monitor fan-in. 2. Replace blocking takes with bounded queues + backpressure. 3. Move `synchronized` off virtual-thread hot paths (pinning). 4. Prefer `lockInterruptibly/tryLock` where stuck-entry must stay cancellable.

## Rule
No tuning without a JMH number on the target JVM and architecture. Orders above are orientation; your workload's contention decides.

## Virtual-thread pinning cost
- Parked virtual threads cost no carrier — except inside `synchronized`, which pins the carrier through JDK 23; a hot `synchronized` block at virtual scale converts cheap WAITING into held OS threads.
- Measure pinning with JFR `jdk.VirtualThreadPinned` events (21+): nonzero counts on the hot path mean the `synchronized` must move or narrow.
- Replacement order: shrink the block first; only then swap the mechanism (`ReentrantLock` parks cleanly without pinning).
- Dumps at virtual scale: thousands of WAITING lines are backlog to count, not contention to fix — filter for BLOCKED before optimizing.

## Measurement checklist
- Record JDK version, CPU count, and `-Xss`/stack settings alongside every number — state behavior and footprint both shift with them.
- Report BLOCKED-count histograms across runs, not single dumps; contention is a distribution.
- Separate park time (scheduler queues, `LockSupport`) from monitor-hold time (critical-section length) — they tune differently.
- Re-run on the second architecture before claiming portability; descheduling and unpark latency differ by OS and CPU.

## Anti-patterns with numbers attached
- Unbounded thread-per-request on platform threads: ~1MB stack each turns 10k concurrent requests into ~10GB of committed stack — pools or virtual threads, no third option.
- `sleep`-based coordination loops: each poll interval adds up to one full interval of latency by construction; latches/futures remove the interval entirely.
- `getState()` polling loops: burn CPU in RUNNABLE while learning nothing a latch would not deliver — sampling replaces signaling at full price and zero rigor.
