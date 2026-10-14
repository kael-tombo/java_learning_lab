# REAL_WORLD_PROJECT — Advanced Number Theory
> Composite-triage service for test-data generation: fast prime screening with stated-scope Miller-Rabin plus Pollard Rho factoring queue. Not a crypto module.

## System and inputs
- Request: (integer as decimal string, purpose tag: testdata/screening/education); anything tagged production-crypto is rejected with a pointer to the approved crypto library.
- Pipeline: trial division (primes to 1000), fixed-base Miller-Rabin {2,7,61} for 32-bit inputs, larger inputs get probabilistic rounds with the round count logged.
- Composite queue: Miller-Rabin composites eligible for Pollard Rho factoring with a per-job time budget.

## Design
- Verdict records carry (method, bases/rounds, timestamp, code version) so every PRIME/COMPOSITE is auditable.
- Scope banner on every response states the base set and range; out-of-scope inputs get probabilistic verdicts labeled as such.
- Factoring worker runs Rho with restart-on-d=n (new constant), bounded by budget, then reports partial/failed honestly.

## Metrics
- Screening throughput (verdicts/sec) by input size bucket.
- Rho success rate and median time-to-first-factor by digit count.
- Out-of-scope request rate (scope-policing signal) and rejection rate for production-crypto tags.
- Verdict reproducibility: nightly rerun of the reference list must match byte-identically.

## Failure modes
- Caller treats a screening verdict as cryptographic certainty: scope banner plus tag rejection; docs carry the non-crypto disclaimer.
- Rho stalls on prime powers: perfect-power precheck diverts to root extraction first.
- Oversized decimal input (10k digits): size guard rejects with the digit limit before allocating.
- Round-count misconfiguration on large inputs: minimum-rounds policy enforced in code, not docs.

## Rollout
1. Serve test-data generation only; nightly reference-list check gates deploys.
2. Open the factoring queue with budgets; dashboard success rate by digit count.
3. Quarterly review of base sets and round policy against published results.

## Acceptance criteria
1. Reference list (17/561/2047/7919/8051) verifies through the full service path with expected verdicts.
2. production-crypto tag is rejected with the approved-library pointer (test included).
3. 341 is reported COMPOSITE with factors 11x31, never PRIME.
4. Nightly rerun matches the checked-in reference output byte-identically.
5. Oversize input is rejected pre-allocation with the digit limit in the message.

## Cost and contract notes
- Screening priced per verdict by size bucket; factoring queue priced per minute with the budget cap enforced in the worker.
- Reference-list rerun is a deploy gate: mismatch blocks promotion, no overrides.
- Verdict records retained 90 days for audit; factoring artifacts (factor trees) retained with the job id.
- Contract: verdict responses embed (method, bases/rounds, code version); clients must log the scope banner, not strip it.
