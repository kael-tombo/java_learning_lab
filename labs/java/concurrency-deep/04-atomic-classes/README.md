# Lab: Atomic Classes
Topic: lock-free read-modify-write via CAS: AtomicX, stamped references, and striped counters.

## What you will learn
1. Name the real structures involved: `AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding.
2. Use the real APIs: `compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder`.
3. Read primary sources: `java.base/java/util/concurrent/atomic/AtomicInteger.java` (JDK 23), `Striped64.java` class javadoc, `VarHandle` specs, JSR-166 (2004, Doug Lea).
4. Key fact: Every RMW linearizes at the winning CAS; losers retry (lock-free: some thread progresses, yours may starve); functions passed to getAndUpdate re-execute on retry (side-effect-free only; expect repeated runs under contention); ABA needs identity freshness/stamps/marks; LongAdder.sum() is a fuzzy non-atomic snapshot; weakCompareAndSet is retry-loops-only; two atomics cannot transact (multi-variable invariants need a lock or single packed CAS).
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
- Start with THEORY.md CAS-loop pattern, then CODE_DEEP_DIVE.md snippet 1 (hand loop, exact totals) — the commit-or-retry contract before the API catalog.
- Run snippet 2 (rerun counting) before reading any `getAndUpdate` advice; the ~3x applications number motivates purity better than prose.
- Attempt EXERCISES.md 6-8 only after 1-5 pass; false-sharing, packing, and weak-CAS audits assume you can already write a correct hand loop.

## Tool commands you will reuse
- Plain `javac`/`java` harnesses with failure counters for retries-per-success; JMH writer sweeps (1/2/8/32) for the crossover knee.
- `-XX:+PrintFieldLayout` for counter layout plus perf counters for coherence traffic before any hand padding.
- `jshell` for ABA sketches (`AtomicReference` vs `AtomicStampedReference` verdicts) — three-line demos that settle stamp debates instantly.
