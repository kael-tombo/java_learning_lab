# Optimization Algorithms — Lab README
> Java Learning Lab · `labs/algorithms` · 25-optimization-algorithms

## What this lab is
- Focus: hill climbing, gradient descent, simulated annealing.
- Core object: descent lemma; cooling schedules; convexity => global optimum.
- You will implement, trace, benchmark, and apply it to hyperparameter tuning, routing, portfolios.

## Learning outcomes
- Explain mechanics and invariants in plain language.
- Derive time/space complexity from first principles.
- Implement bug-free Java 17 code with edge cases.
- Benchmark inputs and visualize scaling.
- Map the technique to one production use-case.

## Map of files
| File | Purpose |
|---|---|
| THEORY.md | Mechanics + invariants + complexity proof (~100 lines) |
| EXERCISES.md | Implement + trace + edge cases with Java templates |
| QUIZ.md | 15 questions with answers |
| FLASHCARDS.md | ~60 quick recall rows |
| MATH_FOUNDATION.md | Recurrences / Master theorem / amortized |
| CODE_DEEP_DIVE.md | Java implementation + pitfalls |
| VISION.md | Mastery path |
| MINI_PROJECT.md | Implement + benchmark + visualize |
| REAL_WORLD_PROJECT.md | Production use-case with metrics + prevention |

## How to work this lab (90–120 min)
1. Read THEORY.md (25 min) — write the invariant in your own words.
2. Do EXERCISES.md tasks 1–4 on paper then in IDE (35 min).
3. Self-test QUIZ.md + FLASHCARDS.md (15 min).
4. Skim MATH_FOUNDATION.md proofs; replicate one (10 min).
5. Read CODE_DEEP_DIVE.md; note 3 pitfalls (10 min).
6. Build MINI_PROJECT.md; record timings table (30+ min).
7. Design REAL_WORLD_PROJECT.md rollout + rollback (20 min).

## Prerequisites
- Java 17+, Big-O basics, JUnit 5.
- Prior labs: complexity-analysis, recursion, sorting basics.

## Definition of done
- [ ] Exercises compile and tests pass.
- [ ] Benchmark table filled with n=1k/10k/100k.
- [ ] One production mapping written with metric + guardrail.
