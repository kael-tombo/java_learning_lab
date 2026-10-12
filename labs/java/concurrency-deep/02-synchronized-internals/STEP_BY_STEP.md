# Step by Step: Synchronized Internals

## Setup
- JDK 17+ (`java -version`). JDK 21+ for virtual-thread steps.
- Work inside this lab directory; compile with `javac -g` so `javap -c` line numbers align.

## Step 1 — Name the operands
Write down the exact entities for object monitors: monitorenter/monitorexit pairing, lock levels, and wait/notify protocol: which thread(s), which object/field, which API from `synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout`. If you cannot name them, stop and re-read THEORY.md.

## Step 2 — Run the minimal probe
```java
// jshell probe: shows the core API in 5 lines
Object o = new Object();
synchronized (o) { System.out.println("holding " + o); }
// javap -c shows monitorenter + two monitorexit paths
```
Record the output verbatim.

## Step 3 — Inspect the mechanism
```
javap -c -p YourClass.class
jstack <pid> | grep -A6 "your-thread-name"
```
Match each line against object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit` and `javap -c` (monitorenter + 2 monitorexit), HotSpot `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, JLS 17.1/17.4.

## Step 4 — Add contention or interleaving
Run two threads/tasks against the same operand from Step 1. Predict the outcome using MATH_FOUNDATION.md edges, then run and compare. If the run disagrees, your edge analysis is wrong — fix the analysis, not the data.

## Step 5 — Break it on purpose
Apply one bug from COMMON_MISTAKES.md (wrong monitor, missing volatile, side-effecting update function, one-shot weak CAS). Observe the failure, then revert.

## Step 6 — State the invariant aloud
Without notes: Biased locking disabled by default in JDK 15 (JEP 374), removed in JDK 18, flag unrecognized on JDK 23; uncontended stack-locking fast path costs on the order of ~10-20ns; wait/notify require monitor ownership (else IllegalMonitorStateException) with while-loop re-check; static (Class-object) and instance (this) monitors are disjoint; monitors are reentrant per thread; unlock->lock is a happens-before edge.

## Checklist
- [ ] Probe output recorded and explained. [ ] Bytecode/dump lines mapped. [ ] Two-thread prediction matched. [ ] One deliberate bug reproduced and fixed.
