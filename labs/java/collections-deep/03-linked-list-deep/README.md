# LinkedList Deep Dive — Lab Overview

Structure under study: `java.util.LinkedList` (source: `java.util.LinkedList`).
Storage model: doubly-linked list of Node{item,next,prev} with first/last handles and size.

## What this lab covers
- node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last.
- Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs).
- no sentinel node: size==0 means first==last==null, every mutation branches on null.
- fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal.
- implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst.

## Key APIs
- Core ops: linkFirst/linkLast/linkBefore + unlink/unlinkFirst/unlinkLast.
- Views/iteration: ListItr / DescendingIterator.
- Concurrency note: unsynchronized; structural change must flow through link/unlink (size+modCount).

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
