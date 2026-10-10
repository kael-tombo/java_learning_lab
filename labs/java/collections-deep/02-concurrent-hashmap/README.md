# ConcurrentHashMap — Lab Overview

Structure under study: `java.util.concurrent.ConcurrentHashMap` (source: `java.util.concurrent.ConcurrentHashMap`).
Storage model: lock-striped hash table: buckets (not the map) are the locking unit.

## What this lab covers
- putVal rejects null key/value with NullPointerException.
- spread() masks high bits (HASH_BITS 0x7fffffff) so hash is non-negative.
- sizing via sizeCtl; initTable lazy; resize doubles, cooperative via ForwardingNode (MOVED) + helpTransfer.
- counting via baseCount + CounterCell[] (LongAdder-style); sumCount() snapshot.
- writes lock only bucket head synchronized(f); empty-bin insert is pure CAS (casTabAt).

## Key APIs
- Core ops: putVal/merge/compute/putIfAbsent.
- Views/iteration: weakly-consistent iterators (never throw CME).
- Concurrency note: volatile tabAt/casTabAt reads; Node.val/next volatile.

## File map
- THEORY.md / CODE_DEEP_DIVE.md: source-verified ground truth (read first).
- HOW_IT_WORKS.md, INTERNALS.md, STEP_BY_STEP.md, VISUAL_GUIDE.md: mechanics.
- MATH_FOUNDATION.md, PERFORMANCE.md, ARCHITECTURE.md: cost model.
- EXERCISES.md, QUIZ.md, FLASHCARDS.md: self-test.
- HISTORY.md, REFERENCES.md, WHY_IT_EXISTS.md, WHY_IT_MATTERS.md: context.
- COMMON_MISTAKES.md, DEBUGGING.md, REFACTORING.md, SECURITY.md, REFLECTION.md: practice.

## Ground rules
- Capacity/ordering/cost claims here match THEORY.md; where they differ, THEORY.md wins.
- All snippets target JDK 17+ unless noted.
- Start with HOW_IT_WORKS.md, then INTERNALS.md, then the JMH drills in EXERCISES.md.
- Start with HOW_IT_WORKS.md, then INTERNALS.md, then the drills in EXERCISES.md.
