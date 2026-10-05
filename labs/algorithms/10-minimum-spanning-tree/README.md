# Minimum Spanning Tree — Lab README
> Cheapest connectivity: Kruskal + Prim. Tailored to MST cut/cycle properties.

## What's Inside
- `THEORY.md` — mechanics, invariants, complexity sketch.
- `EXERCISES.md` — implement + trace + edge cases.
- `QUIZ.md` — 15 questions with answers.
- `FLASHCARDS.md` — ~60 rapid-recall rows.
- `MATH_FOUNDATION.md` — cut/cycle proofs, Union-Find amortized bounds.
- `CODE_DEEP_DIVE.md` — annotated Java + pitfalls.
- `VISION.md` / `MINI_PROJECT.md` / `REAL_WORLD_PROJECT.md` — mastery path.

## How to Use
1. Read `THEORY.md` (15 min).
2. Do `EXERCISES.md` Levels 1–2 with traces.
3. Self-test with `QUIZ.md` + `FLASHCARDS.md`.
4. Study `CODE_DEEP_DIVE.md`, then build `MINI_PROJECT.md`.
5. Finish with `REAL_WORLD_PROJECT.md` (network design) war-story.

## Core Idea
MST connects all vertices at minimum total weight (connected undirected graph).
Kruskal sorts edges, unions disjoint sets. Prim grows tree via min fringe edge.
Cut property justifies each greedy pick. `O(E log E)` / `O(E log V)`.
Union-Find with path compression + union by rank is ~`α(V)` per op.

## Complexity Cheat-Sheet
| Algo | Time | Space | Note |
|------|------|-------|------|
| Kruskal | O(E log E) | O(V) | sort-dominated |
| Prim+PQ | O(E log V) | O(V) | sparse-friendly |
| Borůvka | O(E log V) | O(V) | parallel-friendly |

## Next Steps
See `VISION.md` and `MINI_PROJECT.md` to wire a mock network cheaply.
