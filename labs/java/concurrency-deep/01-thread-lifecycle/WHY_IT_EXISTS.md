# Why It Exists: Thread Lifecycle

## The problem before the mechanism
Shared-memory threads interleave arbitrarily: without the six `Thread.State` values and the transitions between them, every multi-threaded program is a pile of races — stale reads, torn updates, lost signals, deadlocks misdiagnosed. Developers needed a specified, implementable contract rather than folklore about "flushes" and "luck".

## What this mechanism contributes
- A precise vocabulary: `java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token.
- Specified operations: `start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()`.
- A verifiable implementation: `java.base/java/lang/Thread.java` (State enum, start/join/sleep), HotSpot `thread.cpp`/`osthread`, `jstack`/`jcmd Thread.print` output.
- The guarantee: BLOCKED = synchronized-monitor contention only; ReentrantLock contention shows as WAITING (parking); RUNNABLE covers running+ready; getState() is monitoring-only; start() is single-use (second call throws IllegalThreadStateException); virtual threads report the same six states but synchronized pins the carrier through JDK 23 (JEP 444).

## What it deliberately does not do
- It does not make all concurrent code correct — compound actions, multi-variable invariants, and cross-monitor assumptions stay the programmer's job (see COMMON_MISTAKES.md).
- It does not promise fairness, timing, or performance levels — only the semantics in THEORY.md.
- It does not replace higher-level tools (executors, concurrent collections, structured concurrency) for task management.

## The alternative and why it loses
Ad-hoc reasoning ("it worked in testing", "sleep fixes it", "one more null check") passes demos and fails under load, on ARM, or after a JIT upgrade. The specified mechanism fails loudly at review time instead of silently in production.

## Bottom line
Thread Lifecycle exists so that ordering, exclusion, or atomicity claims can be checked against a written contract and its sources — not against machine behavior on one laptop.

## How the contract is enforced (not just documented)
- `start()` single-use is enforced by a state check inside the JDK that throws `IllegalThreadStateException` — the pairing is code, not convention.
- Monitor entry/exit pairing is compiler-generated (`monitorenter` plus normal and exception-table `monitorexit`), so even throwing bodies release — see lab 02's `javap -c` proof.
- Interrupt contracts are enforced per API (`sleep` throws-and-clears, `park` preserves): the enforcement lives in the method, which is why one `interrupt()` call has three outcomes.
- Dump tokens are printed by the JVM from the same state machine the scheduler uses — `jstack` output and `getState()` cannot disagree about the vocabulary, only about the sampling instant.

## What virtual threads changed (and did not)
- Changed: parking a virtual thread unmounts its carrier, so million-thread WAITING backlogs cost memory but not OS threads — capacity-planning math moved.
- Did not change: the six reported values, the BLOCKED-means-monitor rule, or the monitoring-only status of `getState()` — every pre-21 dump skill still applies.
- The pinning footnote (`synchronized` holds the carrier through JDK 23) is a scheduler limitation with a version range, not a new semantic — track the JDK release notes, not folklore.

## The alternative, priced
- `sleep`-and-retry coordination: latency floor equals the poll interval, plus wake storms when many threads poll one flag — latches cost one signal total.
- `getState()` polling loops: burn CPU in RUNNABLE while learning nothing a latch would not deliver — sampling replaces signaling at full price and zero rigor.
- Restarting threads instead of pooling: `start()` single-use forces allocation churn plus `IllegalThreadStateException` landmines — executors amortize both.
- Timing-based "it woke up in testing" confidence: passes on an idle laptop, fails under load or on another OS — events and expiries are the only portable wake reasons.
