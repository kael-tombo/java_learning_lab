# Federated Learning — Mini Project

**Goal**: a mini "server + 3 clients" federation simulator, fully deterministic and
readable in one Java file: rounds, weighted aggregation, dropout handling, norm screen.

## Protocol configuration (defaults; all overridable)

- Clients: 3 toy clients with fixed gradient tables — per client, 4 rounds of synthetic
  "local gradients" (any constant vector is fine; document they're synthetic).
- Server keeps a moving global vector `theta`; `lr = 0.1`; aggregation = data-count
  weighted mean of submitted local updates (canonical FedAvg).
- Rounds = 6; each round ALL clients are preselected, but client 2 skips rounds 3 and 4.

## Required behaviors

1. `Aggregator.weightedMean(submitted)` — must reject empty submissions and print a
   skip notice for a dropped round instead of averaging nothing silently.
2. `NormScreen`: any submitted vector whose norm exceeds `0.6` is scaled to that limit
   before entering the average; log the exact scale applied per client per round.
3. Snapshot after every round: `theta`, submitted-count, and skipped-client list.
4. A staleness guard: a client submitting on a round it previously skipped gets a
   `STALE-SUBMISSION-ACCEPTED` line only if it submits against the CURRENT theta — implement
   by versioning `theta` with a round counter and checking the client's ack.

## Deliverables and acceptance

- Single Java file, compiles clean under `javac --release 21`.
- Deterministic 6-round table in stdout (verbatim-captured): 12 snapshot lines minimum.
- Three-paragraph readout: one on the weighted-vs-count story (quote round-1 and round-6
  positions), one on the norm-screen's visible effect (which round is same with and
  without?), one on staleness hazards with the versioning as evidence.
- Propagation disclaimer: the "clients" are constants in memory; no network, no privacy
  guarantee is implied or tested.

## Stretch idea

Add per-client momentum aggregation (server EMA over submitted vectors with `m = 0.9`)
as a flag; compare 6-round trajectories against the plain average and quote the final
separation (L2 distance between the two final global vectors).
