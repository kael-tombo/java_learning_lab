# Security Notes - Data Pipelines

## PII in flight and at rest

Pipelines copy sensitive fields everywhere (landing, staging, logs).
Minimize at ingestion (drop unneeded columns), mask in logs, encrypt
stores - each copy is breach surface, and pipelines multiply copies.

## Schema changes as injection surface

Renamed fields and type coercions can smuggle malformed values past
naive parsers (the string-amount that breaks sums). Strict typing,
unknown-column rejection, and range checks at the landing gate.

## Replay and backfill authorization

Reprocessing history rewrites served truth: require approval, pin code
versions, and diff before promotion. An unapproved backfill is a data
integrity incident wearing an engineering badge.

## Provenance and tampering

Run logs (code version, input range, counts) are the tamper-evidence
seal on numbers. Sign or append-only-store them; silent log edits void
auditability of every downstream decision.

## Code-level hygiene (JDK)

Validate keys non-null at Record construction; fail on empty batches
rather than serving stale state; ordered maps in output paths; cast
counts to double before rate math; no credentials in run logs.

## Replay as a weapon

Authorized-looking replays can rewrite served history (restated revenue,
erased incidents). Require multi-party approval for production replays,
pin versions, and keep immutable pre/post diffs - replay power needs
replay governance.

## Third-party source trust

External feeds arrive with their own keys, clocks, and definitions -
all attacker- or error-controlled. Quarantine-first ingestion, strict
schemas, and semantic checks treat every source as untrusted by default.
