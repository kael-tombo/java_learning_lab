# Real-World Project: Shift Assigner
> Bipartite worker-to-shift matching via max flow, with a cut certificate for gaps.

## Problem
Assign workers to shifts they are qualified for, maximizing filled shifts.
Unfilled shifts need an explanation: the minimum cut names the bottleneck group.
## Inputs
- workers.csv, shifts.csv, and qualifications.csv (worker, shift) pairs.
- Fixtures: perfect case (all filled), bottleneck case (one short), empty-qualification case.
- Output: assignment list, filled count, and bottleneck explanation when short.
## Steps
1. Build the flow network: source to workers, qualification edges, shifts to sink, all unit capacity.
2. Run Edmonds-Karp to max flow and read the assignment off saturated worker-shift edges.
3. Take the source-reachable set in the final residual graph as the minimum cut.
4. Translate the cut into words: which worker group and which shift group limit the matching.
5. Print assignment lines plus filled/total and the bottleneck note.
6. Cross-check the matching size with a direct augmenting-path implementation.
## Acceptance criteria
- Perfect fixture fills all shifts with a valid assignment (every pair qualified).
- Bottleneck fixture reports the exact shortfall with the correct limiting group.
- Empty-qualification fixture reports zero filled without crashing.
- Both solvers agree on matching size across all fixtures.
- 50-worker random fixture (fixed seed) solves in under 5 seconds.
## Failure modes
- Unknown worker/shift ids in qualifications are rejected with row numbers.
- Duplicate qualification rows are deduplicated with a warning count.
- Disconnected workers appear explicitly as unassigned, never silently dropped.
## Extensions
- Capacities above 1 (workers taking multiple shifts) as a documented extension.
- Priority shifts mode sketch with min-cost flow named as the follow-up.
## How to demo
- Show the bottleneck explanation for the short fixture and verify it by hand.
- Show the residual reachable set and map it to the printed explanation.
