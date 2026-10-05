# Binary Search — Lab README
> Halve the search space: sorted-array mastery. Tailored to binary search (iterative/recursive).

## What's Inside
- `THEORY.md` — mechanics, invariants, complexity sketch.
- `EXERCISES.md` — implement + trace + edge cases.
- `QUIZ.md` — 15 questions with answers.
- `FLASHCARDS.md` — ~60 rapid-recall rows.
- `MATH_FOUNDATION.md` — recurrences, Master theorem, logs.
- `CODE_DEEP_DIVE.md` — annotated Java + pitfalls.
- `VISION.md` / `MINI_PROJECT.md` / `REAL_WORLD_PROJECT.md` — mastery path.
- `LEETCODE_SOLUTION.md` — existing; keep as reference.

## How to Use
1. Read `THEORY.md` (15 min).
2. Do `EXERCISES.md` Levels 1–2 with traces.
3. Self-test with `QUIZ.md` + `FLASHCARDS.md`.
4. Study `CODE_DEEP_DIVE.md`, then build `MINI_PROJECT.md`.
5. Finish with `REAL_WORLD_PROJECT.md` war-story.

## Core Idea
Binary search maintains `a[lo..hi)` with invariant `key ∈ a[lo..hi)` if present.
Probe `mid=(lo+hi)>>>1`; discard half each step. Requires sorted input.
Recurrence `T(n)=T(n/2)+O(1)` → `O(log n)` time, `O(1)` space iterative.

## Complexity Cheat-Sheet
| Case | Time | Space | Note |
|------|------|-------|------|
| Best | O(1) | O(1) | mid hit |
| Worst | O(log n) | O(1) | ~⌊log₂n⌋+1 probes |
| Average | O(log n) | O(1) | uniform key |

## Next Steps
See `VISION.md` for the path and `MINI_PROJECT.md` to benchmark vs linear search.
