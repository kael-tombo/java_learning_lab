# Real-World Project: Vertex Cover Reporter
> Greedy 2-approximation for vertex cover with a brute-force auditor on small graphs.

## Problem
Minimum vertex cover is NP-hard, so the tool ships the fast greedy answer plus a quality report.
For graphs up to 20 nodes a brute-force optimum is feasible and certifies the ratio.
## Inputs
- Graph files as edge lists (n nodes, m edges), plus a generator with fixed seeds.
- 50 generated instances with n between 10 and 20 for the audit run.
- Output: greedy cover set, optimum size (small graphs), and the ratio.
## Steps
1. Parse the edge list and validate node indices and duplicates.
2. Run the greedy endpoint-pair algorithm to build the cover.
3. For n <= 20, brute-force all subsets to find the true optimum size.
4. Record greedy size, optimum size, and ratio per instance in a CSV row.
5. Print the worst ratio and the mean ratio across the audit set.
6. Fail the audit if any ratio exceeds 2 on the generated instances.
## Acceptance criteria
- Audit passes with every ratio at most 2 across all 50 instances.
- A hand-built star graph reports greedy equal to optimum (ratio 1).
- Empty and single-edge graphs return covers of size 0 and 1.
- CSV contains one row per instance with columns instance, greedy, optimum, ratio.
- Greedy on the 1000-node fixture finishes in under 2 seconds.
## Failure modes
- Self-loops are rejected at parse time with the line number.
- Graphs over 20 nodes skip brute force with a note instead of hanging.
- Duplicate edges are deduplicated once, counted once in reports.
## Extensions
- Greedy set-cover mode on universe/set fixtures with the same audit harness.
- LPT scheduling mode comparing makespan to brute-force optimum.
## How to demo
- Show the worst-ratio instance and walk through why greedy paid double there.
- Show the timing gap between greedy and brute force at n = 20.
