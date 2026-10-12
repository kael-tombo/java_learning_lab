# Step by Step: Thread Lifecycle

## Setup
- JDK 17+ (`java -version`). JDK 21+ for virtual-thread steps.
- Work inside this lab directory; compile with `javac -g` so `javap -c` line numbers align.

## Step 1 — Name the operands
Write down the exact entities for the six `Thread.State` values and the transitions between them: which thread(s), which object/field, which API from `start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()`. If you cannot name them, stop and re-read THEORY.md.

## Step 2 — Run the minimal probe
```java
// jshell probe: shows the core API in 5 lines
Thread t = new Thread(() -> { try { Thread.sleep(5000); } catch (InterruptedException e) {} });
System.out.println(t.getState()); // NEW
t.start(); System.out.println(t.getState()); // RUNNABLE
t.join(100); System.out.println(t.getState()); // TIMED_WAITING (sleeping)
```
Record the output verbatim.

## Step 3 — Inspect the mechanism
```
javap -c -p YourClass.class
jstack <pid> | grep -A6 "your-thread-name"
```
Match each line against `java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token and `java.base/java/lang/Thread.java` (State enum, start/join/sleep), HotSpot `thread.cpp`/`osthread`, `jstack`/`jcmd Thread.print` output.

## Step 4 — Add contention or interleaving
Run two threads/tasks against the same operand from Step 1. Predict the outcome using MATH_FOUNDATION.md edges, then run and compare. If the run disagrees, your edge analysis is wrong — fix the analysis, not the data.

## Step 5 — Break it on purpose
Apply one bug from COMMON_MISTAKES.md (wrong monitor, missing volatile, side-effecting update function, one-shot weak CAS). Observe the failure, then revert.

## Step 6 — State the invariant aloud
Without notes: BLOCKED = synchronized-monitor contention only; ReentrantLock contention shows as WAITING (parking); RUNNABLE covers running+ready; getState() is monitoring-only; start() is single-use (second call throws IllegalThreadStateException); virtual threads report the same six states but synchronized pins the carrier through JDK 23 (JEP 444).

## Checklist
- [ ] Probe output recorded and explained. [ ] Bytecode/dump lines mapped. [ ] Two-thread prediction matched. [ ] One deliberate bug reproduced and fixed.
