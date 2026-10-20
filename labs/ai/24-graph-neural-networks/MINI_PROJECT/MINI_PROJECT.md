# Graph Neural Networks — Mini Project

**Goal**: a small in-memory graph-convolution library plus a label-propagation experiment,
all deterministic, no external frameworks.

## Core API (single file acceptable)

- `Graph(int n)` + `addEdge(a, b)` + `addWeightedEdge(a, b, w)`; `degrees()` returns the
  self-inclusive degree vector.
- `MessagePasser.apply(double[] h, Mode mode)` where `mode` selects `ROW_NORM`,
  `SYMMETRIC`, or `MEAN` (symmetric formula as in GCN with `W = I`).
- `Layer` chains an activation of your choice (`tanh` or `relu`) after the aggregate when
  a boolean flag is set — leave it off for value-less hand-checks.

## Experiment (the actual deliverable)

Graph: 6 nodes = two triangles connected by a single bridge edge
(edges within triangle a: 0-1-2-0; triangle b: 3-4-5-3; bridge: 2-3).
Labels: `[0, 0, 0, 1, 1, 1]`.

1. Run 3 rounds of MESSAGE dropping with each mode and print per-mode `h` after each.
2. Node-classify by a one-parameter scan (Exercise-5 style rule): threshold on first
   coordinate; report train accuracy after 1, 2, 3 layers for each mode.
3. Bridge analysis: state, citing specific printed numbers, how the bridge edge favors
   mixing (node 2's value bending toward triangle b) under each normalization.

## Acceptance

- All prints deterministic: sorted mode names, 4-dp rounding.
- A short captured stdout report pasted at the bottom of your source in a comment.
- Identify at least one place where `ROW_NORM` and `SYMMETRIC` disagree by more than
  `0.1`; explain the disagreement from the `d_i d_j` denominator.

## Stretch

Add 20 random graphs (seed-fixed, Erdos-Renyi with `p = 0.2`) and report average node-value
spread (max minus min) after 3 rounds — expect the spread to shrink; that is smoothing in
aggregate. Any claim goes in the report with its captured evidence.
