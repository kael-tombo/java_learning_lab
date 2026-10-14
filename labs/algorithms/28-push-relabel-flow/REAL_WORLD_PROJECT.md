# Real-World Project: Evacuation Route Checker

## Problem

A venue models corridors as a flow network (rooms as nodes, door rates as
capacities) and needs the max exit throughput plus the bottleneck cut. Build
a checker that computes both with two independent methods.

## Inputs

- `network.csv`: rows `from,to,capacity` with non-negative integer rates.
- Source node id and sink node id passed as program arguments.
- Node count capped at 50 for the matrix representation.

## Steps

1. Parse rows; reject negative capacities and unknown endpoint ids.
2. Build the capacity matrix; confirm source differs from sink.
3. Compute max flow with Edmonds-Karp (BFS augmenting paths).
4. Compute max flow with generic push-relabel (preflow plus discharge).
5. Assert both methods report the same value; abort loudly on mismatch.
6. Extract the min cut: BFS the final residual from the source side.
7. Emit `evacuation.txt` with flow value, cut edges, and cut capacity.
8. Write a two-paragraph note naming the bottleneck doors by id.

## Acceptance criteria

1. Both methods agree on every accepted network including the reference.
2. Reference graph (this lab's test edges) reports flow 5 and cut 5.
3. Cut edges listed with capacities summing exactly to the flow value.
4. Disconnected source and sink yields flow 0 with an empty cut note.
5. Negative capacity rows exit with a message naming the row.
6. `evacuation.txt` contains value, cut edges, capacity, and method note.
7. All output uses plain ASCII characters.

## Constraints

- Plain Java only, no external libraries; deterministic single run.
- Matrix form documented with the 50-node cap in the file header.
- No framing of results beyond what both methods confirm.
