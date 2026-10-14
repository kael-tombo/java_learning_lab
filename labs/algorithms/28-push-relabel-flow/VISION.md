# Vision: Push-Relabel Max Flow

## Direction

This lab covers flow networks through push-relabel: preflow initialization,
push and relabel operations, discharge of active nodes, and the O(V^3) bound
for the generic scheme. The practical skill is running the method on a small
graph and stating how it differs from augmenting-path methods.

## What to learn

- Preflow: saturate source edges; neighbors hold excess, conservation waits.
- Heights: source starts at n; push moves excess one level downhill.
- Relabel: lift a stuck active node above its lowest residual neighbor.
- Generic bound: O(V^3); gap heuristic and highest-label speed practice.
- Max-flow min-cut: reachable set in the final residual defines the cut.

## Non-coverage

- This lab does not cover capacity scaling or costed flows.
- It does not cover dynamic trees or other advanced implementations.
- It does not cover multi-commodity flow or NP-hard variants.
- It does not cover/fix a production network optimizer; graphs are tiny.
- No invented pivot traces: every number here comes from a verified run.

## How to use this lab

Trace the preflow values from MOCK_INTERVIEW Q3 by hand, run the full
push-relabel of Q2 against the Edmonds-Karp baseline of Q1, then confirm
both report 5 on the test graph before starting MINI_PROJECT.

## Pitfalls

- Forgetting reverse edges in the residual breaks both methods silently.
- Reading excess at the source as flow; only the sink excess counts.
- Relabeling without checking all residual neighbors first.

## Done when

- You can state the preflow invariant and the height rule from memory.
- You can discharge one active node on paper without notes.
- You can name the O(V^3) bound and one practical improvement.
- You can extract the min cut from a residual graph.
