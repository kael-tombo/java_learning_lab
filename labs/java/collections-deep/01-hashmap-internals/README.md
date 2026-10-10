# HashMap Internals — Lab Overview

Structure under study: `java.util.HashMap` (source: `java.util.HashMap`).
Storage model: hash table with separate chaining over a Node[] table.

## What this lab covers
- spreader `h ^ (h >>> 16)` folds high bits down.
- TREEIFY_THRESHOLD=8, UNTREEIFY_THRESHOLD=6, MIN_TREEIFY_CAPACITY=64.
- resize doubles capacity (power of two); node stays at i or moves to i+oldCap via (e.hash & oldCap)==0.
- null key allowed once, hash 0, bucket 0.
- default capacity 16, load factor 0.75.

## Key APIs
- Core ops: put(k,v)/get(k)/remove(k).
- Views/iteration: entrySet().iterator() EntryIterator.
- Concurrency note: fail-fast via modCount, ConcurrentModificationException.

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
