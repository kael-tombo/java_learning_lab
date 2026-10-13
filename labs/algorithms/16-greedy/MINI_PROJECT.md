# Mini Project: Activity Picker
> Earliest-finish scheduling with a written exchange argument.

## Background
- Sort by finish time, scan once, keep compatible activities.
- The exchange argument is the deliverable, not just the code.
- A failing variant (sort by start) belongs in the test set as contrast.
## Goal
Implement the scheduler plus a verifier and a failing-variant demo.
Write the exchange proof in the README in four numbered steps.
## Tasks
1. Parse id/start/end rows with validation (end after start, unique ids).
2. Sort by end time and scan, keeping starts at or after the last end.
3. Verify output sets are pairwise non-overlapping with a checker.
4. Implement sort-by-start variant and show it failing on a 3-activity fixture.
5. Test identical-end-times and single-activity edge fixtures.
6. Write the 4-step exchange argument mapped to code lines.
## Acceptance criteria
- Classic 6-activity fixture picks the expected 3 bookings.
- Checker passes on all outputs and rejects a corrupted schedule.
- Start-sort variant demonstrably fails the 3-activity fixture.
- Edge fixtures behave as documented.
- README proof references actual variable names from the code.
## Pitfalls
- Strict vs non-strict compatibility (start == end) handled inconsistently.
- Unstable tie-breaking that makes outputs differ run to run.
- Claiming optimality from tests alone without the exchange argument.
- Allowing zero-length intervals that break the counting.
## Stretch
- Fractional-knapsack mode showing the other canonical greedy.
- Weighted-interval note: smallest instance where greedy fails, with DP pointer.
## Timebox
One afternoon session, roughly 2 hours with the proof write-up.
