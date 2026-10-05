# VISION — Advanced Sorting: Problem-Solving Mastery Path
> Where this lab takes you: from `n log n` proofs to engine-level sort tuning.

## The Arc
1. **Foundations** — merge/quick/heap mechanics + Master theorem.
2. **Fluency** — partition + merge blind; overflow-safe mids; stability calls.
3. **Discrimination** — quick(avg) vs merge(worst) vs heap(memory) vs TimSort(objects).
4. **Scale** — external sort, parallel merges, cutoff tuning (see MINI_PROJECT).
5. **Production** — DB sort-merge joins, log pipelines, stdlib selection.

## Milestones
- [ ] M1: partition `[5,2,4,6,1,3]` on paper, pivot-final invariant stated.
- [ ] M2: Master-classify `2T(n/2)+n` + quick-worst unrolling.
- [ ] M3: doubling ratios ≈2.1–2.3 (linearithmic signature).
- [ ] M4: 3-way partition on all-duplicates input measured.
- [ ] M5: sort-choice PR note with data profile.

## Anti-Goals
- Hand-rolling sorts in prod where `Arrays.sort` wins; ignoring stability.

## Interview Lens
- "Quicksort worst + fix?" (shuffle/median). "Why heap O(n) build?" (leaf sum).

## 30-Day Plan
- Wk1 THEORY+CODE_DEEP_DIVE. Wk2 EXERCISES+benchmarks. Wk3 MINI_PROJECT.
- Wk4 REAL_WORLD_PROJECT + teach-back.

## Done = You Can
- Tune or replace a sort bottleneck with measured evidence.
