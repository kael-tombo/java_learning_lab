# ArrayList Deep Dive — Lab Overview

Structure under study: `java.util.ArrayList` (source: `java.util.ArrayList`).
Storage model: resizable array: Object[] elementData + size, contiguous storage.

## What this lab covers
- growth 1.5x: ArraysSupport.newLength(oldCap, minGrowth, oldCap>>1); copy via Arrays.copyOf.
- lazy default: new ArrayList<>() allocates nothing; first add -> DEFAULT_CAPACITY 10.
- two empty singletons: DEFAULTCAPACITY_EMPTY_ELEMENTDATA (grows to 10) vs EMPTY_ELEMENTDATA (grows exact).
- fastRemove nulls the freed slot (elementData[--size]=null) to avoid leaks.
- set(i,e) replaces without modCount++; structural ops (add/remove/grow) increment it.

## Key APIs
- Core ops: add/get/set/remove/ensureCapacity/trimToSize.
- Views/iteration: SubList view + fail-fast Itr/ListItr.
- Concurrency note: unsynchronized; use Collections.synchronizedList (manual sync for iteration) or CopyOnWriteArrayList.

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
