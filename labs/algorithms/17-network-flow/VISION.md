# Vision: Network Flow
> Max-flow/min-cut duality with algorithms that certify their own answers.

## Where this leads
- Bipartite matching, assignment, and transportation-style allocation models.
- Reductions: turning a new problem into flow and inheriting the algorithms.
- Certificates: cuts that prove a flow optimal without trusting the code.
## What mastering it unlocks
- Augment along residual paths and maintain forward/backward edges correctly.
- State max-flow min-cut and use a cut to certify a computed flow.
- Reduce bipartite matching to flow with unit capacities and read off the matching.
- Explain Ford-Fulkerson O(E*|f|) and why Edmonds-Karp fixes it to O(V*E^2).
- Extract the minimum cut as the source-reachable set in the final residual graph.
## What it does not cover
- Push-relabel internals and highest-label variants in full detail.
- Minimum-cost flow and circulation with demands.
- Dynamic or stochastic network models.
## Core questions you will answer
- Why must every augmentation add a backward edge to the residual graph?
- Why does BFS (shortest augmenting path) bound the number of augmentations?
- How does the reachable set in the residual graph define a minimum cut?
- Which capacities make plain Ford-Fulkerson slow, and why?
## How to judge progress
- Code Edmonds-Karp and certify the result with the cut on demand.
- Reduce a matching or allocation story to a flow network correctly.
- Derive both complexity bounds from the augmentation structure.
## Common misuse
- Forgetting backward edges, which silently caps the flow below optimum.
- Quoting max-flow min-cut as magic instead of exhibiting the certifying cut.
## After this lab
- 28-push-relabel-flow for the faster max-flow family.
- 07-graph-algorithms for BFS/DFS/Dijkstra foundations underneath flow.
One-line self-test: Explain why the residual reachable set certifies optimality in two sentences.
