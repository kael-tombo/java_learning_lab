# Why It Exists: Synchronized Internals

## The problem before the mechanism
Shared-memory threads interleave arbitrarily: without object monitors: monitorenter/monitorexit pairing, lock levels, and wait/notify protocol, every multi-threaded program is a pile of races — stale reads, torn updates, lost signals, deadlocks misdiagnosed. Developers needed a specified, implementable contract rather than folklore about "flushes" and "luck".

## What this mechanism contributes
- A precise vocabulary: object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit`.
- Specified operations: `synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout`.
- A verifiable implementation: `javap -c` (monitorenter + 2 monitorexit), HotSpot `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, JLS 17.1/17.4.
- The guarantee: Biased locking disabled by default in JDK 15 (JEP 374), removed in JDK 18, flag unrecognized on JDK 23; uncontended stack-locking fast path costs on the order of ~10-20ns; wait/notify require monitor ownership (else IllegalMonitorStateException) with while-loop re-check; static (Class-object) and instance (this) monitors are disjoint; monitors are reentrant per thread; unlock->lock is a happens-before edge.

## What it deliberately does not do
- It does not make all concurrent code correct — compound actions, multi-variable invariants, and cross-monitor assumptions stay the programmer's job (see COMMON_MISTAKES.md).
- It does not promise fairness, timing, or performance levels — only the semantics in THEORY.md.
- It does not replace higher-level tools (executors, concurrent collections, structured concurrency) for task management.

## The alternative and why it loses
Ad-hoc reasoning ("it worked in testing", "sleep fixes it", "one more null check") passes demos and fails under load, on ARM, or after a JIT upgrade. The specified mechanism fails loudly at review time instead of silently in production.

## Bottom line
Synchronized Internals exists so that ordering, exclusion, or atomicity claims can be checked against a written contract and its sources — not against machine behavior on one laptop.

## Before monitors: what passed for synchronization
- Early concurrent code leaned on timing (`sleep` to "let the other thread finish"), flag polling without edges, and single-threaded luck — all invisible in unit tests, all broken under load or on new hardware.
- Libraries could not compose: two "careful" modules sharing one field with no common guard corrupted each other, and neither module's tests showed it — the failure needed the interleaving only production supplied.
- Debugging was archaeology: without monitor addresses and BLOCKED tokens, a hang gave no artifact pointing at the contested invariant — dumps changed hangs from mysteries into holder hunts.

## Why the design pairs exclusion with conditions
- Mutual exclusion alone serializes but cannot coordinate: producers need somewhere to sleep until data arrives — the WaitSet plus `wait`/`notify` puts the sleep inside the exclusion so the predicate check and the sleep are atomic together.
- The ownership check (`IllegalMonitorStateException`) exists because condition operations without the lock cannot atomically test-and-sleep — the exception converts a race into a loud failure at the call site.
- Reentrancy exists because OO composition (super-calls, template methods, recursion) constantly re-enters: non-recursive monitors would deadlock the most ordinary call shapes, so the count-entries design pays a counter to keep composition working.

## Why the implementation keeps changing under a fixed contract
- The contract (paired enter/exit, reentrancy, ownership-checked conditions, same-monitor edge) is what programs are written against; stack locking, inflation/deflation, elision, and coarsening are how HotSpot keeps that contract cheap across hardware eras.
- Biased locking lived and died on measurements, not taste: single-thread-repeated-entry was common enough to optimize until it was not — JEP 374 documents the reversal with numbers.
- Virtual threads re-price but do not rewrite: pinning changes the cost of BLOCKED, not its meaning — the contract outlasts its third scheduling substrate.

## The alternative, priced
- Bare-flag coordination without monitors: every lost update and torn check costs a production incident measured in days — one guard line replaces all of it.
- `ReentrantLock` everywhere "for performance": hand-paired `lock/unlock` without `try/finally` leaks on throws, and library locks hide from elision/coarsening — pay the ceremony only where timeouts, interruption, fairness, or multiple conditions are needed.
