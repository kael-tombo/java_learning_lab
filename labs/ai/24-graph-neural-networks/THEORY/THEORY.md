# Graph Neural Networks — Theory

A **graph neural network** operates on data organized as nodes and edges rather than fixed
grids or sequences: think dependency graphs, road networks, social graphs, molecules. The
common trick is *message passing*: every layer lets each node hear from its neighbors and
replaces its own vector with a transformed combination of the gathered messages.

## What a network layer actually computes

Per graph convolution step, typically:

1. Gather: take the neighbor set `N(i)` of node `i`.
2. Aggregate: combine `h_j` for `j in N(i)` with sum, mean, or max (we use sum-style
   weighting in this lab, with constant normalization).
3. Combine: apply a weight matrix and a non-linearity to the aggregate (with or without
   the node's own previous state — famous as the "self-loop" question).

Stacking two layers widens each node's receptive field to two hops; note the trade-off
of pushing too many layers (classic semi-supervised studies report deep plain-GCN stacks
underperforming, so width/depth tuning matters — treat report numbers as method-specific).

## Standard variant: the GCN layer

The widely used graph-convolution form keeps self-relations explicitly by adding the
identity:

```
A_hat = A + I
H^(l+1) = sigma( D_hat^{-1/2} * A_hat * D_hat^{-1/2} * H^(l) * W^(l) )
```

where `D_hat` holds the self-inclusive degrees. The symmetric normalization prevents hub
nodes from dominating purely because they appear in many adjacency rows. When every node
has equal self-inclusive degree (our cycle graph does: exactly three), the symmetric
normalization reduces to plain mean aggregation — that reduction is the key to making the
lesson hand-checkable.

## Tasks these networks handle

- Node classification: label each node (semi-supervised when labels cover few nodes).
- Graph classification: pool node vectors into one graph-level vector.
- Link prediction and sampling-based variants (GraphSAGE-style neighborhood sampling) for
  large graphs — concept-level only in this lab.

## Java angle

Adjacency is just a square array; message passing is two nested loops. Everything in
CODE_DEEP_DIVE runs on `int[][]` and `double[]`, so you can test the algebra itself
before adding any framework. Deterministic small-graph checks (a 4-cycle and a star) are
the fastest way to make the normalization rules stick.
