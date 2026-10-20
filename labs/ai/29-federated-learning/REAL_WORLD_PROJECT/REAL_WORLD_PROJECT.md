# Federated Learning — Real-World Project

**Goal**: a realistic-but-bounded coordination sketch for privacy-preserving analytics
across teams: what would a distributed model-tuning service look like in Java, and where
do the promises actually need footnotes?

## Scenario (self-contained, no real data ingested)

Four business units hold customer-behavior summary tables. A central "tuning" service
would like a jointly useful predictive model without tables leaving the units. Your
deliverable is (a) the orchestration skeleton and (b) a findings document about what this
cannot achieve by itself.

## Components

1. `ParticipantStub` interface: `submit(Weights w, RoundContext c)` and `capabilities()`;
   four stub implementations with fixed, hand-written update vectors (sizes differ).
2. `Coordinator`: round loop, participant selection by round-robin with 1 dropout per
   round, weighted aggregation, versioned theta, and a retry window.
3. `CompliancePanel`: ledger printing per round — vectors submitted (norm only, not
   contents), counts, and round version; the design rule: no raw table keys ever appear
   in the log (enforce by type: ledger sees only norms).
4. `ThreatNotes` (static utility): documentation-mode class describing where the naive
   protocol fails privacy expectations (inference from submitted update vectors, repeated
   queries reconstructing data patterns) — textual, examined by graders.

## Write-up (the main artifact, ~2 pages)

- What the aggregation arithmetic does and does not protect against (quote the norms
  table from one run; explain why visibility of *norms alone* still leaks rate-of-change
  signals across rounds).
- Which guarantees you would need before suggesting deployment to a real compliance
  review (differential-privacy-style noise privacy claims, secure aggregation for vector
  contents, contract law side) — described as open requirements with pointers in general
  terms, not implementations.
- A roll-out plan: two-week prototype cadence with what would be measured (per-unit
  contribution skew, round dropout rate, end-to-end round latency).

## Constraints

`javac --release 21`, one-file compile, seeded determinism; ASCII prints only; no git
commits, no real credentials, no network sockets — the stub pattern is deliberate.
