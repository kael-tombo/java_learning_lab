# Dijkstra — Lab README
> Single-source shortest paths (non-negative weights). Tailored to Dijkstra + min-heap.

## What's Inside
- `THEORY.md` — mechanics, invariants, complexity sketch.
- `EXERCISES.md` — implement + trace + edge cases.
- `QUIZ.md` — 15 questions with answers.
- `FLASHCARDS.md` — ~60 rapid-recall rows.
- `MATH_FOUNDATION.md` — greedy-choice proof, heap bounds.
- `CODE_DEEP_DIVE.md` — annotated Java + pitfalls.
- `VISION.md` / `MINI_PROJECT.md` / `REAL_WORLD_PROJECT.md` — mastery path.
- `LEETCODE_SOLUTION.md` — existing; keep as reference.

## How to Use
1. Read `THEORY.md` (15 min).
2. Do `EXERCISES.md` Levels 1–2 with traces.
3. Self-test with `QUIZ.md` + `FLASHCARDS.md`.
4. Study `CODE_DEEP_DIVE.md`, then build `MINI_PROJECT.md`.
5. Finish with `REAL_WORLD_PROJECT.md` (maps routing) war-story.

## Core Idea
Dijkstra extracts min-dist unsettled node, relaxes outgoing edges, using `PriorityQueue`.
Invariant: extracted `dist[u]` is final (non-negative weights). No negative edges.
`O((V+E) log V)` with binary heap, `O(V²)` naive. Early exit for single target.

## Complexity Cheat-Sheet
| Heap | Time | Space | Note |
|------|------|-------|------|
| Binary | O((V+E) log V) | O(V) | standard Java PQ |
| Naive | O(V²) | O(V) | dense graphs |
| Fibonacci | O(E+V log V) | O(V) | theory only |

## Next Steps
See `VISION.md` and `MINI_PROJECT.md` to benchmark heap variants on city grids.
