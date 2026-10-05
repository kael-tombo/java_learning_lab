# Knapsack DP — Lab README
> 0/1 choice under capacity. Tailored to 0/1 knapsack (weight/value DP).

## What's Inside
- `THEORY.md` — mechanics, invariants, complexity sketch.
- `EXERCISES.md` — implement + trace + edge cases.
- `QUIZ.md` — 15 questions with answers.
- `FLASHCARDS.md` — ~60 rapid-recall rows.
- `MATH_FOUNDATION.md` — pseudo-polynomial analysis, reductions.
- `CODE_DEEP_DIVE.md` — annotated Java + pitfalls.
- `VISION.md` / `MINI_PROJECT.md` / `REAL_WORLD_PROJECT.md` — mastery path.

## How to Use
1. Read `THEORY.md` (15 min).
2. Do `EXERCISES.md` Levels 1–2 with traces.
3. Self-test with `QUIZ.md` + `FLASHCARDS.md`.
4. Study `CODE_DEEP_DIVE.md`, then build `MINI_PROJECT.md`.
5. Finish with `REAL_WORLD_PROJECT.md` (cargo/budget) war-story.

## Core Idea
0/1 knapsack: pick subset max value with `Σw ≤ W`, each item once.
Recurrence `dp[i][w]=max(dp[i-1][w], dp[i-1][w-wi]+vi)`. 1-D needs reverse `w` loop.
Invariant: `dp[w]` = best using processed items at capacity `w`. `O(nW)` time.
Pseudo-polynomial; NP-hard in general. Reconstruct via parent table.

## Complexity Cheat-Sheet
| Form | Time | Space | Note |
|------|------|-------|------|
| 2-D | O(nW) | O(nW) | reconstructable |
| 1-D opt | O(nW) | O(W) | reverse loop |
| Fractional | O(n log n) | O(1) | greedy by ratio |

## Next Steps
See `VISION.md` and `MINI_PROJECT.md` to pack a mock cargo manifest.
