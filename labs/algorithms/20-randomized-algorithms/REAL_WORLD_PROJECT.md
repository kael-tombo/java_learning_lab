# Real-World Project: Monte Carlo Harness
> Seeded pi estimation and Fermat testing with exact reproducibility checks.

## Problem
Randomized methods must be testable: fixed seeds make every run byte-reproducible.
The harness records reference outputs and fails on any drift.
## Inputs
- Seed, dart count, and estimator parameters from a config file.
- Reference outputs recorded from the first verified run.
- Fermat cases: 15 (caught), 561 (passes base 2 - documented blind spot).
## Steps
1. Estimate pi with dart-throwing under the configured seed and count.
2. Report estimate, absolute error vs 3.14159265, and darts used.
3. Run the Fermat base-2 test on 15 and 561 and record both verdicts.
4. Re-run twice more and assert byte-identical outputs (determinism gate).
5. Plot-data mode writes (darts, error) rows for 1k through 200k darts.
6. Fail the suite if any output differs from the recorded reference.
## Acceptance criteria
- Three consecutive runs are byte-identical on all outputs.
- 200k-dart seed-42 estimate lands within 0.1 of pi.
- Fermat reports composite for 15 and pass for 561 with the blind-spot note attached.
- Error column shrinks overall across the plot-data sweep.
- Unseeded mode is refused in test runs (only allowed in demo runs).
## Failure modes
- Seed 0 and negative seeds are accepted but logged (documented Java Random behavior).
- Dart counts above the cap are refused with the time reason.
- NaN or negative config values fail at parse time with the field named.
## Extensions
- Reservoir sampler with the inclusion-probability check on small streams.
- Randomized pivot statistics: recursion-depth histogram over seeded quicksort runs.
## How to demo
- Show the determinism gate passing across three runs.
- Show the error sweep table and the shrinking trend.
