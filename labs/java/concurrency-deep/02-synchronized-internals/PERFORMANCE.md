# Performance: Synchronized Internals

## Cost model (orders of magnitude, not promises)
- Uncontended stack-locking fast path: tens of nanoseconds (~10-20ns scale) — a mark-word CAS to your own stack record, no syscall.
- Recursive entry: one more nearly-free record push.
- Inflated contention: OS mutex + park/unpark per waiter — microseconds plus scheduling delay; throughput caps at the critical-section rate.
- JIT extras: lock elision (non-escaping objects) can remove the lock entirely; coarsening merges adjacent same-monitor blocks. Both show in JIT logs, never in source.

## Contention reasoning
- Throughput under contention ~= 1 / (critical-section time); adding threads past that only grows the EntryList and park traffic.
- No fairness: winners are unspecified, starvation legal — tail latency, not just mean, degrades.

## How to measure (JMH sketch)
```java
@Benchmark @Threads(16)
public int guardedIncrement() { synchronized (guard) { return ++shared; } }
```
Vary thread count and guard granularity; attach `-XX:+PrintCompilation -XX:+LogCompilation` to confirm elision/coarsening rather than assuming it.

## Tuning levers
1. Narrow the block to the invariant (move I/O, alien calls out). 2. Split guards per independent invariant. 3. Consider ReentrantLock only for timeout/interrupt/fairness/multiple-conditions — not for raw speed on uncontended paths.

## Rule
No tuning without a JMH number on the target JVM and architecture. Orders above are orientation; your workload's contention decides.

## Inflation economics
- Onset cost: first real contention pays allocation (ObjectMonitor) plus the first park/unpark round-trip — latency spikes on exactly the request that tips the lock over, then settles at the inflated rate.
- Steady contention: throughput ≈ 1/C (C = critical-section time) with per-waiter park/unpark microseconds on top; adding threads grows `_EntryList` depth and scheduler traffic, not commits.
- Deflation churn on bursty guards: repeated inflate/deflate cycles add variance without changing the mean — splitting the guard or narrowing the section removes the cycle, not the load.
- Virtual-thread multiplier (21+): each BLOCKED virtual thread holds a carrier through JDK 23 pinning — price contention in carriers, not just microseconds, on virtual runtimes.

## Measurement protocol
- Warm up past JIT and inflation settling (millions of acquisitions, as in CODE_DEEP_DIVE.md snippet 5) before reading any number — cold locks measure compilation, not contention.
- Sweep thread count (1/4/16/64) at fixed work: the knee where ops/s flattens is the contention point; report the knee, not one configuration.
- Attach `-XX:+PrintCompilation -XX:+LogCompilation` to separate elided/coarsened sites (0ns or merged) from real acquisitions before concluding anything about "synchronized cost".
- Capture JFR `jdk.JavaMonitorEnter` with stack traces at the knee: the hottest blocked frame names the guard to split, not the method to micro-opt.

## Tuning levers (ordered by payoff)
1. Narrow the block to the invariant; move I/O, logging, and alien calls out — section time divides throughput directly.
2. Split one guard per independent invariant; shared monitors serialize unrelated work at 1/C total.
3. Batch adjacent same-monitor updates to invite coarsening; keep guarded objects thread-local to invite elision.
4. Reach for `ReentrantLock` only for timeouts, interruption, fairness, or multiple conditions — never for raw uncontended speed, where stack locking already wins.
5. On virtual-thread hot paths, prefer park-based locks over `synchronized` to avoid carrier pinning (through JDK 23).
