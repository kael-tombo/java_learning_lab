# Mini Project: Window Drills
> Two window patterns drilled to linearity with counters.

## Background
- Fixed windows slide in O(1) per step; variable windows shrink on violation.
- Each index enters and leaves at most once - the counters prove it.
- Last-seen maps make the longest-unique shrink step O(1).
## Goal
Implement longest-unique-substring and max-sum-k with visit counters.
Verify the classic fixtures and the 2n visit bound.
## Tasks
1. Implement longest-unique with expand/shrink and best-bounds tracking.
2. Assert abcabcbb gives 3, bbbbb gives 1, empty gives 0.
3. Implement fixed max-sum-k with O(1) window updates.
4. Verify max-sum fixtures including all-negative series by hand.
5. Count index visits and assert at most 2 per index everywhere.
6. Test k = 1, k = length, and single-character inputs.
## Acceptance criteria
- All string fixtures report exact expected values with valid bounds.
- All numeric fixtures match hand-computed answers.
- Visit bound holds on every fixture with counters printed.
- Edge cases (empty, k = 1, k = length) pass.
- Reported substrings verify repeat-free on re-check.
## Pitfalls
- Moving left backward on some inputs, breaking the amortized bound.
- Rescanning the window per step, returning to quadratic silently.
- Shrink conditions that never trigger, growing the window to the whole string.
- Forgetting to update best bounds when shrinking (stale answers).
## Stretch
- At-most-K-distinct as a second variable-window drill.
- Minimum-window-substring sketch with the validity predicate spelled out.
## Timebox
One afternoon session, roughly 2 hours with counters.
