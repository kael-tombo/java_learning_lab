# Mini Project: Tiny Max Flow
> Edmonds-Karp on a 4-node network with a cut certificate.

## Background
- Residual BFS finds augmenting paths; forward/backward edges update each round.
- The unreachable set at termination is the minimum cut - print it.
- Small graphs allow full hand verification of every number.
## Goal
Implement Edmonds-Karp and certify the answer with the cut.
Hand-augment the fixture graph and match the program's flow of 5.
## Tasks
1. Hardcode capacities for the 4-node fixture (3,2 / 1,2 / 3 edges).
2. Loop BFS-augment-update until the sink is unreachable.
3. Print flow value and per-edge final flows.
4. Compute the source-reachable set and print it as the minimum cut.
5. Hand-trace augmentations on paper and reconcile path by path.
6. Brute-force all s-t cuts of the fixture and confirm min equals 5.
## Acceptance criteria
- Program reports maxflow 5 with valid per-edge flows.
- Hand trace matches the program augmentation by augmentation.
- Cut enumeration confirms minimum 5 with the printed reachable set.
- Per-edge flows conserve at middle nodes (inflow equals outflow).
- A disconnected second fixture reports 0 with the empty-side cut.
## Pitfalls
- Missing backward edges, capping flow below optimum.
- DFS instead of BFS while claiming the Edmonds-Karp bound.
- Printing the cut from the original graph instead of the residual.
- Integer types too small for the flow sums on bigger tests.
## Stretch
- Bipartite-matching mode on a workers/jobs fixture.
- Bottleneck-edge report: which capacity increase would raise the flow.
## Timebox
One evening session, roughly 2 hours with hand tracing.
