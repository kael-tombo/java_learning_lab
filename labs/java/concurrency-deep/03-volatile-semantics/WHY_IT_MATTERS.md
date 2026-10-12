# Why It Matters: Volatile Semantics

## Production consequences
1. **Outages.** Misreading the Java Memory Model happens-before edges for volatile fields: visibility, ordering, and limits causes hangs (lost notify, uninterruptible BLOCKED), corruption (unpublished construction, torn compound updates), and cascading latency (contended single CAS word, inflated monitors under load).
2. **Debuggability.** The same facts that prevent bugs diagnose them: JLS 17.4 (happens-before), 17.5 (final-field safety), 17.7 (word tearing), JSR-133 (2004 memory-model rewrite), `VarHandle.java` (Java 9) tokens map 1:1 to root causes, so on-call engineers find the contested monitor, missing edge, or hot CAS word in minutes.
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
Volatile gives visibility + access atomicity (incl. long/double) but NOT compound-action atomicity (volatile++ races: read-modify-write in three steps); DCL is correct only with volatile (or holder idiom/enum singleton); transitivity A->B->C chains edges; volatile reads are near-free on x86 (TSO) while writes need a fence, both directions need fences on ARM (qualitative only); volatile arrays cover the reference, never the elements.

## On-call playbook (this lab only)
- Stale flag (reader never sees update): draw the four-hop chain, find the missing hop (usually the keyword itself), add the edge — never a sleep or retry.
- Half-constructed object via lazy init: check the DCL keyword first; absent `volatile` (and no holder/enum) is the verdict before any deeper debugging.
- Lost increments under load: `volatile++` is the suspect — replace with `AtomicLong`/`LongAdder` and watch the shortfall vanish; the "performance" of volatile counters was the race.
- Element-visibility failure behind `volatile ref[]`: per-element semantics missing — swap to `AtomicIntegerArray`/VarHandle elements or republish-then-swap the whole reference.
- ARM-only ordering failure: missing explicit edge papered over by x86 TSO — add the volatile pair and re-run on both architectures.

## Review and test signal
- Reject cross-thread plain flags on sight; demand the volatile/atomic/interrupt edge with the chain drawn in the PR.
- Reject `++`/`+=`/check-then-act on volatile fields; demand the AtomicLong/LongAdder/lock replacement matched to contention level.
- Require the DCL verdict per lazy singleton (volatile-DCL vs holder vs enum) stated in the review — "lazy" without a verdict is a finding.
- Demand stress loops (jittered starts, thousands of iterations) for publication harnesses — single-run greens are inadmissible evidence for races.

## Migration and platform notes
- x86 to ARM ports: re-run every visibility-sensitive benchmark and re-derive "volatile is cheap" assumptions — reads stop being free, writes get dearer; batching payloads per publish matters more off x86.
- Counter migrations off volatile: expect exactness to appear (shortfalls vanish) while uncontended latency stays flat — the win is correctness first, striping second.
- VarHandle descents: require the profiler line and the mode table in the same PR — acquire/release without evidence is premature fencing-arbitrage.
- Keep one StaleSpin capture per service runbook: the next "flag updates are instant" claim meets plainSpins-vs-volSpins numbers, not opinions.
