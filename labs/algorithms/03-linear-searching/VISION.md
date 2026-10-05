# VISION — Linear Searching: Problem-Solving Mastery Path
> Where this lab takes you: from scans to knowing exactly when not to scan.

## The Arc
1. **Foundations** — prefix-clean invariant, probe counting, first-hit semantics.
2. **Fluency** — null-safe `.equals`, empty/duplicate traces blind.
3. **Discrimination** — linear vs binary vs hash (size, order, query count).
4. **Scale** — sentinel/branch tricks; when to sort-once-then-binary-search.
5. **Production** — log scans, small-n hot paths, pre-index filters.

## Milestones
- [ ] M1: invariant + variant stated without notes.
- [ ] M2: 4 edge traces (empty/dup/null/single) green.
- [ ] M3: crossover measured (linear wins n<~50 vs binary).
- [ ] M4: "sort once?" break-even computed for q queries.
- [ ] M5: code-review comment catching `==`-on-objects.

## Anti-Goals
- Binary-searching unsorted data; hashing for one-shot tiny scans.

## Interview Lens
- "Average probes?" ((n+1)/2). "Why first occurrence matters?"

## 30-Day Plan
- Wk1 THEORY+EXERCISES. Wk2 QUIZ/FLASHCARDS. Wk3 MINI_PROJECT benchmark.
- Wk4 REAL_WORLD_PROJECT + teach-back.

## Done = You Can
- Choose scan vs index with a back-of-envelope probe budget.
