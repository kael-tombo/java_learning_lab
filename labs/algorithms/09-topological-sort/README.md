# Topological Sort — Lab README
> Linearize DAGs: Kahn + DFS. Tailored to topological ordering and cycle detection.

## What's Inside
- `THEORY.md` — mechanics, invariants, complexity sketch.
- `EXERCISES.md` — implement + trace + edge cases.
- `QUIZ.md` — 15 questions with answers.
- `FLASHCARDS.md` — ~60 rapid-recall rows.
- `MATH_FOUNDATION.md` — DAG characterization, counting orders.
- `CODE_DEEP_DIVE.md` — annotated Java + pitfalls.
- `VISION.md` / `MINI_PROJECT.md` / `REAL_WORLD_PROJECT.md` — mastery path.

## How to Use
1. Read `THEORY.md` (15 min).
2. Do `EXERCISES.md` Levels 1–2 with traces.
3. Self-test with `QUIZ.md` + `FLASHCARDS.md`.
4. Study `CODE_DEEP_DIVE.md`, then build `MINI_PROJECT.md`.
5. Finish with `REAL_WORLD_PROJECT.md` (build-system DAG) war-story.

## Core Idea
Topo sort orders DAG so every edge `u→v` has `u` before `v`.
Kahn: repeatedly emit indegree-0 nodes. DFS: emit postorder reversed.
Invariant: emitted prefix has no incoming edge from remainder. `O(V+E)`.
Fails (partial output) iff cycle exists — the detection signal.

## Complexity Cheat-Sheet
| Method | Time | Space | Note |
|--------|------|-------|------|
| Kahn | O(V+E) | O(V) | lexicographic with PQ |
| DFS | O(V+E) | O(V) | needs reverse postorder |
| Matrix | O(V²) | O(V) | dense only |

## Next Steps
See `VISION.md` and `MINI_PROJECT.md` to schedule a mock build DAG.
