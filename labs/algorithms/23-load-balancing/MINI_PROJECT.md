# Mini-Project: Dispatch Simulator

## Goal

Simulate three dispatch rules (round-robin, random with fixed seed, and
least-connections) over one skewed arrival script and compare max load.

## Inputs

- 3 servers, 12 arrivals with fixed holding times below; seed 42 for random.
- Holding times: [4, 1, 1, 2, 5, 1, 1, 3, 1, 2, 1, 4].

## Steps

1. Model each server with an open-connection counter and release events.
2. Implement round-robin: arrivals cycle s1, s2, s3 regardless of load.
3. Implement random: pick uniformly with `new Random(42)`.
4. Implement least-connections with earliest-server tie-break.
5. Replay the 12 arrivals under each rule with the same holding times.
6. Record peak concurrent connections per server per rule.
7. Print a table of (rule, peak s1, peak s2, peak s3, max peak).
8. State which rule minimized the max peak and by how much.

## Acceptance criteria

1. All three rules replay the identical 12-arrival, identical-hold script.
2. Random rule uses seed 42 and prints the seed used.
3. Table shows peaks for every server under every rule.
4. Least-connections max peak is less than or equal to round-robin max peak.
5. Release logic verified: after advancing the clock past the final release, every counter is zero.
6. Winner statement cites the two max-peak numbers.
7. All output uses plain ASCII characters.

## Grading note

- Winner decided by max-peak numbers only, not by prose.
- Random rule must print the seed 42 it actually used.
- Post-drain zero counters required for the release check.

## Stretch

- Add a fourth rule: pick two at random, take the less loaded; compare peaks.
- Skew the script harder (one 10-tick request) and re-run the comparison.
