# Bellman-Ford + Floyd-Warshall — Lab README
> Shortest paths with negatives + all-pairs. Tailored to Bellman-Ford and Floyd-Warshall.

## What's Inside
- `THEORY.md` — mechanics, invariants, complexity sketch.
- `EXERCISES.md` — implement + trace + edge cases.
- `QUIZ.md` — 15 questions with answers.
- `FLASHCARDS.md` — ~60 rapid-recall rows.
- `MATH_FOUNDATION.md` — `V-1` relaxation proof, DP recurrence.
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
Bellman-Ford relaxes all edges `V-1` times; one more pass detects negative cycles.
Floyd-Warshall DP: `d[k][i][j]=min(d[k-1][i][j], d[k-1][i][k]+d[k-1][k][j])`.
Handles negative weights (no negative cycles for queries). `O(VE)` and `O(V³)`.

## Complexity Cheat-Sheet
| Algo | Time | Space | Note |
|------|------|-------|------|
| Bellman-Ford | O(VE) | O(V) | single source + detection |
| Floyd-Warshall | O(V³) | O(V²) | all pairs, simple loops |
| SPFA avg | ~O(E) | O(V) | no worst guarantee |

## Next Steps
See `VISION.md` and `MINI_PROJECT.md` to visualize negative-cycle detection.
