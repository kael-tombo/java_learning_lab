# Real-World Project: Room Booking Maximizer

## Problem

A venue receives room requests as (start, end) pairs and wants the largest
conflict-free subset plus a machine-style plan for two overflow rooms. Build
a tool that computes the greedy selection and checks it against brute force.

## Inputs

- `requests.csv`: rows `id,start,end` with integer hours, at least 30 rows.
- Machine count 2 for the overflow-room extension.
- A flag selecting `single` room or `overflow` analysis.

## Steps

1. Parse and validate rows: end after start, no negative times.
2. Sort requests by end time; greedily accept non-overlapping ones.
3. Record the accepted set and its count.
4. Brute-force all subsets (inputs capped at 20 rows for this check) and
   confirm the greedy count equals the brute-force maximum.
5. For overflow mode, list-schedule all requests onto 2 rooms greedily.
6. Report per-room load and the makespan with both lower bounds cited.
7. Emit `schedule.txt` with accepted ids, counts, loads, and makespan.
8. Write a two-paragraph operations note on when a request must be refused.

## Acceptance criteria

1. Greedy count matches brute-force maximum on the capped fixture.
2. Accepted set verified pairwise conflict-free by the checker.
3. Overflow loads cover every request exactly once across 2 rooms.
4. Makespan is at least ceil(total/2) and at least the longest request.
5. Invalid rows (end before start) are rejected with a message.
6. `schedule.txt` contains ids, counts, loads, makespan, and bounds.
7. All output uses plain ASCII characters.

## Constraints

- Plain Java only, no external libraries; deterministic single run.
- Brute-force check limited to 20 rows; greedy handles the full file.
- Times are integers; no date parsing or time-zone handling.
