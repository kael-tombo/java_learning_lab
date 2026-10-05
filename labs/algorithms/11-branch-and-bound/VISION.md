# VISION — Branch and Bound: Problem-Solving Mastery Path
> Where this lab takes you: from exhaustive search to optimizer engineering.

## The Arc
1. **Foundations** — relaxations as bounds, fathom rules, best-first vs DFS.
2. **Fluency** — knapsack/TSP B&B blind with ratio presort + greedy seed.
3. **Discrimination** — B&B vs DP vs FPTAS (W-size? n? approx-ok?).
4. **Scale** — incremental bounds, strong branching, time-boxed incumbents.
5. **Production** — schedulers/packers with optimality-gap SLAs.

## Milestones
- [ ] M1: bound computation on paper for a 3-item instance.
- [ ] M2: fathom soundness argued in a paragraph.
- [ ] M3: greedy seed halves nodes (measured).
- [ ] M4: gap-vs-time curve plotted (see MINI_PROJECT).
- [ ] M5: optimizer ships with gap + timeout guardrails.

## Anti-Goals
- Exact B&B without timeouts in prod; unsorted bounds.

## Interview Lens
- "Bound? Fathom? Why optimal?" — the triple.

## 30-Day Plan
- Wk1 THEORY+MATH bounds. Wk2 EXERCISES. Wk3 MINI_PROJECT.
- Wk4 REAL_WORLD_PROJECT + teach-back.

## Done = You Can
- Ship optimizers that prove, prune, and stop on time.
