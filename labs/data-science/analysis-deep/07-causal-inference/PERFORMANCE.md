# Performance - Causal Inference

## Complexities

- Stratified gaps, DiD, balance tables: O(n) single passes.
- Nearest-score matching (taught conceptually): O(n log n) with sorted
  scores; this lab's snippets use exact strata, O(cells).
- Sensitivity grids: O(grid * cells) - trivial at these sizes.

## Scaling guidance

- Causal work is assumption-bound, not compute-bound: ten clean strata
  beat a million rows with unmeasured confounding.
- With large registries, exact strata explode combinatorially; coarsen
  deliberately (age bands, not exact age) and show balance before/after.
- Bootstrap CIs around adjusted gaps cost O(B * n); B = 1000 is the
  conventional workhorse - state B, seed the RNG, report it.

## No invented benchmarks

No timings are quoted: on lab-sized tables everything is
sub-millisecond and any number would be theater. Profile only if a
real registry pipeline is slow, then report hardware with the numbers.

## Real cost driver

Human time dominates: drawing the confounding map and defending the
assumption dwarf computation. Budget review hours, not server hours.

## Cost table

| Operation | Time | Memory |
|---|---|---|
| stratum gaps, DiD | O(cells) | O(strata) |
| balance per covariate | O(n) | O(1) |
| sensitivity grid G | O(G * cells) | O(G) output |
| bootstrap B resamples | O(B * n) | O(n) |

## Measurement note

Timing these is theater at lab scale; time the data plumbing (registry
extracts, joins) instead, and report row counts with every duration so
rates (rows/sec) - not naked seconds - are comparable.
