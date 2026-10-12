# Why It Matters: Thread Lifecycle

## Production consequences
1. **Outages.** Misreading the six `Thread.State` values and the transitions between them causes hangs (lost notify, uninterruptible BLOCKED), corruption (unpublished construction, torn compound updates), and cascading latency (contended single CAS word, inflated monitors under load).
2. **Debuggability.** The same facts that prevent bugs diagnose them: `java.base/java/lang/Thread.java` (State enum, start/join/sleep), HotSpot `thread.cpp`/`osthread`, `jstack`/`jcmd Thread.print` output tokens map 1:1 to root causes, so on-call engineers find the contested monitor, missing edge, or hot CAS word in minutes.
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
BLOCKED = synchronized-monitor contention only; ReentrantLock contention shows as WAITING (parking); RUNNABLE covers running+ready; getState() is monitoring-only; start() is single-use (second call throws IllegalThreadStateException); virtual threads report the same six states but synchronized pins the carrier through JDK 23 (JEP 444).

## On-call playbook (this lab only)
- Deadlock footer first (`Found one Java-level deadlock`): the JVM names the cycle — start there, not at thread 1.
- No footer: cluster by identical stack, split BLOCKED (find `- locked <0x...>` holder) from WAITING-parking (find the missing unpark/notify), and diff two dumps 5s apart for stuck-vs-progressing.
- High CPU plus RUNNABLE spins: profiler (async-profiler/JFR), not more dumps — dumps cannot separate running from ready.
- Lingering JVM after deploy stop: list non-daemon survivors (`getAllStackTraces` filter) and give each a `shutdown`/`awaitTermination` owner.
- Log the interrupt-status value (cleared vs preserved) in every cancellation incident report — the contract decides whether the code or the caller is wrong.

## Interview and review signal
- Ask candidates to predict the dump token for `ReentrantLock` contention vs `synchronized` contention — the split tests subsystem thinking, not memorization.
- In review, reject `getState()` branches and `sleep`-based waits on sight; accept them only rewritten as join/latch/future edges with a stated wake condition.
- Require every `catch (InterruptedException)` to restore or propagate — swallowed status is a shutdown bug with a timer on it.
- Ask what wakes each TIMED_WAITING thread on the team-owned paths (event, expiry, or both) — "timeout" as the only answer is a design smell.

## Migration note (virtual threads, 21+)
- Same six states means existing alerts keep firing; retune thresholds instead: thousands of WAITING is backlog, thousands of BLOCKED is pinning — different runbooks.
- Audit `synchronized` on request paths before migrating: each pinned carrier at scale erases the thread-count win virtual threads were bought for.
- Count pinning with `jdk.VirtualThreadPinned` per deploy; trend it like a contention metric, not a one-off check.
- Keep one platform-thread pool for the paths that must pin (native calls, unavoidable monitors) and measure its queue separately.
