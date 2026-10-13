# Real-World Project: Room Scheduler
> Maximum-activity scheduling from a CSV of interval requests, with proof notes.

## Problem
One room, many requests with start/end times: fit the maximum number of non-overlapping bookings.
The earliest-finish greedy rule is optimal here, and the README must say why.
## Inputs
- bookings.csv rows: id, start, end (integer times, end after start).
- Fixture sets: overlapping cluster, chainable sequence, identical-end-times edge case.
- Output: chosen ids in schedule order plus the count.
## Steps
1. Parse and validate rows (numeric times, end greater than start, unique ids).
2. Sort requests by end time, breaking ties by start time.
3. Scan once, keeping a request when its start is at or after the last kept end.
4. Emit chosen ids and count; also emit rejected ids with the blocking booking.
5. Include the 3-step exchange argument in the README next to the algorithm.
6. Add a check mode that verifies the output set is pairwise non-overlapping.
## Acceptance criteria
- Six-request classic fixture yields exactly 3 bookings with the expected ids.
- Chainable 10-request fixture schedules all 10.
- Identical-end-times fixture keeps exactly one of the tied requests.
- Check mode passes on all outputs and catches a hand-corrupted schedule.
- Invalid rows (end before start, duplicates) are rejected with row numbers.
## Failure modes
- Zero-length meetings are rejected (they break the strict-overlap accounting).
- Requests spanning midnight are rejected; times must lie in one day.
- Ties in end time resolve deterministically by start time then id.
## Extensions
- Weighted variant explicitly refused in the README with the DP reason and a counterexample.
- Multi-room extension sketch: when greedy still works and when it stops.
## How to demo
- Walk the scan on the classic fixture showing kept vs rejected per step.
- Read the exchange argument aloud and map each step to the code.
