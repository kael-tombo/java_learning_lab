# VISION — Sorting Basics: Problem-Solving Mastery Path
> Where this lab takes you: from first scan to production-grade ordering.

## The Arc
1. **Foundations** — invariants, traces, `Θ(n²)` vs `Θ(n log n)` intuition.
2. **Fluency** — implement bubble/insertion/selection blind; edge tables green.
3. **Discrimination** — know when basics suffice (n<50, nearly-sorted → insertion).
4. **Scale** — graduate to advanced sorts; benchmark crossovers (see MINI_PROJECT).
5. **Production** — DB ORDER BY, log pipelines, `Collections.sort` (TimSort) awareness.

## Milestones (checkable)
- [ ] M1: trace 3 sorts on `[5,2,4,6,1,3]` without code.
- [ ] M2: stability + in-place table filled from memory.
- [ ] M3: doubling experiment shows quadratic curve.
- [ ] M4: insertion beats quick on n=10 nearly-sorted (measured).
- [ ] M5: explain sort choice in a PR (data size + stability + memory).

## Anti-Goals
- Memorizing code without invariants; premature `Arrays.sort` avoidance in prod.

## Interview Lens
- "Why insertion for small n?" (cache + constants). "Stable?" with example.

## 30-Day Plan
- Wk1 THEORY+EXERCISES L1–L2. Wk2 QUIZ/FLASHCARDS to 90%+. Wk3 MINI_PROJECT.
- Wk4 REAL_WORLD_PROJECT war-story + teach-back (5-min whiteboard).

## Done = You Can
- Pick the right sort for a ticket, justify with numbers, and avoid classic traps.
