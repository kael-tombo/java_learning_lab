# Mini Project: Seeded Pi
> Monte Carlo estimation with reproducibility as the graded property.

## Background
- Fixed seeds make randomized runs exactly reproducible for tests.
- Error shrinks like 1/sqrt(n); the sweep table shows it.
- Determinism gate: three runs must be byte-identical.
## Goal
Estimate pi under seed 42 and gate the suite on reproducibility.
Record the error sweep from 1k to 200k darts.
## Tasks
1. Implement dart-throwing pi estimation with a seed parameter.
2. Run 200k darts under seed 42 and record the estimate.
3. Run twice more and assert byte-identical outputs.
4. Sweep 1k, 10k, 100k, 200k darts writing (darts, error) rows.
5. Assert the 200k estimate is within 0.1 of pi.
6. Add the Fermat 15-vs-561 demo with the blind-spot note in output.
## Acceptance criteria
- Determinism gate passes across three runs.
- 200k estimate is within 0.1 of pi.
- Sweep table shows overall error shrinkage.
- Fermat demo prints both verdicts with the note attached.
- Unseeded runs are refused in test mode.
## Pitfalls
- new Random() per run while claiming reproducibility.
- Reporting one lucky estimate as the method's error.
- Sweeping without fixed seeds, making the trend irreproducible.
- Reading the blind-spot note as a bug instead of a documented limit.
## Stretch
- Reservoir sampler with inclusion checks on small streams.
- Repetition-count calculator from an error target with the inequality shown.
## Timebox
One afternoon session, roughly 2 hours with sweeps.
