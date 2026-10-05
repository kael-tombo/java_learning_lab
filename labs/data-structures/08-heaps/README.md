# Heaps (Advanced Use) — Lab `08-heaps`
> Data structures track · Java 17 · Tailored to heaps.

## Why this matters
Heaps underpin streaming analytics, pathfinding, job scheduling, median maintenance. This lab builds
correct-by-construction intuition: representation → invariants → operations → costs.

## Learning objectives
- Explain the memory layout of Heaps (Advanced Use) (contiguous vs linked vs hashed vs tree-linked).
- Implement core ops from scratch: heapify-O(n), push, pop, meld.
- State Big-O for each op and the assumption behind it (amortized, expected, worst).
- Choose correctly vs alternatives using a complexity / locality / memory tradeoff table.
- Handle edge cases: empty, single element, full/capacity, duplicates, nulls, concurrent modification.

## Lab map
| File | Purpose |
|---|---|
| THEORY.md | operations, invariants, complexity table |
| EXERCISES.md | implement-from-scratch + traces + edge cases (Java templates) |
| QUIZ.md | 15 questions with answers |
| FLASHCARDS.md | ~60 recall rows |
| MATH_FOUNDATION.md | amortized analysis, load factor / height math |
| CODE_DEEP_DIVE.md | Java implementation + resize/hash/balance pitfalls |
| VISION.md | mastery path |
| MINI_PROJECT.md | implement + benchmark + visualize |
| REAL_WORLD_PROJECT.md | production use-case with metrics |

## How to work this lab
1. Read THEORY.md (30 min), take notes on invariants.
2. Do EXERCISES.md in order; run with `javac` / `jshell`.
3. Self-test with QUIZ.md and FLASHCARDS.md (spaced repetition).
4. Read MATH_FOUNDATION.md + CODE_DEEP_DIVE.md before MINI_PROJECT.md.
5. Finish with REAL_WORLD_PROJECT.md; record metrics.

## Success criteria
- [ ] All core ops implemented without looking, tests pass on edge cases.
- [ ] Can derive (not just recite) each complexity row.
- [ ] Benchmark shows expected scaling (e.g., linear vs log vs constant).
- [ ] Can name 2 production systems that use heaps and why.
