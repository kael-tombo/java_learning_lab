# DP Basics — Lab README
> Memoize or tabulate: overlapping subproblems. Tailored to Fib/climbing-stairs入门 DP.

## What's Inside
- `THEORY.md` — mechanics, invariants, complexity sketch.
- `EXERCISES.md` — implement + trace + edge cases.
- `QUIZ.md` — 15 questions with answers.
- `FLASHCARDS.md` — ~60 rapid-recall rows.
- `MATH_FOUNDATION.md` — recurrences, induction proofs.
- `CODE_DEEP_DIVE.md` — annotated Java + pitfalls.
- `VISION.md` / `MINI_PROJECT.md` / `REAL_WORLD_PROJECT.md` — mastery path.

## How to Use
1. Read `THEORY.md` (15 min).
2. Do `EXERCISES.md` Levels 1–2 with traces.
3. Self-test with `QUIZ.md` + `FLASHCARDS.md`.
4. Study `CODE_DEEP_DIVE.md`, then build `MINI_PROJECT.md`.
5. Finish with `REAL_WORLD_PROJECT.md` (resource allocation) war-story.

## Core Idea
DP solves overlapping subproblems once: `dp[n]=dp[n-1]+dp[n-2]` (Fib).
Top-down memo vs bottom-up tabulation; state DAG must be acyclic.
Invariant: when computing state, dependencies already solved.
Drops exponential naive to `O(n)` time, `O(1)` space optimized.

## Complexity Cheat-Sheet
| Form | Time | Space | Note |
|------|------|-------|------|
| Naive recurse | O(2ⁿ) | O(n) | repeated work |
| Memo | O(n) | O(n) | recursion + table |
| Tabulated opt | O(n) | O(1) | two vars |

## Next Steps
See `VISION.md` and `MINI_PROJECT.md` to benchmark naive vs DP.
