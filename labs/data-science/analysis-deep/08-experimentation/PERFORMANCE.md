# Performance - Experimentation

## Complexities

- Readout (d/SE/z/p/CI): O(1) arithmetic plus one erf evaluation.
- SRM check: O(arms). Power table: O(rows). All sub-microsecond; the
  lab's programs are dominated by JVM startup, honestly stated.

## Scaling guidance

- Analysis never bottlenecks: even a billion-row log aggregates to four
  numbers (x_A, n_A, x_B, n_B) before statistics begin.
- Aggregation is the real pipeline: count per arm in one streaming
  pass, O(events) time, O(arms) memory. Sketch that, don't optimize z.
- Segmentation multiplies readouts, not cost: each slice reuses the
  same O(1) math - but each slice spends error budget (multiplicity).

## No invented benchmarks

No timings quoted; "runs instantly" claims are omitted because JVM
startup (~50-100ms in practice, unmeasured here) dominates and varies.
Time your own harness if it matters.

## Real cost driver

Traffic-time: the weeks a test occupies the experimentation slot.
Power planning (SampleSize pattern) is how that cost is controlled -
statistics here serve scheduling, not CPUs.

## Cost table

| Operation | Time | Memory |
|---|---|---|
| readout (d/SE/z/p/CI) | O(1) + 1 erf | O(1) |
| SRM check | O(arms) | O(1) |
| power table, R rows | O(R) | O(1) |
| aggregation to counts | O(events) | O(arms) |

## Measurement note

Time the aggregation pass (events/sec at your row width), never the
statistics. Report row counts with durations; naked seconds compare
nothing across traffic scales.
