# Linear Searching — Lab README
> Scan-first search: correctness before cleverness. Tailored to linear search on unsorted arrays/lists.

## What's Inside
- `THEORY.md` — mechanics, invariants, complexity sketch.
- `EXERCISES.md` — implement + trace + edge cases.
- `QUIZ.md` — 15 questions with answers.
- `FLASHCARDS.md` — ~60 rapid-recall rows.
- `MATH_FOUNDATION.md` — counting, expectations, amortized view.
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
Linear search scans `a[0..n-1]` left→right, returning first `i` with `a[i]==key`.
Invariant: `key ∉ a[0..i-1]` before checking `i`. Terminates with found index or -1.
No preconditions on order; works on any `Iterable`. Cost is `Θ(n)` worst/average, `Θ(1)` best.

## Complexity Cheat-Sheet
| Case | Time | Space | Note |
|------|------|-------|------|
| Best | O(1) | O(1) | key at index 0 |
| Worst | O(n) | O(1) | full scan / absent |
| Average | O(n) | O(1) | ~n/2 probes uniform |

## Next Steps
See `VISION.md` for the problem-solving path and `MINI_PROJECT.md` to benchmark vs binary search.
