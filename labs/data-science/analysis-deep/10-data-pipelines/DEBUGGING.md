# Debugging - Data Pipelines

## 1. Row counts doubled after rerun

Cause: blind append sink replayed. Fix: keyed merge (PipeIdem); verify
by replaying and asserting identical state - the exercise-1 assertion.

## 2. Nulls where values were expected

Cause: blank strings vs true nulls, or a renamed source column silently
mapping to nothing. Fix: distinguish isBlank from null in checks; fail
on unknown columns instead of ignoring them.

## 3. Schema change broke readers at midnight

Cause: breaking change deployed without versioning. Fix: CI compat gate
(subset + types); breaking edits ship as v2 with a dual-read window and
a dated reader-migration deadline.

## 4. Windows shifted after late data

Cause: arrival-time windows with late events, or no lateness policy.
Fix: declare event-time semantics, route lates per policy, document the
choice where the window is defined.

## 5. Non-deterministic replay output

Cause: wall-clock calls or hash-order iteration in transforms. Fix:
event time only, ordered maps, double-run diff assertion in the backfill
gate - determinism tested, not hoped.

## 6. Silent column drop from source

Cause: source renamed a field; pipeline selected known columns and
ignored the rest. Fix: strict mode - unknown/missing columns quarantine
the batch; schema diffs page before serving.

## 7. Backfill promoted bad history

Cause: promotion without diff tolerances. Fix: the six-line gate
(counts, key overlap, mismatch rate, checks, version pin, sign-off) -
missing lines block promotion mechanically.

## 8. Drift passes but dashboards look wrong

Symptom: trio green, metrics off. Cause: correct rows, wrong meaning -
source redefined a code (status 3 now means refunded, meant shipped).
Fix: semantic checks (value-distribution per code) alongside the trio;
version the codebook with the schema.
