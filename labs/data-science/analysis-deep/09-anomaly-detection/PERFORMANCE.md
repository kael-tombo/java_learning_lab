# Performance - Anomaly Detection

## Complexities

- Scoring n points with fitted center/spread: O(n) time, O(1) extra.
- Fitting (sort-based quartiles/median): O(n log n), the only
  super-linear step, run on schedule not per point.
- Sweep over G thresholds on L labels: O(G*L).
- Bayes/volume math: O(1).

## Scaling guidance

- Per-event scoring at stream rates: precompute center/spread, score in
  O(1) per event with primitive doubles - no allocation per point.
- History windows in the millions: sort-based fitting still fits in one
  pass of memory; beyond that, reservoir-sample the window and say so.
- Threshold sweeps parallelize trivially (streams over thresholds) but
  rarely need to - measure before threading.

## No invented benchmarks

No throughput or latency numbers are quoted: they depend on hardware,
event width, and JVM warmup. The complexities above plus your own JMH
run are the honest performance story.

## Real cost driver

Human triage minutes per flag dominate compute by orders of magnitude.
Every 0.1 of precision gained is on-call sleep saved - optimize the
false-positive rate before the code.

## Cost table

| Operation | Time | Memory |
|---|---|---|
| fit Window (sort) | O(n log n) | O(n) |
| score n points | O(n) | O(1) |
| sweep G x L labels | O(G*L) | O(G) table |
| Bayes + volumes | O(1) | O(1) |

## Measurement note

Benchmark scoring with production-width events after warmup; report
events/sec with n and event width. Fitting runs on schedule - time it
once per Window size and calendar accordingly, not per deploy.
