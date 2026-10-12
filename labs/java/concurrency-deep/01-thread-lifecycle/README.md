# Lab: Thread Lifecycle
Topic: the six `Thread.State` values and the transitions between them.

## What you will learn
1. Name the real structures involved: `java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token.
2. Use the real APIs: `start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()`.
3. Read primary sources: `java.base/java/lang/Thread.java` (State enum, start/join/sleep), HotSpot `thread.cpp`/`osthread`, `jstack`/`jcmd Thread.print` output.
4. Key fact: BLOCKED = synchronized-monitor contention only; ReentrantLock contention shows as WAITING (parking); RUNNABLE covers running+ready; getState() is monitoring-only; start() is single-use (second call throws IllegalThreadStateException); virtual threads report the same six states but synchronized pins the carrier through JDK 23 (JEP 444).
5. Run every snippet in this lab with `jshell` or `javac`/`java` (JDK 17+; JDK 21+ for virtual-thread notes) and confirm the stated behavior.

## How this lab is organized
- `THEORY.md` — concepts and invariants (source-verified ground truth).
- `CODE_DEEP_DIVE.md` — annotated source/bytecode walkthroughs.
- `HOW_IT_WORKS.md`, `INTERNALS.md`, `ARCHITECTURE.md` — mechanism at three zoom levels.
- `STEP_BY_STEP.md`, `VISUAL_GUIDE.md`, `MENTAL_MODELS.md` — guided paths through the same facts.
- `EXERCISES.md`, `QUIZ.md`, `FLASHCARDS.md` — practice and recall.
- `COMMON_MISTAKES.md`, `DEBUGGING.md`, `PERFORMANCE.md`, `SECURITY.md` — production skills.
- `HISTORY.md`, `REFERENCES.md`, `WHY_IT_EXISTS.md`, `WHY_IT_MATTERS.md`, `REFLECTION.md`, `REFACTORING.md`, `MATH_FOUNDATION.md` — context and depth.

## Prerequisites
- Java 17+ installed (`java -version`); `javap -c` available for bytecode checks.
- Comfort with `Thread`, `synchronized`, and basic `java.util.concurrent` usage.
- A willingness to read thread dumps and JLS sections cited in REFERENCES.md.

## Definition of done
- You can state the lab's key fact (item 4 above) without notes and point to the source that proves it.
- All EXERCISES.md tasks run and produce the predicted output.
- You score 7/8+ on QUIZ.md and clear all FLASHCARDS.md without peeking.

## Reading order
- Start with THEORY.md invariants 1-5, then CODE_DEEP_DIVE.md snippet 1 (all six states forced) — vocabulary before diagnosis.
- Read DEBUGGING.md with a live `jstack` of your own process open; match each token line to a real thread.
- Attempt EXERCISES.md 6-8 only after 1-5 pass; the later tasks assume you can already force every state on demand.

## Tool commands you will reuse
- `jstack <pid> > dump.txt` and `jcmd <pid> Thread.print` for captures; `javap -c -p` for the bytecode pairing proved in neighboring labs.
- `jcmd <pid> Thread.print -l` adds lock-owner lines; JFR `jdk.JavaMonitorEnter` adds timestamped contention events beyond text snapshots.
- JFR `jdk.VirtualThreadPinned` (21+) for pinning evidence when virtual-thread dumps show unexpected BLOCKED clusters.
