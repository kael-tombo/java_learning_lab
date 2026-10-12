# Why It Matters: Synchronized Internals

## Production consequences
1. **Outages.** Misreading object monitors: monitorenter/monitorexit pairing, lock levels, and wait/notify protocol causes hangs (lost notify, uninterruptible BLOCKED), corruption (unpublished construction, torn compound updates), and cascading latency (contended single CAS word, inflated monitors under load).
2. **Debuggability.** The same facts that prevent bugs diagnose them: `javap -c` (monitorenter + 2 monitorexit), HotSpot `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, JLS 17.1/17.4 tokens map 1:1 to root causes, so on-call engineers find the contested monitor, missing edge, or hot CAS word in minutes.
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
Biased locking disabled by default in JDK 15 (JEP 374), removed in JDK 18, flag unrecognized on JDK 23; uncontended stack-locking fast path costs on the order of ~10-20ns; wait/notify require monitor ownership (else IllegalMonitorStateException) with while-loop re-check; static (Class-object) and instance (this) monitors are disjoint; monitors are reentrant per thread; unlock->lock is a happens-before edge.

## On-call playbook (this lab only)
- `javap -c -p` first when "synchronized doesn't release" is claimed: the trio (one enter, two exits, exception table) settles it in seconds — release is compiler-generated.
- BLOCKED clusters: group by monitor address, find `- locked <0x...>` holder, read the holder's frame — the fix location is the holder's stack, never the waiters'.
- `WAITING (on object monitor)` with no notifier: search the guard for notify paths; absent notifier means convert to timed wait plus re-check immediately, then design the signal properly.
- Post-deploy latency step with flat CPU: suspect fresh inflation on a newly contended guard — JFR `jdk.JavaMonitorEnter` rates confirm before any code change.
- Suspected bias-era advice in a runbook: grep for `UseBiasedLocking`; any hit means the runbook predates JDK 18 and its lock-cost numbers are fiction.

## Review and test signal
- Reject `synchronized` on parameters, boxed values, interned strings, and `this` escaping to callers — demand the private-final-guard diff.
- Reject `if (cond) wait()` and bare `notify()` with multiple predicates — demand `while` plus `notifyAll` or a written single-condition proof.
- Require the static-vs-instance drawing for every class with both: two monitors means two exclusion domains, and the review must name which invariant each covers.
- Demand a contention test (multi-threaded increment/buffer run) wherever a new guard is introduced — uncontended tests cannot validate a contention mechanism.

## Migration and modernization notes
- Virtual threads (21+): audit request-path `synchronized` for carrier pinning through JDK 23; each pinned BLOCKED thread costs a carrier, so pinning guards are the first migration blockers.
- Prefer narrowing and splitting before mechanism swaps: most inflated monitors deflate permanently once the section shrinks or the guard splits — `ReentrantLock` is for API needs (timeout/interrupt/fairness), not for speed.
- Track elision/coarsening wins in JIT logs per release: JDK upgrades change escape-analysis reach, so yesterday's inflated guard may be today's removed lock — re-measure, don't assume stasis.
- Keep one executable `javap -c` capture per service in the runbook: when the next "locks are slow" claim arrives, the pairing output plus the cliff numbers end the debate with artifacts.
