# Lab: Synchronized Internals
Topic: object monitors: monitorenter/monitorexit pairing, lock levels, and wait/notify protocol.

## What you will learn
1. Name the real structures involved: object mark word (64-bit header: hash, GC age, lock bits), stack lock records (displaced mark word), inflated `ObjectMonitor` (`_cxq`, `_EntryList`, `_WaitSet`), exception-table second `monitorexit`.
2. Use the real APIs: `synchronized` blocks/methods, `Object.wait()/wait(t)/notify()/notifyAll()`, `ReentrantLock.lockInterruptibly/tryLock` (contrast), `-XX:+PrintFieldLayout`.
3. Read primary sources: `javap -c` (monitorenter + 2 monitorexit), HotSpot `objectMonitor.cpp`, `synchronizer.cpp`, `markWord.hpp`, JLS 17.1/17.4.
4. Key fact: Biased locking disabled by default in JDK 15 (JEP 374), removed in JDK 18, flag unrecognized on JDK 23; uncontended stack-locking fast path costs on the order of ~10-20ns; wait/notify require monitor ownership (else IllegalMonitorStateException) with while-loop re-check; static (Class-object) and instance (this) monitors are disjoint; monitors are reentrant per thread; unlock->lock is a happens-before edge.
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
- Start with THEORY.md lock levels, then CODE_DEEP_DIVE.md snippet 1 (`javap -c` pairing) — the compiler proof before the contention stories.
- Run snippet 4 (wrong-monitor overlap) before reading any wait/notify material; monitor identity is the prerequisite for everything else.
- Attempt EXERCISES.md 6-8 only after 1-5 pass; bytecode reading and cliff measurement assume you can already force BLOCKED on demand.

## Tool commands you will reuse
- `javap -c -p` on your own classes for the monitorenter/monitorexit pairing; `jstack <pid>` filtered to BLOCKED plus holder addresses for contention.
- `-XX:+PrintCompilation -XX:+LogCompilation` for elision/coarsening evidence; JFR `jdk.JavaMonitorEnter` for timestamped contention rates.
- `jcmd <pid> Thread.print -l` for lock-owner lines when `jstack -l` output needs a scriptable twin.
