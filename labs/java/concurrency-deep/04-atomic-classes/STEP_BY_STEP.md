# Step by Step: Atomic Classes

## Setup
- JDK 17+ (`java -version`). JDK 21+ for virtual-thread steps.
- Work inside this lab directory; compile with `javac -g` so `javap -c` line numbers align.

## Step 1 — Name the operands
Write down the exact entities for lock-free read-modify-write via CAS: AtomicX, stamped references, and striped counters: which thread(s), which object/field, which API from `compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder`. If you cannot name them, stop and re-read THEORY.md.

## Step 2 — Run the minimal probe
```java
// jshell probe: shows the core API in 5 lines
var c = new java.util.concurrent.atomic.AtomicInteger(0);
System.out.println(c.incrementAndGet()); // 1: one lock cmpxchg
System.out.println(c.getAndUpdate(x -> x * 2)); // CAS loop, pure function
```
Record the output verbatim.

## Step 3 — Inspect the mechanism
```
javap -c -p YourClass.class
jstack <pid> | grep -A6 "your-thread-name"
```
Match each line against `AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding and `java.base/java/util/concurrent/atomic/AtomicInteger.java` (JDK 23), `Striped64.java` class javadoc, `VarHandle` specs, JSR-166 (2004, Doug Lea).

## Step 4 — Add contention or interleaving
Run two threads/tasks against the same operand from Step 1. Predict the outcome using MATH_FOUNDATION.md edges, then run and compare. If the run disagrees, your edge analysis is wrong — fix the analysis, not the data.

## Step 5 — Break it on purpose
Apply one bug from COMMON_MISTAKES.md (wrong monitor, missing volatile, side-effecting update function, one-shot weak CAS). Observe the failure, then revert.

## Step 6 — State the invariant aloud
Without notes: Every RMW linearizes at the winning CAS; losers retry (lock-free: some thread progresses, yours may starve); functions passed to getAndUpdate re-execute on retry (side-effect-free only; expect repeated runs under contention); ABA needs identity freshness/stamps/marks; LongAdder.sum() is a fuzzy non-atomic snapshot; weakCompareAndSet is retry-loops-only; two atomics cannot transact (multi-variable invariants need a lock or single packed CAS).

## Checklist
- [ ] Probe output recorded and explained. [ ] Bytecode/dump lines mapped. [ ] Two-thread prediction matched. [ ] One deliberate bug reproduced and fixed.
