# Step by Step: Volatile Semantics

## Setup
- JDK 17+ (`java -version`). JDK 21+ for virtual-thread steps.
- Work inside this lab directory; compile with `javac -g` so `javap -c` line numbers align.

## Step 1 — Name the operands
Write down the exact entities for the Java Memory Model happens-before edges for volatile fields: visibility, ordering, and limits: which thread(s), which object/field, which API from `volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast). If you cannot name them, stop and re-read THEORY.md.

## Step 2 — Run the minimal probe
```java
// jshell probe: shows the core API in 5 lines
class Box { volatile boolean ready; int data; }
// writer: box.data = 42; box.ready = true;
// reader: if (box.ready) System.out.println(box.data); // must see 42
```
Record the output verbatim.

## Step 3 — Inspect the mechanism
```
javap -c -p YourClass.class
jstack <pid> | grep -A6 "your-thread-name"
```
Match each line against volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes and JLS 17.4 (happens-before), 17.5 (final-field safety), 17.7 (word tearing), JSR-133 (2004 memory-model rewrite), `VarHandle.java` (Java 9).

## Step 4 — Add contention or interleaving
Run two threads/tasks against the same operand from Step 1. Predict the outcome using MATH_FOUNDATION.md edges, then run and compare. If the run disagrees, your edge analysis is wrong — fix the analysis, not the data.

## Step 5 — Break it on purpose
Apply one bug from COMMON_MISTAKES.md (wrong monitor, missing volatile, side-effecting update function, one-shot weak CAS). Observe the failure, then revert.

## Step 6 — State the invariant aloud
Without notes: Volatile gives visibility + access atomicity (incl. long/double) but NOT compound-action atomicity (volatile++ races: read-modify-write in three steps); DCL is correct only with volatile (or holder idiom/enum singleton); transitivity A->B->C chains edges; volatile reads are near-free on x86 (TSO) while writes need a fence, both directions need fences on ARM (qualitative only); volatile arrays cover the reference, never the elements.

## Checklist
- [ ] Probe output recorded and explained. [ ] Bytecode/dump lines mapped. [ ] Two-thread prediction matched. [ ] One deliberate bug reproduced and fixed.
