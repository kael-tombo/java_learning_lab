# MLOps Orchestration - Internals

## Backoff schedule
- Delay for attempt n is min(cap, base * 2^n); the snippet yields 1, 2, 4, 8, 16, then capped 30 s.
- The cap bounds worst-case stall; jitter spreads retries so dependents are not hammered in sync.
- Retry only transient errors; validation failures fail fast instead.

## Lineage fingerprint
- Concatenate data version, code commit, and parameter string into one pointer.
- A deterministic fingerprint of that pointer identifies the run; identical inputs reproduce it.
- The snippet fingerprint 1047179432 demonstrates the rerun-equality check.

## Promotion gate
- Overall lift must clear its bar and every slice must clear its no-regression bar.
- The snippet passes overall (+0.025 vs +0.010 bar) but slice 2 fails, so promotion is false.
- One combined boolean prevents partial promotion of a model with a broken segment.

## Idempotence mechanics
- Key all writes by run id and partition so reruns overwrite rather than duplicate.
- Guard side effects with explicit promotion flags, never inside retried tasks.
- Record attempt counts and backoff actually used for postmortems.

## Total-wait arithmetic
- Six uncapped waits from base 1 s sum to 1+2+4+8+16+32 = 63 s of stall.
- A cap truncates terms above it; jitter replaces each term with a spread.
- Attempt limits multiply worst case: bound attempts and the cap bounds cost.

## Fingerprint equality
- The pointer concatenates data version, code commit, parameter string, pins.
- Deterministic hashing yields 1047179432 in the snippet across identical reruns.
- Any pointer change alters the fingerprint, naming the divergence source.

## Gate conjunction mechanics
- Overall lift compares candidate minus baseline against the minimum lift.
- Each slice compares its drop against the maximum allowed absolute drop.
- AND-composition means the snippet's passing overall (+0.025 vs +0.010)
  still blocks on slice 2: the veto is the design, not an accident.

## Retry classification
- Transient signatures (timeouts, dependency errors) retry on schedule.
- Deterministic signatures (schema violations, range failures) stop immediately.
- Misclassification costs both ways: wasted GPU hours or duplicate side effects.

## Queue arithmetic
- Shared-queue wait grows with backfill parallelism; separation removes the term.
- Cap backfill concurrency so replays proceed without starving cadence runs.
- Queue wait per lane is the fairness metric, reviewed after every incident.
