# DFS — Lab README
> Depth-first exploration with recursion/stack. Tailored to DFS (pre/in/post, cycle detection).

## What's Inside
- `THEORY.md` — mechanics, invariants, complexity sketch.
- `EXERCISES.md` — implement + trace + edge cases.
- `QUIZ.md` — 15 questions with answers.
- `FLASHCARDS.md` — ~60 rapid-recall rows.
- `MATH_FOUNDATION.md` — recursion depth, `O(V+E)` proof.
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
DFS dives along one path, backtracks on dead end, using recursion or explicit stack.
Invariant: nodes on stack form current path; colors white/gray/black prevent repeats.
Yields forests, discovery/finish times, topo order on DAGs. `O(V+E)` time, `O(V)` space.

## Complexity Cheat-Sheet
| Case | Time | Space | Note |
|------|------|-------|------|
| Adj list | O(V+E) | O(V) | standard |
| Adj matrix | O(V²) | O(V) | dense |
| Iterative | O(V+E) | O(V) | explicit stack |

## Next Steps
See `VISION.md` for the path and `MINI_PROJECT.md` to compare DFS vs BFS.
