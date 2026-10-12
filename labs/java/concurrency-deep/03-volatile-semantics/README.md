# Lab: Volatile Semantics
Topic: the Java Memory Model happens-before edges for volatile fields: visibility, ordering, and limits.

## What you will learn
1. Name the real structures involved: volatile field access (JLS 17.4.5), program-order/monitor/lifecycle edges, StoreLoad fences (`xchg`+`lock` on x86, `dmb ish` on ARMv8), safe-publication piggybacking, `VarHandle` access modes.
2. Use the real APIs: `volatile` field read/write, double-checked locking with volatile, `AtomicIntegerArray`/VarHandle array-element volatile access, `VarHandle.getAcquire/setRelease/getOpaque` (contrast).
3. Read primary sources: JLS 17.4 (happens-before), 17.5 (final-field safety), 17.7 (word tearing), JSR-133 (2004 memory-model rewrite), `VarHandle.java` (Java 9).
4. Key fact: Volatile gives visibility + access atomicity (incl. long/double) but NOT compound-action atomicity (volatile++ races: read-modify-write in three steps); DCL is correct only with volatile (or holder idiom/enum singleton); transitivity A->B->C chains edges; volatile reads are near-free on x86 (TSO) while writes need a fence, both directions need fences on ARM (qualitative only); volatile arrays cover the reference, never the elements.
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
- Start with THEORY.md edge rules, then CODE_DEEP_DIVE.md snippet 1 (stale spin) — the hoisted-read shock before the formalism.
- Run snippet 2 (`volatile++` losses) before reading any counter advice; the shortfall numbers motivate AtomicLong/LongAdder better than prose.
- Attempt EXERCISES.md 6-8 only after 1-5 pass; transitivity and VarHandle modes assume you can already draw the basic piggyback chain.

## Tool commands you will reuse
- `javap -c -p` to exhibit the three bytecode steps inside `volatile++` (`getfield`/`iadd`/`putfield`) — the race made visible as instructions.
- `jshell` plus thread harnesses for stress loops; `CountDownLatch` gates to jitter starts so races cannot hide behind staggered launches.
- JMH read-vs-write split benchmarks per architecture; never one blended "volatile cost" number and never one architecture's table applied to another.
