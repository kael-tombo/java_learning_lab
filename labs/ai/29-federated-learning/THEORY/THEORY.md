# Federated Learning — Theory

**Federated learning (FL)** trains a shared model across many data holders while the raw
data never leaves their premises. A coordinator ships the current weights, participants
compute local updates on their own private batches, and the coordinator merges updates.

## The loop (standard rounds)

1. **Selection**: choose a subset of participants for the round (all of them in our toy).
2. **Broadcast**: send the current global model to the chosen clients.
3. **Local update**: each client does some private training/steps on its own data.
4. **Aggregation**: the server fuses client updates — the classic scheme is a weighted
   mean proportional to each client's data count (the canonical FedAvg averaging rule)
   and weights update.

The essential discipline is projection: participants hold data the server cannot read;
the math only sees vectors of numbers. Everything in our snippets reduces to client
gradient vectors and weighted summation on the server.

## Distribution shift is the central difficulty

- **Non-IID partitions**: client datasets differ in size, class balance, and feature
  ranges. A plain uniform average of update directions then encodes the majority, not the
  population — the weighted variant exists for exactly this reason and the drift snippet
  quantifies the difference.
- **Client drift within a round**: between two aggregations, clients wander along their
  own gradients; the longer the local phase, the farther they drift from whatever the
  server believes — known measures and fixes (proximal penalties in the loss,
  server-side momentum) exist at concept level here.

## Practical concerns that dominate engineering time

- Participation turnover: clients join and leave; stale updates from a past round are a
  correctness hazard (they must be dropped or explicitly down-weighted).
- Cost model: a full round costs upload plus download of the weights that many times;
  sparsification/quantization families exist to shrink payload (not implemented here).
- Robustness: malicious or buggy clients can inject extreme vectors; anomaly detection on
  submitted update norms belongs in any real design review (literature exists freely but
  is not benchmarked in this lab).

## Where this lab puts Java

The aggregation math and the round bookkeeping are pure arithmetic; the snippets build a
two-dimension gradient toy where every average can be recomputed by hand. The writing
projects (per folder) then scale the bookkeeping sketch up to a mock service layout.
