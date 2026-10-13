# Math Foundation: Augmentation Bounds and Cut Duality
> Ford-Fulkerson O(E*|f|), Edmonds-Karp O(V*E^2), cut capacity as optimality proof.

## Definitions
- Flow: per-edge values within capacities with conservation at non-terminals.
- Residual graph: forward slack plus backward edges recording pushed flow.
- Augmenting path: s-t path in the residual graph; bottleneck = minimum slack.
- Cut (S, T): capacity = sum of capacities from S side to T side.

## Counting argument
- One augmentation: O(E) path search plus O(V) update: O(E) total.
- Ford-Fulkerson augments at most |f| times (unit progress per round): O(E*|f|).
- Edmonds-Karp uses BFS shortest paths: O(V*E) augmentations suffice.
- Total O(V*E^2); capacities need not be integers for this bound.

## Recurrence
- Flow value rises by the bottleneck each round: strictly increasing progress.
- BFS distances from s in the residual graph never decrease across rounds.
- Each augmentation saturates at least one edge on a shortest path.
- Edges saturate O(V) times before distances must rise: O(V*E) rounds total.

## Derivation of the bound
- Weak duality: every flow value <= every cut capacity (telescoping conservation sum).
- Termination with no augmenting path yields the reachable-set cut at equality.
- Max-flow min-cut: the final flow meets its cut, proving both optimal.
- Integer capacities additionally give integral flows (each bottleneck integral).

## Worked mini-proofs
- Proof 1: flow <= cut via conservation summed over S. (4 lines)
- Proof 2: BFS distance monotonicity across augmentations (standard lemma). (5 lines)
- Proof 3: reachable-set cut capacity equals final flow value. (4 lines)

## Exercises with answers
- 1. Max flow of the 4-node fixture (3,2 / 1,2 / 3). Answer: 5.
- 2. Min cut capacity of the same fixture. Answer: 5 (S = {s} suffices).
- 3. Ford-Fulkerson rounds bound for integer max flow 5. Answer: at most 5 unit rounds.

## Pitfalls
- Quoting O(E*|f|) for Edmonds-Karp (the BFS bound is better and capacity-free).
- Reading the cut off the original graph instead of the final residual.
- Forgetting backward edges, which breaks both the algorithm and the duality.

## Checklist
- Derive both augmentation bounds from rounds-times-search.
- Prove weak duality from conservation in four lines.
