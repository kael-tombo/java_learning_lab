# Graph Neural Networks — Real-World Project

**Goal**: a relational mail-routing scorer — a Java design exercise where graph features
feed a screening decision, deliberately kept to a small, fully synthetic dataset.

## Scenario

Route requests (nodes) to data centers (a few hub nodes); each request carries a small
feature vector (priority tier, payload size class — invented enums, clearly fake data).
Model the routing table as a bipartite-like graph and score with message passing so a
node's own attributes and its peers' congestion shape the decision.

## Components

1. `Topology`: 8 request nodes + 3 hubs; edges with weights in `[0..1]` for affinity.
2. `FeatureTable`: per-node 3-dim vectors; hub nodes include a synthetic load value.
3. `RelationalScorer`: two rounds of symmetric-normalized message passing, `W = I`;
   then a linear score per request node.
4. `PolicySimulator`: pick argmax hub per request; report per-hub load totals pre/post
   scoring and the count of ties broken deterministically.

## Analysis deliverables (write these, not just code)

- A before/after table of hub loads: does relational smoothing actually disperse load vs
  the greedy argmax on raw features? Quote the numbers from your run.
- Discussion of two deployment realities: (a) a hub's own state changes between rounds —
  a stale-refresh hazard for any real scheduler; (b) feedback loops (routing shapes the
  state the router learns from), with one mitigating idea each.
- Explicit statement of the toy-data caveat: no benchmark claim is made.

## Constraints

No external graph libraries; `javac --release 21`; seed everything; keep the full source
under ~300 lines so a reviewer can audit by reading it.
