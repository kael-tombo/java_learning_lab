# Model Training Pipelines — Internals

## Orchestrator mechanics
The runner stores per-stage state (pending, running, passed, failed)
and advances on pass events only. Retries re-execute a stage from its
versioned inputs; stages must be pure functions of those inputs so
retries converge to the same outputs.

## Dataset versioning
Ingest writes content-addressed snapshots: the version id derives from
a hash of the query plus source state. Identical sources yield
identical ids, which lets reruns skip ingest safely and lets audits
resolve "which data" unambiguously.

## Tracker storage
A relational table per run with columns for params (JSON), metrics
(JSON), code hash, data hash, seed, timestamps, and artifact pointer.
Queries like "all runs on dataset v3 with lr=0.01" are ordinary SQL —
the tracker's value is completeness of fields, not query cleverness.

## Registry mechanics
Models are blobs in immutable storage keyed by version; metadata rows
point at blobs plus lineage. Promotion is a pointer update (candidate
to production), never a blob edit. Garbage collection deletes blobs
with no references from deployed, audited, or recent-candidate sets.

## Idempotence requirements
Validate, transform, train, and evaluate must all be re-runnable with
identical results given identical inputs. Randomness is allowed only
through the recorded seed, which is part of the inputs.

## Promotion mechanics
A candidate becomes production through a recorded decision: threshold
comparison against the incumbent plus an approver identity. The
pointer update is atomic in the registry; serving resolves the pointer
at request time, so rollback is a second pointer update with its own
record. Demotion keeps history — the audit trail shows every version
that ever served, in order.
