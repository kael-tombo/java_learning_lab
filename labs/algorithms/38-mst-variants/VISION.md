# VISION — MST Variants
> Direction: from running Kruskal as a recipe to seeing every MST algorithm as the cut property in different clothes.

## Where this sits
- Kruskal (lightest edge crossing any cut, cycle check via union-find), Prim (lightest edge out of the grown tree), Boruvka (parallel cheapest-outgoing per component): one property, three schedules, all O(E log V) in standard forms.
- Second-best MST via max-edge swaps; MST edge-sensitivity and bottleneck (minimax) paths as nearby ideas.
- Distinct weights imply a unique MST; ties need explicit tie-breaking for stable plans.

## 4-week direction
- Week 1: hand-run Kruskal and Prim on the reference graph; reproduce weight 8 both ways.
- Week 2: finish MINI_PROJECT; complete the timing table and name the winner per size.
- Week 3: trace every second-best swap by hand; verify 9 is minimal over the swaps.
- Week 4: REAL_WORLD_PROJECT review; whiteboard the cut property and one correctness sketch in 10 minutes.

## Done criteria
- State the cut property and apply it to justify one Kruskal edge and one Prim step.
- Explain why distinct weights force uniqueness, with the exchange argument.
- Pick Kruskal vs Prim (heap vs dense) for a given (V, E, density) triple.

## Non-coverage
- This lab does not implement Boruvka (described as the parallel schedule), dynamic MST, or directed MST (Edmonds), each named with its trigger condition.
- No linear-time randomized MST theory; bounds quoted are the standard deterministic ones.
- Geometric/Euclidean MST specializations are out of scope.

## Pitfalls
- Forgetting the tie-break; nondeterministic plans erode trust in phased builds.
- Spanning a disconnected graph silently; components must be reported.
- Calling any spanning tree minimal without the cut/cycle exchange check.

## Adjacent labs
- Pair with 37-graph-coloring-clique for proof style and graph-algorithms-deep for flow/cut duality around the cut property.
- Revisit when tempted by a "cheaper" hand-drawn network; the swap table prices hunches.

## Weekly drills
- State the cut property and apply it to one reference-graph edge from memory.
- Re-run Kruskal and Prim by hand on the 7-edge graph; confirm 8 both ways.
- Argue uniqueness from distinct weights via a single exchange step.

## Anti-roadmap
- Do not accept shuffled-input plan changes; determinism is a feature, enforce the tie-break.
- Do not span disconnected surveys; report components instead.
