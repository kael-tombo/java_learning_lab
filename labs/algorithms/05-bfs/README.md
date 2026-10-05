# BFS — Lab README
> Level-order graph exploration. Tailored to breadth-first search with a FIFO queue.

## What's Inside
- `THEORY.md` — mechanics, invariants, complexity sketch.
- `EXERCISES.md` — implement + trace + edge cases.
- `QUIZ.md` — 15 questions with answers.
- `FLASHCARDS.md` — ~60 rapid-recall rows.
- `MATH_FOUNDATION.md` — queue analysis, `O(V+E)` proof.
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
BFS enqueues source, marks visited, expands frontier level by level.
Invariant: queue holds frontier in nondecreasing distance; `dist[]` is final when dequeued.
Unweighted shortest paths. `O(V+E)` time, `O(V)` space. Needs visited set to avoid requeue.

## Complexity Cheat-Sheet
| Case | Time | Space | Note |
|------|------|-------|------|
| Adj list | O(V+E) | O(V) | standard |
| Adj matrix | O(V²) | O(V) | dense scan |
| Early exit | O(V+E) worst | O(V) | target search |

## Next Steps
See `VISION.md` for the path and `MINI_PROJECT.md` to visualize frontiers.
