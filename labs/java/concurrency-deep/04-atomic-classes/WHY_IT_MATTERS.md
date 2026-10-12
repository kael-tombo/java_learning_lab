# Why It Matters: Atomic Classes

## Production consequences
1. **Outages.** Misreading lock-free read-modify-write via CAS: AtomicX, stamped references, and striped counters causes hangs (lost notify, uninterruptible BLOCKED), corruption (unpublished construction, torn compound updates), and cascading latency (contended single CAS word, inflated monitors under load).
2. **Debuggability.** The same facts that prevent bugs diagnose them: `java.base/java/util/concurrent/atomic/AtomicInteger.java` (JDK 23), `Striped64.java` class javadoc, `VarHandle` specs, JSR-166 (2004, Doug Lea) tokens map 1:1 to root causes, so on-call engineers find the contested monitor, missing edge, or hot CAS word in minutes.
3. **Portability.** Code correct under the specified edges stays correct on x86 and ARM, under any JIT; code correct "by timing" breaks on the next platform or release.

## Where it shows up
- Thread pools and task pipelines: state analysis separates healthy idle (parked takes) from contention (identical BLOCKED stacks).
- Lazy initialization and configuration publishing: one volatile edge (or holder idiom) replaces fragile double-checking.
- Counters and metrics at scale: striping choices decide whether the hot path costs nanoseconds or serializes the fleet.
- Latency-sensitive paths: uncontended fast paths (~10-20ns scale) keep the common case cheap; measurement (PERFORMANCE.md) proves it per workload.

## Cost of ignorance (qualitative)
- A wrong-monitor or missing-edge race: weeks of flaky failures for a one-line fix.
- A contended single-word counter: linear retry burn that vanishes with striping.
- A `synchronized`-in-virtual-thread hot spot: carrier pinning that erases the scalability virtual threads were bought for.

## The one sentence for your team
Every RMW linearizes at the winning CAS; losers retry (lock-free: some thread progresses, yours may starve); functions passed to getAndUpdate re-execute on retry (side-effect-free only; expect repeated runs under contention); ABA needs identity freshness/stamps/marks; LongAdder.sum() is a fuzzy non-atomic snapshot; weakCompareAndSet is retry-loops-only; two atomics cannot transact (multi-variable invariants need a lock or single packed CAS).

## On-call playbook (this lab only)
- Exactness failure on a counter (shortfalls under load): check for `volatile++` or impure-loop first — replace with `AtomicLong`/`LongAdder` and watch totals go exact before any deeper theory.
- Duplicated effects with exact totals (double logs, double enqueues): side-effecting update function re-running per lost race — purify f, move effects post-commit, re-measure the ratio.
- Throughput cliff past a few writers on one atomic: single-word saturation (retries-per-success ≈ N) — stripe with `LongAdder` and confirm the retry collapse, not just the ops/s rise.
- Corruption with plausible values in pools/stacks: ABA suspect — log A->B->A identity transitions, then stamp/mark or fresh-allocate; values "looking right" is the ABA signature.
- Drift between live reports and reconciled totals: fuzzy `sum()` treated as exact — quiesce (`sumThenReset` at quiet points) for truth, keep live sums for dashboards.

## Review and test signal
- Reject `++`/`+=` on shared fields and effectful `getAndUpdate` lambdas on sight; demand the atomic/striped replacement plus the purity diff.
- Reject two-atomic "transactions" spanning one invariant; demand the lock or the packed-single-CAS design with the width budget stated.
- Reject one-shot `weakCompareAndSet` verdicts; demand plain `compareAndSet` or a retry loop with the spurious-failure comment.
- Require writer-count reasoning per counter (cold/hot/extremum/enforcement) in the PR — the counter pick without a writer count is a guess.

## Migration and scaling notes
- Volatile-counter migrations: expect shortfalls to vanish while uncontended latency holds — correctness first, then the crossover measurement picks AtomicLong vs LongAdder per counter.
- Metrics-at-scale rollouts: default hot paths to `LongAdder`, keep sequence issuance on `AtomicLong`, and wire `sum()`-vs-quiescent divergence checks where totals border enforcement.
- JDK upgrade re-measurement: re-lowering (intrinsic selection, cell growth policy) shifts knees — re-run the 1/2/8/32 sweep per release instead of carrying last year's crossover forward.
- Keep one retries-per-success capture per service runbook: the next "atomics are slow" claim meets the retry curve, and the next "striping is free" claim meets the memory bill.
