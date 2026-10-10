# TreeMap / TreeSet — Lab Overview

Structure under study: `java.util.TreeMap / java.util.TreeSet` (source: `java.util.TreeMap`).
Storage model: red-black tree of Entry nodes (TreeSet = TreeMap<E,Boolean> with PRESENT sentinel).

## What this lab covers
- color literal: RED=false, BLACK=true; height bound <= 2*log2(n+1).
- identity is compareTo==0 (or comparator.compare==0), NOT equals().
- compare(key,key) null/type pre-check: addEntryToEmptyMap calls it on empty map first.
- live bounded views: subMap/headMap/tailMap (+ Navigable variants); descendingMap reversed view.
- iteration ascending via on-the-fly successor links; fail-fast via modCount.

## Key APIs
- Core ops: getEntry/put/fixAfterInsertion/fixAfterDeletion/getSuccessor.
- Views/iteration: NavigableSubMap view classes.
- Concurrency note: unsynchronized; null keys rejected under natural ordering, allowed only if comparator handles them.

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
